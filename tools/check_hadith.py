"""Check every Arabic passage marked «…» in a volume against the hadith collections.

Usage:
    python3 -I tools/check_hadith.py "<vol dir>" > report.md

Each passage gets one of:
  match     found in a collection, letters agree
  differs   found, but some words differ by a letter or two: likely a reading error; check against the scan
  loose     a related narration exists with different wording (often the author quotes by meaning)
  not found nothing close in the nine collections (sayings, verses of poetry, other books)
The report lists 'differs' first; those are the items to check by hand.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arabic import Hadith, norm, ratio, BOOK_NAMES

SPAN = re.compile(r'«([^»]*)»')


import difflib
SKIP = re.compile(r'^(فَقَدْ|فقد)?\s*(قَالَ|قال)\s|صَلِّ عَلٰی سَیِّدِنَا|صلی اللہ علیٰ سیدنا|وَصَلَّى اللّٰهُ|وَصَلَّی اللّٰهُ|الحمد للہ رب')


def word_diffs(q, m):
    """(book words, reference words) for each place where the two texts differ."""
    qa, ma = q.split(), m.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, qa, ma, autojunk=False).get_opcodes():
        if op != 'equal': out.append((' '.join(qa[i1:i2]) or '—', ' '.join(ma[j1:j2]) or '—'))
    return out


def main():
    vdir = sys.argv[1]
    H = Hadith()
    rows = []
    ndir = os.path.join(vdir, 'page-notes')
    for fn in sorted(os.listdir(ndir)):
        if not fn.endswith('.txt'): continue
        page, in_terms = None, False
        for line in open(os.path.join(ndir, fn), encoding='utf-8'):
            m = re.match(r'^=== \d+ \| (\d+)', line)
            if m: page = int(m.group(1)); in_terms = False; continue
            if line.startswith('## terms'): in_terms = True; continue
            if in_terms: continue
            for sm in SPAN.finditer(line):
                text = sm.group(1)
                if ' / ' in text or len(norm(text).split()) < 3 or SKIP.search(text): continue
                hits = H.find(text)
                if not hits:
                    rows.append(('not found', page, text, None)); continue
                sc, book, no, seg, _ = hits[0]
                q = norm(text)
                d = word_diffs(q, seg)
                if sc >= 0.999: kind = 'match'
                elif sc >= 0.9 and len(d) <= 3: kind = 'differs'
                elif sc >= 0.6: kind = 'loose'
                else: kind = 'not found'
                rows.append((kind, page, text, (sc, book, no, seg, d)))
    order = ['differs', 'loose', 'match', 'not found']
    print(f'# Hadith check: {os.path.basename(vdir)}\n')
    for k in order:
        print(f'- {k}: {sum(r[0] == k for r in rows)}')
    for k in order:
        print(f'\n## {k}\n')
        for kind, page, text, h in rows:
            if kind != k: continue
            line = f'- p{page}: {text}'
            if h:
                sc, book, no, seg, d = h
                line += f'\n  - {BOOK_NAMES[book]} {no} ({sc:.2f})'
                if kind == 'differs':
                    line += '; ' + '، '.join(f'{a} → {b}' for a, b in d)
            print(line)


if __name__ == '__main__':
    main()
