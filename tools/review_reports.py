"""Local reviewer for the Qur'an, hadith and corrections reports.

Usage:
    python3 -I tools/review_reports.py
    python3 -I tools/review_reports.py --no-browser --port 8765

Where decisions are saved (so that re-running the checks does not lose them):
  corrections  an inline <!-- review: accepted|rejected --> mark in reports/volNN-corrections.md; a manual
               edit is stored as the changed lines only ("Review edit: ⟦old⟧ ⇒ ⟦new⟧"), never the whole page
  Qur'an       DIFFERS / DECIDED / KEPT ayat: <volume dir>/quran-decisions.tsv, read by mark_arabic.py
               (Accept = use the Qur'an words, Reject = keep as printed; run mark_arabic.py --write to apply);
               other entries: reports/volNN-review.tsv
  hadith       reports/volNN-review.tsv; the text starts as the book's own words (PLAN rule 14)
Nothing here edits page-notes/: applying an accepted correction or reverting a rejected one is a separate step.
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
REPORTS = ROOT / 'reports'
REPORT_FILES = {
    'corrections': 'vol{volume:02d}-corrections.md',
    'quran': 'vol{volume:02d}-quran-check.md',
    'hadith': 'vol{volume:02d}-hadith-check.md',
}
REVIEW = re.compile(r'\s*<!--\s*review:\s*(accepted|rejected)\s*-->')
QURAN_START = re.compile(r'^(DIFFERS|CITE|DECIDED|KEPT|QURAN|ARABIC)\s+p(\d+)\b(.*)$')
HADITH_START = re.compile(r'^- p(\d+):\s*(.*)$')
DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
BOOK_FILES = {
    'صحیح بخاری': 'bukhari', 'صحیح مسلم': 'muslim', 'سنن ابی داؤد': 'abudawud',
    'سنن ترمذی': 'tirmidhi', 'سنن نسائی': 'nasai', 'سنن ابن ماجہ': 'ibnmajah',
    'موطا مالک': 'malik', 'اربعین نووی': 'nawawi', 'احادیث قدسیہ': 'qudsi',
}


def review_status(text):
    match = REVIEW.search(text)
    return match.group(1) if match else 'unreviewed'


def clean_review(text):
    return REVIEW.sub('', text).strip()


def set_review(text, status):
    return clean_review(text) + f' <!-- review: {status} -->'


def display_text(text):
    return re.sub(r'<br\s*/?>', '\n', clean_review(text)).replace(r'\|', '|')


def stored_text(text):
    return text.replace('\r', '').replace('\n', '<br>')


def split_row(line):
    text = line.strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|') and not text.endswith(r'\|'):
        text = text[:-1]
    cells, current, escaped, in_ayah = [], [], False, False
    for char in text:
        if char == '﴿':
            in_ayah = True
        elif char == '﴾':
            in_ayah = False
        if char == '|' and not escaped and not in_ayah:
            cells.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
        if char == '\\' and not escaped:
            escaped = True
        else:
            escaped = False
    cells.append(''.join(current).strip())
    return cells


def join_row(cells):
    return '|' + '|'.join(f' {cell} ' if cell else ' ' for cell in cells) + '|'


def page_numbers(label, volume, printed_default=True, pdf_first=False):
    """(pdf, printed) from a report's page cell. Labels seen in the reports: "40", "p305 (PDF 306)",
    "169 (pr. 168)", "98 (97)", "97–98 (pr. 96–97)", "toc (PDF 14)". `pdf_first`: the column header
    names the PDF page first ("pdf page (printed)"), so "N (M)" is PDF N, printed M."""
    label = clean_review(label).translate(DIGITS)
    pdf_match = re.search(r'\bPDF\s*(?:p\.?\s*)?(\d+)', label, re.I)
    printed_match = re.search(r'\bpr\.\s*(?:p\.?\s*)?(\d+)', label, re.I)
    first_match = re.search(r'\d+', label)
    first = int(first_match.group()) if first_match else None
    pdf = int(pdf_match.group(1)) if pdf_match else None
    printed = int(printed_match.group(1)) if printed_match else None
    bare_pair = re.match(r'^\s*(\d+)(?:[–-]\d+)?\s*\((\d+)(?:[–-]\d+)?\)', label)
    if not pdf and not printed and bare_pair and pdf_first:
        return int(bare_pair.group(1)), int(bare_pair.group(2))
    if not pdf and not printed and first and pdf_first:
        return first, first - 1
    if pdf:
        printed = printed or (first if first != pdf else pdf - 1)
    elif printed:
        pdf = first
    elif first:
        toc_printed = re.search(r'\b(?:toc|contents)\b.*\bp\.?\s*\d+', label, re.I)
        if printed_default or toc_printed:
            printed, pdf = first, first + 1
        else:
            pdf, printed = first, first - 1
    return pdf, printed


def report_path(reports, volume, report):
    if report not in REPORT_FILES:
        raise ValueError('Unknown report type')
    return reports / REPORT_FILES[report].format(volume=volume)


def read_lines(path):
    text = path.read_text(encoding='utf-8')
    return text.splitlines(), text.endswith('\n')


def write_lines(path, lines, final_newline):
    text = '\n'.join(lines) + ('\n' if final_newline else '')
    fd, temporary = tempfile.mkstemp(prefix='.review-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# The corrections tables changed their column names over the volumes:
#   | Page | Kind | Book had | Applied | How decided |        (Vols 2–9, 15)
#   | Page | Kind | Printed | Applied | Note |                (Vols 10–11)
#   | page (pdf/printed) | book had | applied | why |         (Vols 12–14, 16)
#   | pdf page (printed) | kind | printed | written / decision | note |   (Vol 22 on)
#   | PDF page (printed) | kind | as printed | changed to | note |        (Vol 23)
ORIGINAL_COLUMNS = ('book had', 'printed', 'as printed')
APPLIED_COLUMNS = ('applied', 'written / decision', 'changed to')


def table_columns(headers, cells):
    """Header names fitted to a row (some rows omit or add the kind column), plus the page,
    original and applied column names; None when the row does not fit."""
    effective = list(headers)
    if len(cells) == len(effective) - 1 and 'kind' in effective:
        effective.remove('kind')
    elif len(cells) == len(effective) + 1 and 'kind' not in effective:
        effective.insert(1, 'kind')
    if len(cells) != len(effective):
        return None
    page_key = next((key for key in effective if key.startswith(('page', 'pdf page'))), None)
    original_key = next((key for key in effective if key in ORIGINAL_COLUMNS), None)
    applied_key = next((key for key in effective if key in APPLIED_COLUMNS), None)
    if not page_key or not original_key or not applied_key:
        return None
    return effective, page_key, original_key, applied_key


def base_item(volume, report, line, category, page_label, original, corrected, note,
              pdf=None, printed=None):
    return {
        'id': f'{report}:{line + 1}', 'volume': volume, 'report': report, 'line': line,
        'category': category, 'page_label': page_label, 'original': original,
        'corrected': corrected, 'note': note, 'pdf_page': pdf, 'printed_page': printed,
        'status': 'unreviewed',
    }


class VolumeText:
    def __init__(self, volume):
        self.volume = volume
        self.pages = None
        self.toc = None
        matches = list(ROOT.glob(f'Vol {volume:02d} */page-notes'))
        if volume == 1:
            matches += list(ROOT.glob('Index pilot - 01 */page-notes'))
        self.notes_dir = matches[0] if matches else None

    def load(self):
        if self.pages is not None:
            return
        self.pages = {}
        self.toc = ''
        if not self.notes_dir:
            return
        toc_path = self.notes_dir.parent / 'toc.tsv'
        if toc_path.exists():
            self.toc = toc_path.read_text(encoding='utf-8').strip()
        for path in self.notes_dir.glob('*.txt'):
            page = None
            content = []
            in_terms = False
            def store():
                if page is not None:
                    self.pages[page] = '\n'.join(content).strip()
            for line in path.read_text(encoding='utf-8').splitlines():
                marker = re.match(r'^===\s+(\d+)(?:\s*\|\s*(\d+))?', line)
                if marker:
                    store()
                    page = int(marker.group(2) or marker.group(1))
                    content = []
                    in_terms = False
                elif page is not None:
                    if line.strip() == '## terms':
                        in_terms = True
                    elif line.startswith('#'):
                        in_terms = False
                        content.append(line)
                    elif not in_terms:
                        content.append(line)
            store()

    def correction(self, printed, before, applied):
        from arabic import norm
        self.load()
        matched = printed
        if printed is None:
            return (*self.toc_correction(before, applied), None)
        page = self.pages.get(printed, '')
        old_fragments = replacement_fragments(before)
        new_fragments = replacement_fragments(applied)
        def has_fragment(candidate, fragment):
            fragment = clean_fragment(fragment)
            return bool(fragment) and (fragment in candidate or norm(fragment) in norm(candidate))
        if not text_unchanged_report(applied) and old_fragments and new_fragments and not any(has_fragment(page, f) for f in old_fragments + new_fragments):
            for adjacent in (printed - 1, printed + 1):
                candidate = self.pages.get(adjacent, '')
                if any(has_fragment(candidate, f) for f in new_fragments + old_fragments):
                    page = candidate
                    matched = adjacent
                    break
        if not page:
            return '', '', matched
        original = corrected = page
        mismatched_quotation = not quoted_text(before) and quoted_text(applied) and '﴿' not in applied
        if not mismatched_quotation and not text_unchanged_report(applied):
            for old, new in zip(old_fragments, new_fragments):
                original = replace_reported_text(original, old, new)
        dropped = re.search(r'stray\s+["“](.*?)["”]\s+dropped', applied, re.I)
        if dropped:
            for old in old_fragments:
                if old in page:
                    corrected = page.replace(old, old.replace(' ' + dropped.group(1), ''), 1)
                    original = page
                    break
        if re.search(r'\b(?:given|kept) once\b', applied, re.I):
            for old in old_fragments:
                if old in page:
                    original = page.replace(old, old + '\n' + old, 1)
                    break
        if original == corrected and not text_unchanged_report(applied):
            for old, new in zip(old_fragments, new_fragments):
                if old in corrected:
                    corrected = replace_reported_text(corrected, new, old)
        if "editor's note" in applied:
            original = re.sub(r'\n*\[حاشیہ:\s*\(از مرتب\).*?\]', '', original, flags=re.S)
        return original, corrected, matched

    def toc_correction(self, before, applied):
        self.load()
        if not self.toc:
            return '', ''
        rows = self.toc.splitlines()
        if re.search(r'headings.*spelled differently', before, re.I):
            summary = re.search(r'\(([^()]*)\)', before)
            pairs = re.findall(r'([^/،,]+)/([^/،,]+)', summary.group(1)) if summary else []
            matching = [row for row in rows if any(new.strip() in row for _, new in pairs)]
            corrected = '\n'.join(matching)
            original = corrected
            for old, new in pairs:
                original = original.replace(new.strip(), old.strip())
            return original, corrected
        if re.search(r'the headings are printed on pp\.', before, re.I):
            summary = re.search(r'gives\s+(.*?);\s*the headings', before, re.I)
            entries = re.findall(r'([^,]+?)\s+(\d+)(?:,|$)', summary.group(1)) if summary else []
            matching = [row for row in rows if any(title.strip() in row for title, _ in entries)]
            corrected = '\n'.join(matching)
            original = corrected
            for title, number in entries:
                original = re.sub(r'(^\t*.*' + re.escape(title.strip()) + r'.*\t)\d+$',
                                  lambda match: match.group(1) + number, original, flags=re.M)
            return original, corrected
        quotes = quoted_text(applied) + quoted_text(before)
        titles = [re.sub(r'\s+\d+$', '', clean_fragment(q)) for q in quotes]
        matching = [row for row in rows if any(title and title in row for title in titles)]
        if not matching:
            numbers = [int(n) for n in re.findall(r'\d+', applied.translate(DIGITS))]
            matching = [row for row in rows if numbers and row.rsplit('\t', 1)[-1] == str(numbers[-1])]
        corrected = '\n'.join(matching) if matching else self.toc
        original = corrected
        for old, new in zip(quoted_text(before), quoted_text(applied)):
            original = replace_reported_text(original, old, new)
        old_numbers = re.findall(r'\d+', before.translate(DIGITS))
        if old_numbers and len(matching) == 1:
            original = re.sub(r'\t\d+$', '\t' + old_numbers[0], original)
        if re.search(r'\badded\b', applied, re.I) and matching:
            original = ''
        elif re.search(r'\brow removed\b', applied, re.I):
            title = clean_fragment(quoted_text(before)[0]) if quoted_text(before) else before
            page = re.search(r'\d+$', title)
            number = page.group() if page else (old_numbers[-1] if old_numbers else '')
            title = re.sub(r'\s+\d+$', '', title)
            sermon = re.search(r'\bunder\s+(.+)$', before)
            original = '\t'.join([sermon.group(1) if sermon else '', title, number])
            corrected = ''
        return original, corrected


def quoted_text(text):
    values = re.findall(r'«(.*?)»', text, re.S)
    values += re.findall(r'["“](.*?)["”]', text, re.S)
    return [value.strip() for value in values if value.strip()]


def text_unchanged_report(text):
    return re.search(r'\b(?:kept|indexed|marked|identified|recorded)\b', text, re.I)


def replacement_fragments(text):
    ornate = re.findall(r'﴿(.*?)﴾', text, re.S)
    literal = [re.sub(r'^\s*\d+:\d+(?:-\d+)?\s*', '', value).strip() for value in ornate]
    literal = [value for value in literal if value]
    if literal:
        return literal
    quoted = quoted_text(text)
    if quoted:
        if re.search(r'\bprinted\b', text, re.I) and len(quoted) > 1:
            return [quoted[-1]]
        return quoted
    value = re.sub(r'﴿.*?﴾', '', text, flags=re.S)
    value = re.split(r"\s*\+\s*editor's note\b", value, maxsplit=1, flags=re.I)[0]
    value = re.sub(r'\s*\(for\s+[^)]*\)\s*$', '', value, flags=re.I).strip()
    return [value] if value else []


def clean_fragment(text):
    return text.strip().strip('…. ').strip()


def replace_reported_text(page, before, after):
    from arabic import norm
    before, after = before.strip(), after.strip()
    if '…' in before and '…' in after:
        for old_part, new_part in zip(before.split('…'), after.split('…')):
            if old_part.strip() and new_part.strip():
                page = replace_reported_text(page, old_part, new_part)
        return page
    before, after = clean_fragment(before), clean_fragment(after)
    if not before or not after or before == after:
        return page
    words = list(re.finditer(r'\S+', page))
    def word_starts(word):
        values = [word.start()]
        if '|' in word.group():
            values.append(word.start() + word.group().index('|') + 1)
        return values
    start = page.find(after)
    end = start + len(after) if start >= 0 else None
    if start < 0 and '…' in after:
        parts = [clean_fragment(part) for part in after.split('…') if clean_fragment(part)]
        match = re.search('.*?'.join(map(re.escape, parts)), page, re.S)
        if match:
            start, end = match.span()
    if start < 0:
        size = len(after.split())
        target = norm(after)
        for index in range(len(words) - size + 1):
            candidate_end = words[index + size - 1].end()
            for candidate_start in word_starts(words[index]):
                candidate = page[candidate_start:candidate_end]
                if norm(candidate) == target:
                    start, end = candidate_start, candidate_end
                    break
            if start >= 0:
                break
    if start < 0:
        target = norm(before.replace('…', ' '))
        size = len(before.split())
        best = None
        for length in range(max(1, size - 1), size + 2):
            for index in range(len(words) - length + 1):
                candidate_end = words[index + length - 1].end()
                for candidate_start in word_starts(words[index]):
                    candidate = page[candidate_start:candidate_end]
                    score = difflib.SequenceMatcher(None, target, norm(candidate), autojunk=False).ratio()
                    if best is None or score > best[0]:
                        best = (score, candidate_start, candidate_end)
        if best and best[0] >= 0.65:
            return page[:best[1]] + before + page[best[2]:]
        return page
    before_words = before.split()
    best = None
    for size in range(max(1, len(before_words) - 1), len(before_words) + 2):
        for index, word in enumerate(words):
            if index + size > len(words) or words[index + size - 1].end() < end:
                continue
            candidate_end = words[index + size - 1].end()
            for candidate_start in word_starts(word):
                if candidate_start > start:
                    continue
                candidate = page[candidate_start:candidate_end]
                score = difflib.SequenceMatcher(None, norm(before), norm(candidate), autojunk=False).ratio()
                if best is None or score > best[0]:
                    best = (score, candidate_start, candidate_end)
    if best and best[0] >= 0.65:
        return page[:best[1]] + before + page[best[2]:]
    return page[:start] + before + page[end:]


EDIT = re.compile(r'<br>\s*Review edit:\s*⟦(.*?)⟧\s*⇒\s*⟦(.*?)⟧', re.S)
OLD_EDIT = re.compile(r'<br>\s*Review edit:.*?(?=<br>\s*Review edit:|\s*<!--\s*review:|$)', re.S)


def review_edits(cell):
    """(old, new) line blocks saved by the reviewer in an applied cell."""
    return [(display_text(old), display_text(new)) for old, new in EDIT.findall(cell)]


def strip_review_edits(cell):
    return OLD_EDIT.sub('', cell).strip()


def apply_edits(text, edits):
    """Apply saved edits to the page text; returns the text and how many edits no longer apply."""
    missed = 0
    for old, new in edits:
        if old and old in text:
            text = text.replace(old, new, 1)
        else:
            missed += 1
    return text, missed


def same_text(a, b):
    """Equal apart from trailing spaces and line endings (a browser's innerText can differ in those)."""
    lines = lambda s: [line.rstrip() for line in s.replace('\r', '').strip('\n').split('\n')]
    return lines(a) == lines(b)


def line_edits(before, after):
    """Only the changed lines, each as (old block, new block); an insertion carries a neighbouring line
    so that it can be placed again. The whole page is never stored in the report."""
    a = before.replace('\r', '').split('\n')
    b = after.replace('\r', '').strip('\n').split('\n')
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        old, new = a[i1:i2], b[j1:j2]
        if not old:                       # pure insertion: anchor on the line before (or after)
            if i1 > 0:
                old, new = [a[i1 - 1]], [a[i1 - 1]] + new
            elif i2 < len(a):
                old, new = [a[i2]], new + [a[i2]]
        if old:
            out.append(('\n'.join(old), '\n'.join(new)))
    return out


def parse_corrections(path, volume, text=None):
    lines, _ = read_lines(path)
    items = []
    text = text or VolumeText(volume)
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith('|') or i + 1 >= len(lines) or not re.match(r'^\s*\|?\s*:?-+', lines[i + 1]):
            i += 1
            continue
        headers = [cell.strip().lower() for cell in split_row(lines[i])]
        i += 2
        while i < len(lines) and lines[i].lstrip().startswith('|'):
            cells = split_row(lines[i])
            if all(re.fullmatch(r':?-+:?', cell.replace(' ', '')) for cell in cells):
                i += 1
                continue
            columns = table_columns(headers, cells)
            if not columns:
                i += 1
                continue
            effective, page_key, original_key, applied_key = columns
            values = dict(zip(effective, cells))
            page_label = display_text(values[page_key])
            edits = review_edits(values[applied_key])
            applied = display_text(strip_review_edits(values[applied_key]))
            original_report = display_text(values[original_key])
            cross_volume = re.match(r'^Vol\s+(\d+)\s+p\.?\s*(\d+)$', page_label, re.I)
            pdf_volume = int(cross_volume.group(1)) if cross_volume else volume
            if cross_volume:
                printed = int(cross_volume.group(2))
                pdf = printed + 1
                source_text = VolumeText(pdf_volume)
            else:
                pdf, printed = page_numbers(page_label, volume, printed_default=volume < 10,
                                            pdf_first=page_key.startswith('pdf') or 'pdf,' in page_key or 'pdf/' in page_key)
                source_text = text
            notes = [f'Book had: {original_report}', f'Applied: {applied}']
            for key, value in values.items():
                if key not in (page_key, original_key, applied_key) and display_text(value):
                    notes.append(f'{key.title()}: {display_text(value)}')
            if pdf is None and re.match(r'^(?:toc|contents|فہرست)', page_label, re.I):
                for value in (applied, original_report, '\n'.join(notes)):
                    numbers = [int(n) for n in re.findall(r'\d+', value.translate(DIGITS))]
                    numbers = [n for n in numbers if 1 <= n <= 700]
                    if numbers:
                        printed, pdf = numbers[-1], numbers[-1] + 1
                        break
            is_toc = re.match(r'^(?:toc|contents|فہرست)', page_label, re.I) or display_text(values.get('kind', '')).lower() == 'toc'
            original, corrected, matched = source_text.correction(None if is_toc else printed, original_report, applied)
            if not is_toc and matched is not None:
                printed = matched
                pdf = printed + 1
            base = corrected
            corrected, unapplied = apply_edits(corrected, edits)
            if unapplied:
                notes.append(f'{unapplied} saved review edit(s) no longer match the page text.')
            if not corrected:
                notes.append('No transcribed page text was found for this report row.')
            item = base_item(
                volume, 'corrections', i, display_text(values.get('kind', 'correction')),
                page_label, original, corrected, '\n'.join(notes), pdf, printed,
            )
            item['pdf_volume'] = pdf_volume
            item['base'] = base
            item['status'] = review_status(lines[i])
            items.append(item)
            i += 1
    return items


def continuation(block, label):
    prefix = re.compile(r'^\s+' + re.escape(label) + r':\s*(.*)$')
    for line in block:
        match = prefix.match(line)
        if match:
            return display_text(match.group(1))
    return None


def best_window(query_text, reference_text):
    """The run of words in `reference_text` closest to `query_text` (letter skeletons compared), as printed
    in the reference; '' when nothing is close."""
    from arabic import norm
    reference_words = reference_text.split()
    query = norm(query_text).split()
    reference = [norm(word) for word in reference_words]
    if not query or not reference:
        return ''
    positions = {}
    for i in range(len(reference) - 2):
        positions.setdefault(tuple(reference[i:i + 3]), set()).add(i)
    starts = set()
    for j in range(len(query) - 2):
        for i in positions.get(tuple(query[j:j + 3]), ()):
            starts.add(i - j)
    if not starts:
        starts = set(range(len(reference)))
    best_score, best = 0, ''
    for start in starts:
        for offset in (-1, 0, 1):
            begin = max(0, start + offset)
            for length in (len(query) - 1, len(query), len(query) + 1):
                if length < 1:
                    continue
                score = difflib.SequenceMatcher(None, query, reference[begin:begin + length], autojunk=False).ratio()
                if score > best_score:
                    best_score, best = score, ' '.join(reference_words[begin:begin + length])
    return best


# ---------------------------------------------------------------- decisions that survive report reruns
# The Qur'an and hadith reports are regenerated by mark_arabic.py / check_hadith.py, so a mark written
# into them would be lost. Owner decisions on DIFFERS ayat go where mark_arabic.py reads them
# (<volume dir>/quran-decisions.tsv, PLAN rule); every other review of these two reports goes to
# reports/volNN-review.tsv, keyed by report, printed page and the letter skeleton of the book's words.

REVIEW_HEADER = ('# Owner review of the Qur\'an and hadith check reports (written by tools/review_reports.py).\n'
                 '# report<TAB>printed page<TAB>skeleton of the book\'s words<TAB>accepted|rejected<TAB>edited text\n')
DECISIONS_HEADER = ("# Owner's decisions on ayat where the book's wording differs from the Qur'an (read by tools/mark_arabic.py).\n"
                    "# page<TAB>book's words<TAB>keep | <surah:ayah><TAB>Qur'an words to put in their place\n")
QURAN_DECISION_KINDS = ('DIFFERS', 'DECIDED', 'KEPT')


def skeleton(text):
    from arabic import norm
    return norm(display_text(text))


def tsv_rows(path):
    if not path.exists():
        return []
    return [line.split('\t') for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.startswith('#')]


def tsv_replace(path, header, matches, row):
    """Drop the rows for which matches(row) is true, append `row` and write atomically."""
    if path.exists():
        lines = path.read_text(encoding='utf-8').splitlines()
    else:
        lines = header.rstrip('\n').split('\n')
    kept = [line for line in lines if not line.strip() or line.startswith('#') or not matches(line.split('\t'))]
    kept.append('\t'.join(cell.replace('\t', ' ').replace('\n', ' ') for cell in row))
    write_lines(path, kept, True)


def volume_dir(volume):
    notes = VolumeText(volume).notes_dir
    if not notes:
        raise ValueError(f'No folder found for volume {volume}')
    return notes.parent


def review_file(reports, volume):
    return reports / f'vol{volume:02d}-review.tsv'


def saved_reviews(reports, volume, report):
    out = {}
    for row in tsv_rows(review_file(reports, volume)):
        if len(row) >= 4 and row[0] == report and row[1].isdigit():
            out[(int(row[1]), row[2])] = (row[3], row[4] if len(row) > 4 else '')
    return out


def saved_decisions(volume):
    from arabic import norm
    out = {}
    try:
        path = volume_dir(volume) / 'quran-decisions.tsv'
    except ValueError:
        return out
    for row in tsv_rows(path):
        if len(row) >= 3 and row[0].strip().isdigit():
            out[(int(row[0]), norm(row[1]))] = ('keep',) if row[2] == 'keep' else (row[2], row[3] if len(row) > 3 else '')
    return out


def parse_quran(path, volume, reports):
    lines, _ = read_lines(path)
    reviews = saved_reviews(reports, volume, 'quran')
    decisions = saved_decisions(volume)
    items = []
    i = 0
    while i < len(lines):
        match = QURAN_START.match(clean_review(lines[i]))
        if not match:
            i += 1
            continue
        kind, page, body = match.group(1), int(match.group(2)), match.group(3).strip()
        end = record_end(lines, i, QURAN_START)
        block = lines[i:end]
        note = body
        original = corrected = ''
        ref = None
        alternatives = []
        if kind == 'DIFFERS':
            original = continuation(block, 'book') or ''
            for line in block:
                alt = re.match(r'^\s+alt \d+:\s+(\S+)\s+\[([^]]+)\]\s*(.*)$', line)
                if alt:
                    alternatives.append({'ref': alt.group(1), 'score': alt.group(2), 'text': alt.group(3).strip(),
                                         'suggest': best_window(original, alt.group(3)) or alt.group(3).strip()})
            if alternatives:
                ref, corrected = alternatives[0]['ref'], alternatives[0]['suggest']
            else:
                corrected = original
            note = '' if alternatives else body
        elif kind == 'CITE':
            text = continuation(block, 'text') or ''
            reference = re.search(r'the words are ([^,]+)', body)
            citation = re.search(r'book cites (.*?\(\d+:\d+\))', body)
            original = f'Book citation: {citation.group(1) if citation else body}\n\n{text}'
            corrected = f'Correct citation: {reference.group(1) if reference else ""}\n\n{text}'
        elif kind == 'DECIDED':
            head, _, content = body.partition('(owner):')
            ref = head.strip() or None
            original, _, corrected = content.strip().partition(' → ')
            corrected = display_text(corrected)
            note = head.strip()
        elif kind == 'QURAN':
            original = continuation(block, 'old') or ''
            corrected = continuation(block, 'new') or ''
        else:
            original = re.sub(r'^\(owner: keep as printed\)\s*', '', body)
            corrected = original
        status = 'unreviewed'
        help_text = ''
        if kind in QURAN_DECISION_KINDS:
            from arabic import norm
            help_text = ('Accept: put the Qur\'an words in the lower box in place of the book\'s words '
                         '(“Use this” picks another ayah). Reject: keep the book\'s words as printed. '
                         'Saved to the volume\'s quran-decisions.tsv; run tools/mark_arabic.py --write to apply.')
            decision = decisions.get((page, norm(original)))
            if decision:
                if decision[0] == 'keep':
                    status = 'rejected'
                else:
                    status, ref, corrected = 'accepted', decision[0], decision[1] or corrected
                said = 'keep as printed' if decision[0] == 'keep' else f'use {decision[0]}'
                help_text += (f'\nAlready decided earlier ({said}), recorded in quran-decisions.tsv.')
                if kind == 'DIFFERS':
                    help_text += (' This report was generated before that decision, so it still lists the ayah; '
                                  'it will drop out when the Qur\'an check is run again.')
        else:
            saved = reviews.get((page, skeleton(original)))
            if saved:
                status = saved[0]
                corrected = saved[1] or corrected
        item = base_item(volume, 'quran', i, kind, f'p{page}', original, corrected, note,
                         pdf=page + 1, printed=page)
        item['ref'] = ref
        item['alternatives'] = alternatives
        item['help'] = help_text
        item['arabic'] = True
        item['status'] = status
        items.append(item)
        i = end
    return items


class HadithReferences:
    def __init__(self):
        self.cache = {}

    def text(self, source):
        """The collection's text of the hadith a report line names ("صحیح بخاری 3445 (0.92); …")."""
        match = re.match(r'^(.*?)\s+(\d+)\s+\([0-9.]+\)', source)
        book = BOOK_FILES.get(match.group(1)) if match else None
        if not book:
            return ''
        if book not in self.cache:
            path = ROOT / 'reference' / f'ara-{book}.json'
            if not path.exists():
                return ''
            self.cache[book] = json.loads(path.read_text(encoding='utf-8'))['hadiths']
        record = next((row for row in self.cache[book] if str(row.get('hadithnumber')) == match.group(2)), None)
        return record['text'] if record else ''


def parse_hadith(path, volume, references, reports):
    """The right pane starts as the book's own words (PLAN rule 14: the book's wording stays as printed);
    the collection's nearest wording is shown in the details only, for checking a reading error."""
    lines, _ = read_lines(path)
    reviews = saved_reviews(reports, volume, 'hadith')
    items = []
    category = ''
    i = 0
    while i < len(lines):
        heading = re.match(r'^##\s+(differs|loose|match|not found)\s*$', lines[i])
        if heading:
            category = heading.group(1)
            i += 1
            continue
        match = HADITH_START.match(clean_review(lines[i]))
        if not match or not category:
            i += 1
            continue
        page, original = int(match.group(1)), match.group(2).strip()
        end = record_end(lines, i, HADITH_START)
        source = ''
        for line in lines[i + 1:end]:
            nested = re.match(r'^\s+-\s*(.*)$', line)
            if nested and not source:
                source = clean_review(nested.group(1).strip())
        note = source
        nearest = best_window(original, references.text(source)) if category == 'differs' else ''
        corrected, status = original, 'unreviewed'
        saved = reviews.get((page, skeleton(original)))
        if saved:
            status = saved[0]
            corrected = saved[1] or original
        item = base_item(volume, 'hadith', i, category, f'p{page}', original, corrected, note,
                         pdf=page + 1, printed=page)
        item['help'] = ('Accept: the lower box is what the book prints (edit it only to fix a reading error). '
                        'Reject: the passage needs another look.')
        item['compare'] = {'label': 'Collection wording, for comparison only (the book\'s wording stays):',
                           'text': nearest} if nearest else None
        item['arabic'] = True
        item['status'] = status
        items.append(item)
        i = end
    return items


def record_end(lines, start, pattern):
    end = start + 1
    while end < len(lines) and not pattern.match(clean_review(lines[end])) and not lines[end].startswith('## '):
        end += 1
    return end


def save_corrections(lines, start, status, edited, item):
    if not lines[start].lstrip().startswith('|'):
        raise ValueError('The report changed; reload before reviewing')
    cells = split_row(lines[start])
    headers = None
    for i in range(start - 1, -1, -1):
        if re.match(r'^\s*\|?\s*:?-+', lines[i]) and i > 0:
            headers = [cell.strip().lower() for cell in split_row(lines[i - 1])]
            break
    if not headers:
        raise ValueError('Could not find the table header')
    columns = table_columns(headers, cells)
    if not columns:
        raise ValueError('Could not identify the applied column')
    effective, _, _, applied_key = columns
    applied = effective.index(applied_key)
    value = cells[applied]
    if not same_text(edited, item['corrected']):
        # store only the changed lines, measured from the page text before any review edit
        value = strip_review_edits(value)
        for old, new in line_edits(item['base'], edited):
            value += '<br>Review edit: ⟦' + stored_text(old).replace('|', r'\|') + '⟧ ⇒ ⟦' + \
                     stored_text(new).replace('|', r'\|') + '⟧'
    cells[applied] = set_review(value, status)
    lines[start] = join_row(cells)


class ReportStore:
    def __init__(self, reports):
        self.reports = reports
        self.references = HadithReferences()
        self.texts = {}
        self.quran = None
        self.lock = threading.RLock()   # review() reloads items while holding it

    def volumes(self):
        volumes = {}
        for path in self.reports.glob('vol*.md'):
            match = re.match(r'vol(\d+)-(corrections|quran-check|hadith-check)\.md$', path.name)
            if not match:
                continue
            volume = int(match.group(1))
            report = {'corrections': 'corrections', 'quran-check': 'quran', 'hadith-check': 'hadith'}[match.group(2)]
            volumes.setdefault(volume, []).append(report)
        return [{'volume': volume, 'reports': sorted(volumes[volume])} for volume in sorted(volumes)]

    def items(self, volume, report):
        path = report_path(self.reports, volume, report)
        if not path.exists():
            return []
        if report == 'corrections':
            with self.lock:
                text = self.texts.setdefault(volume, VolumeText(volume))
                text.load()
            return parse_corrections(path, volume, text)
        if report == 'quran':
            return parse_quran(path, volume, self.reports)
        return parse_hadith(path, volume, self.references, self.reports)

    def item(self, volume, report, line):
        found = next((item for item in self.items(volume, report) if item['line'] == line), None)
        if not found:
            raise ValueError('This entry is no longer in the report (it was edited or regenerated); reload the page')
        return found

    def review(self, volume, report, line, status, edited, ref=None):
        if status not in ('accepted', 'rejected'):
            raise ValueError('Status must be accepted or rejected')
        with self.lock:
            item = self.item(volume, report, line)
            if report == 'corrections':
                path = report_path(self.reports, volume, report)
                lines, final_newline = read_lines(path)
                save_corrections(lines, line, status, edited, item)
                write_lines(path, lines, final_newline)
            elif report == 'quran' and item['category'] in QURAN_DECISION_KINDS:
                self.save_decision(volume, item, status, edited, ref)
            else:
                edit = '' if same_text(edited, item['corrected']) and item['status'] == 'unreviewed' else edited
                key = skeleton(item['original'])
                tsv_replace(review_file(self.reports, volume), REVIEW_HEADER,
                            lambda row: row[:3] == [report, str(item['printed_page']), key],
                            [report, str(item['printed_page']), key, status, stored_text(edit)])
        return self.item(volume, report, line)

    def save_decision(self, volume, item, status, edited, ref=None):
        from arabic import Quran, norm
        page, book = item['printed_page'], item['original']
        if status == 'rejected':
            row = [str(page), book, 'keep']
        else:
            choices = {item.get('ref')} | {alt['ref'] for alt in item.get('alternatives', [])}
            ref = ref or item.get('ref')
            if ref not in choices:
                raise ValueError(f'Unknown reference {ref}')
            if not ref:
                raise ValueError('No Qur\'an reference to replace this with; reject it or edit the report')
            if self.quran is None:
                self.quran = Quran()
            words = display_text(edited).replace('\n', ' ').strip()
            try:
                self.quran.phrase(ref, words)
            except (ValueError, AttributeError):
                raise ValueError(f'The words in the lower box are not found in {ref}; '
                                 'edit them to words of that ayah') from None
            row = [str(page), book, ref, words]
        tsv_replace(volume_dir(volume) / 'quran-decisions.tsv', DECISIONS_HEADER,
                    lambda r: r[0].strip() == str(page) and norm(r[1]) == norm(book), row)


PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Scheherazade+New:wght@400;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<title>Report review</title>
<style>
:root{--bg:#f3f5f4;--paper:#fff;--ink:#1d2925;--muted:#65736d;--line:#d6ded9;--accent:#176b57;--red:#a43b3b;--redbg:#fbe9e7;--green:#176b46;--greenbg:#e3f4e9}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{background:var(--paper);border-bottom:1px solid var(--line);padding:12px 18px}
.top,.controls,.itembar{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.top{justify-content:space-between;margin-bottom:10px}h1{font-size:20px;margin:0}.counts{color:var(--muted)}
select,button{font:inherit;border:1px solid var(--line);border-radius:6px;background:#fff;color:inherit;padding:7px 11px}button{cursor:pointer;font-weight:600}button:hover:not(:disabled){border-color:var(--accent)}button:disabled{opacity:.45;cursor:default}
.accept{background:var(--green);color:#fff;border-color:var(--green)}.reject{background:var(--red);color:#fff;border-color:var(--red)}.reset{margin-left:auto;font-weight:400}
.workspace{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;padding:12px;height:calc(100vh - 122px);min-height:520px}.left{display:flex;flex-direction:column;gap:10px;min-height:0}.itembar{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:9px 12px}.itemtitle{font-weight:700}.badge{border-radius:20px;padding:2px 9px;font-size:12px;background:#edf0ee;color:var(--muted)}.badge.accepted{background:var(--greenbg);color:var(--green)}.badge.rejected{background:var(--redbg);color:var(--red)}
details{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:7px 11px;max-height:38vh;overflow:auto;flex:none}
.help{margin:6px 0;color:var(--muted);white-space:pre-wrap;direction:ltr;text-align:left}
.alt{border-top:1px solid var(--line);padding:6px 0}.althead{direction:ltr;text-align:left;display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px}.althead b{color:var(--ink)}.althead button{padding:2px 9px;font-size:12px}.alt.chosen .althead b{color:var(--accent)}.alt.chosen{background:#f1f8f5}
.ayah{direction:rtl;text-align:right;font:22px/2.1 "Scheherazade New","Geeza Pro","Noto Naskh Arabic",serif;margin:2px 4px}
.text.arabic{font:23px/2.1 "Scheherazade New","Geeza Pro","Noto Naskh Arabic",serif;direction:rtl;text-align:right}summary{cursor:pointer;color:var(--muted)}.note{white-space:pre-wrap;margin:8px 0 2px;text-align:start;unicode-bidi:plaintext;font-family:"Noto Nastaliq Urdu","Geeza Pro",serif}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:8px;display:flex;flex-direction:column;min-height:0;flex:1;overflow:hidden}.panel h2{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:0;padding:9px 13px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between}.text{padding:15px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;font:18px/2 "Noto Nastaliq Urdu","Geeza Pro",serif;direction:auto;text-align:start}.text[contenteditable=true]{outline:none}.text[contenteditable=true]:focus{box-shadow:inset 0 0 0 2px var(--accent)}.text mark{padding:1px 2px;border-radius:3px;color:inherit}.del{background:var(--redbg);text-decoration:line-through}.add{background:var(--greenbg)}.legend{font-size:11px;letter-spacing:0;text-transform:none}.legend span{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 8px}
.pdfpanel{background:var(--paper);border:1px solid var(--line);border-radius:8px;display:flex;flex-direction:column;min-height:0;overflow:hidden}.pdfhead{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-bottom:1px solid var(--line)}.pdfhead a{color:var(--accent)}.pdfview{flex:1;overflow:auto;text-align:center;background:#e7ebe8;padding:10px}.pdfview img{max-width:100%;height:auto;background:#fff;box-shadow:0 1px 5px #68736d}.empty{margin:auto;color:var(--muted);padding:35px;text-align:center}.error{background:var(--redbg);color:var(--red);padding:8px 12px;display:none}.error.show{display:block}
@media(max-width:850px){.workspace{grid-template-columns:1fr;height:auto}.left{height:700px}.pdfpanel{height:700px}.reset{margin-left:0}}
</style>
</head>
<body>
<header>
<div class="top"><h1>Report review</h1><span class="counts" id="counts">Loading…</span></div>
<div class="controls">
<label>Volume <select id="volume"></select></label>
<label>Report <select id="report"><option value="corrections">Corrections</option><option value="quran">Qur’an check</option><option value="hadith">Hadith check</option></select></label>
<label>Show <select id="filter"><option value="all">All</option><option value="unreviewed">Unreviewed</option><option value="accepted">Accepted</option><option value="rejected">Rejected</option></select></label>
<button id="prev">← Previous</button><button id="next">Next →</button>
<button id="accept" class="accept">Accept</button><button id="reject" class="reject">Reject</button>
<button id="reset" class="reset">Reset edit</button>
</div>
</header>
<div id="error" class="error"></div>
<main class="workspace">
<section class="left">
<div class="itembar"><span id="itemtitle" class="itemtitle">No item</span><span id="badge" class="badge"></span></div>
<details id="details" open><summary>Report details</summary><div id="help" class="help"></div><div id="note" class="note" dir="auto"></div><div id="alts"></div></details>
<div class="panel"><h2><span id="originaltitle">Book’s words (as transcribed)</span> <span class="legend">removed <span style="background:var(--redbg)"></span></span></h2><div id="original" class="text" dir="auto"></div></div>
<div class="panel"><h2><span id="correctedtitle">Correction — editable</span> <span class="legend">added <span style="background:var(--greenbg)"></span></span></h2><div id="corrected" class="text" dir="auto" contenteditable="true" spellcheck="false"></div></div>
</section>
<section class="pdfpanel"><div class="pdfhead"><strong id="pdftitle">PDF page</strong><a id="pdflink" target="_blank" rel="noopener">Open PDF</a></div><div class="pdfview" id="pdfview"><div class="empty">Select an item to view its page.</div></div></section>
</main>
<script>
const $=id=>document.getElementById(id);
let allItems=[],items=[],position=0,dirty=false,busy=false,chosenRef=null;
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function tokens(s){return s.match(/\s+|[^\s]+/g)||[]}
function diff(oldText,newText){
 const a=tokens(oldText),b=tokens(newText),m=a.length,n=b.length;
 const dp=Array.from({length:m+1},()=>new Uint32Array(n+1));
 for(let i=m-1;i>=0;i--)for(let j=n-1;j>=0;j--)dp[i][j]=a[i]===b[j]?dp[i+1][j+1]+1:Math.max(dp[i+1][j],dp[i][j+1]);
 const ops=[];let i=0,j=0;
 while(i<m&&j<n){if(a[i]===b[j]){ops.push(['equal',a[i]]);i++;j++}else if(dp[i+1][j]>=dp[i][j+1]){ops.push(['delete',a[i++]])}else ops.push(['add',b[j++]])}
 while(i<m)ops.push(['delete',a[i++]]);while(j<n)ops.push(['add',b[j++]]);return ops;
}
function diffHtml(oldText,newText,side){
 return diff(oldText,newText).filter(([kind])=>kind==='equal'||(side==='old'?kind==='delete':kind==='add')).map(([kind,text])=>{
  const value=escapeHtml(text);return kind==='delete'?'<mark class="del">'+value+'</mark>':kind==='add'?'<mark class="add">'+value+'</mark>':value;
 }).join('');
}
function editedText(){return $('corrected').innerText.replace(/\r/g,'').replace(/\n$/,'')}
function confirmDiscard(){return !dirty||confirm('Discard the unsaved manual edit?')}
async function api(path,options){const response=await fetch(path,options);const data=await response.json();if(!response.ok)throw new Error(data.error||'Request failed');return data}
function showError(message){$('error').textContent=message;$('error').classList.toggle('show',!!message)}
async function loadVolumes(){
 const volumes=await api('/api/volumes');
 $('volume').innerHTML=volumes.map(v=>'<option value="'+v.volume+'" data-reports="'+v.reports.join(',')+'">Volume '+v.volume+'</option>').join('');
 updateReports();await loadItems();
}
function updateReports(){
 const available=($('volume').selectedOptions[0]?.dataset.reports||'').split(',');
 for(const option of $('report').options)option.disabled=!available.includes(option.value);
 if($('report').selectedOptions[0]?.disabled)$('report').value=['corrections','quran','hadith'].find(report=>available.includes(report));
}
async function loadItems(focusLine=null){
 showError('');allItems=await api('/api/items?volume='+$('volume').value+'&report='+$('report').value);applyFilter(focusLine);
}
function applyFilter(focusLine=null){
 const filter=$('filter').value;items=allItems.filter(item=>filter==='all'||item.status===filter);position=0;
 if(focusLine!==null){const found=items.findIndex(item=>item.line===focusLine);if(found>=0)position=found}
 render();
}
function render(){
 dirty=false;showError('');
 const counts=allItems.reduce((out,item)=>{out[item.status]=(out[item.status]||0)+1;return out},{});
 $('counts').textContent=items.length?(position+1)+' of '+items.length+' shown · '+(counts.accepted||0)+' accepted · '+(counts.rejected||0)+' rejected · '+(counts.unreviewed||0)+' unreviewed':'No items in this view';
 $('prev').disabled=!items.length||position===0;$('next').disabled=!items.length||position===items.length-1;
 for(const id of ['accept','reject','reset'])$(id).disabled=!items.length;
 if(!items.length){$('itemtitle').textContent='No item';$('badge').textContent='';$('original').textContent='';$('corrected').textContent='';$('note').textContent='';$('pdftitle').textContent='PDF page';$('pdfview').innerHTML='<div class="empty">No report item selected.</div>';return}
 const item=items[position];
 $('itemtitle').textContent=item.category+' · '+item.page_label+' · '+REPORT_LABEL[item.report];
 $('badge').textContent=item.status;$('badge').className='badge '+item.status;
 chosenRef=item.ref||null;
 $('help').textContent=item.help||'';
 $('note').replaceChildren(...(item.note||'').split('\n').filter(Boolean).map(line=>{const d=document.createElement('div');d.dir='auto';d.textContent=line;return d}));
 $('details').hidden=!item.note&&!item.help&&!(item.alternatives||[]).length;
 for(const id of ['original','corrected']){$(id).classList.toggle('arabic',!!item.arabic);$(id).dir=item.arabic?'rtl':'auto'}
 renderAlternatives(item);
 $('original').innerHTML=diffHtml(item.original,item.corrected,'old');
 $('corrected').innerHTML=diffHtml(item.original,item.corrected,'new');
 for(const id of ['original','corrected']){const pane=$(id),mark=pane.querySelector('mark');if(mark)requestAnimationFrame(()=>{pane.scrollTop+=mark.getBoundingClientRect().top-pane.getBoundingClientRect().top-pane.clientHeight/2})}
 if(item.pdf_page){
  const pdfVolume=item.pdf_volume||item.volume,path='/pdf/vol'+String(pdfVolume).padStart(2,'0')+'.pdf';
  $('pdftitle').textContent='Volume '+pdfVolume+' · PDF page '+item.pdf_page+(item.printed_page?' · printed page '+item.printed_page:'');
  $('pdflink').href=path+'#page='+item.pdf_page;$('pdflink').style.visibility='visible';
  $('pdfview').innerHTML='<div class="empty">Rendering PDF page…</div>';
  const image=new Image();image.alt='PDF page '+item.pdf_page;image.onload=()=>{$('pdfview').replaceChildren(image)};image.onerror=()=>{$('pdfview').innerHTML='<div class="empty">Could not render this PDF page. Use “Open PDF”.</div>'};image.src='/api/page?volume='+pdfVolume+'&page='+item.pdf_page;
 }else{$('pdftitle').textContent='No single PDF page';$('pdflink').style.visibility='hidden';$('pdfview').innerHTML='<div class="empty">This entry refers to multiple pages or has no page number.</div>'}
}
function renderAlternatives(item){
 const alts=item.alternatives||[];
 const compare=item.compare?'<div class="alt"><div class="althead">'+escapeHtml(item.compare.label)+'</div><div class="ayah" dir="rtl" lang="ar">'+escapeHtml(item.compare.text)+'</div></div>':'';
 $('alts').innerHTML=compare+alts.map((alt,k)=>'<div class="alt'+(alt.ref===chosenRef?' chosen':'')+'"><div class="althead"><b>'+(k+1)+'. '+escapeHtml(alt.ref)+'</b><span>match '+escapeHtml(alt.score)+'</span>'+
  (alt.ref===chosenRef?'<span>✓ in the lower box</span>':'<button data-k="'+k+'">Use this</button>')+'</div><div class="ayah" dir="rtl" lang="ar">'+escapeHtml(alt.text)+'</div></div>').join('');
 for(const button of $('alts').querySelectorAll('button'))button.onclick=()=>{const alt=alts[+button.dataset.k];chosenRef=alt.ref;
  $('original').innerHTML=diffHtml(item.original,alt.suggest,'old');$('corrected').innerHTML=diffHtml(item.original,alt.suggest,'new');dirty=true;renderAlternatives(item);setTitles()};
 setTitles();
}
function setTitles(){
 const item=items[position];$('correctedtitle').textContent=item&&item.report==='quran'&&chosenRef?'Qur’an words ('+chosenRef+') — editable':'Correction — editable';
}
const REPORT_LABEL={corrections:'Correction',quran:'Qur’an check',hadith:'Hadith check'};
async function save(status){
 if(!items.length||busy)return;busy=true;showError('');for(const id of ['accept','reject','prev','next'])$(id).disabled=true;
 const item=items[position];
 try{
  await api('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({volume:item.volume,report:item.report,line:item.line,status,corrected:editedText(),ref:chosenRef})});
  dirty=false;await loadItems(item.line);
 }catch(error){
  showError(error.message);for(const id of ['accept','reject'])$(id).disabled=false;
  $('prev').disabled=position===0;$('next').disabled=position===items.length-1;
 }finally{busy=false}
}
$('volume').addEventListener('change',async()=>{if(confirmDiscard()){updateReports();await loadItems()}else render()});
$('report').addEventListener('change',async()=>{if(confirmDiscard())await loadItems();else render()});
$('filter').addEventListener('change',()=>{if(confirmDiscard())applyFilter();else render()});
function move(delta){const next=position+delta;if(next>=0&&next<items.length&&confirmDiscard()){position=next;render()}}
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('accept').onclick=()=>save('accepted');$('reject').onclick=()=>save('rejected');
$('reset').onclick=()=>{if(items.length)render()};
$('corrected').addEventListener('input',()=>{dirty=true});
$('corrected').addEventListener('blur',()=>{if(items.length&&dirty){const item=items[position],text=editedText();$('original').innerHTML=diffHtml(item.original,text,'old');$('corrected').innerHTML=diffHtml(item.original,text,'new')}});
$('corrected').addEventListener('paste',event=>{event.preventDefault();const text=event.clipboardData.getData('text/plain');document.execCommand('insertText',false,text)});
window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue=''}});
loadVolumes().catch(error=>showError(error.message));
</script>
</body>
</html>'''


class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, store):
        self.store = store
        self.page_cache = {}
        super().__init__(address, handler)


class ReviewHandler(BaseHTTPRequestHandler):
    def json_response(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def bytes_response(self, payload, content_type):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        try:
            url = urlparse(self.path)
            if url.path == '/':
                self.bytes_response(PAGE.encode('utf-8'), 'text/html; charset=utf-8')
            elif url.path == '/api/volumes':
                self.json_response(self.server.store.volumes())
            elif url.path == '/api/items':
                query = parse_qs(url.query)
                volume = int(query['volume'][0])
                report = query['report'][0]
                self.json_response(self.server.store.items(volume, report))
            elif url.path == '/api/page':
                query = parse_qs(url.query)
                volume, page = int(query['volume'][0]), int(query['page'][0])
                self.bytes_response(self.render_page(volume, page), 'image/png')
            elif re.fullmatch(r'/pdf/vol\d\d\.pdf', url.path):
                self.send_pdf(int(url.path[8:10]))
            else:
                self.json_response({'error': 'Not found'}, 404)
        except (KeyError, ValueError) as error:
            self.json_response({'error': str(error) or 'Invalid request'}, 400)
        except Exception as error:
            self.json_response({'error': str(error)}, 500)

    def do_POST(self):
        try:
            if urlparse(self.path).path != '/api/review':
                self.json_response({'error': 'Not found'}, 404)
                return
            self.check_same_origin()
            length = int(self.headers.get('Content-Length', '0'))
            if length > 2_000_000:
                raise ValueError('Request is too large')
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            item = self.server.store.review(
                int(data['volume']), data['report'], int(data['line']), data['status'], data['corrected'],
                data.get('ref') or None,
            )
            self.json_response({'ok': True, 'item': item})
        except PermissionError as error:
            self.json_response({'error': str(error)}, 403)
        except (KeyError, ValueError, json.JSONDecodeError) as error:
            self.json_response({'error': str(error) or 'Invalid request'}, 400)
        except Exception as error:
            self.json_response({'error': f'{type(error).__name__}: {error}'}, 500)

    def check_same_origin(self):
        """Only this tool's own page may save. A web page open in another tab could otherwise POST here
        (a form or no-cors fetch cannot send application/json, and a browser always sends Origin on a
        cross-site POST); the Host check stops DNS rebinding."""
        own = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if self.headers.get('Host', '') not in own:
            raise PermissionError('Unexpected Host header')
        origin = self.headers.get('Origin')
        if origin is not None and urlparse(origin).netloc not in own:
            raise PermissionError('Requests from other sites are not accepted')
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            raise PermissionError('Expected application/json')

    def render_page(self, volume, page):
        if volume < 1 or volume > 32 or page < 1:
            raise ValueError('Invalid volume or page')
        key = (volume, page)
        if key in self.server.page_cache:
            return self.server.page_cache[key]
        pdf = ROOT / 'scanned_version' / f'Khutbaat-i-Hakeem-ul-Ummat-Vol-{volume:02d}.pdf'
        if not pdf.exists():
            raise ValueError('PDF not found')
        result = subprocess.run(
            ['pdftoppm', '-f', str(page), '-l', str(page), '-r', '140', '-png', '-singlefile', str(pdf)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=45,
        )
        if len(self.server.page_cache) >= 24:
            self.server.page_cache.pop(next(iter(self.server.page_cache)))
        self.server.page_cache[key] = result.stdout
        return result.stdout

    def send_pdf(self, volume):
        pdf = ROOT / 'scanned_version' / f'Khutbaat-i-Hakeem-ul-Ummat-Vol-{volume:02d}.pdf'
        if not pdf.exists():
            self.json_response({'error': 'PDF not found'}, 404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        self.send_header('Content-Length', str(pdf.stat().st_size))
        self.end_headers()
        with pdf.open('rb') as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--reports-dir', type=Path, default=REPORTS, help=argparse.SUPPRESS)
    args = parser.parse_args()
    store = ReportStore(args.reports_dir.resolve())
    server = ReviewServer(('127.0.0.1', args.port), ReviewHandler, store)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Report reviewer: {url}', flush=True)
    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
