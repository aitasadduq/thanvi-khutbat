"""Mark the Arabic passages in a volume's page-notes and put in the verified Qur'an text.

Usage:
    python3 -I tools/mark_arabic.py "<vol dir>" [--write]

Markup written into page-notes (also what transcription should use from now on):
    ﴿9:119|<Qur'an text>﴾   an ayah or part of one; the text is copied from the reference mushaf
    «<Arabic>»               any other Arabic: hadith, dua, Arabic saying or verse
Both are set in the Arabic face on the site.

Without --write the script only reports what it would change. The report lists
  QURAN   spans replaced by the reference text (with the old text when the letters differed)
  CHECK   spans that look like the Qur'an but did not match well enough to replace
  ARABIC  spans marked as other Arabic
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arabic import Quran, norm, ratio, cited_surah, SURAHS

URDU_CHARS = re.compile('[ٹڈڑںےگچپژ]')
URDU_WORDS = set(('ہے ہیں کہ میں کی کا کے سے نے کو اور یہ وہ تو بھی نہ تھا تھے تھی پر جو اس جس کس ایک یعنی '
              'خلاصہ وعظ تاریخ اشاعت بمطابق '
              # Persian (couplets are not Arabic)
              'اند است ست را می بر از چہ چو چوں نیست باشد شد شود کند کرد در ایں آں تا باید خود ہمہ گر اگر بود نبود باش').split())
HARAKAT = re.compile(r'[ً-ْٰ]')
VOWEL = re.compile(r'[\u064E-\u0652]')      # fatha..sukun: Urdu words (تعالیٰ، فوراً) never carry these
ANY_MARK = re.compile(r'[﴿﴾«»]')


def urdu_word(w):
    w = w.strip('"\'“”()،۔.:!؟?')
    return bool(URDU_CHARS.search(w)) or w in URDU_WORDS


def is_ar_word(w):
    return bool(VOWEL.search(w))


def arabic_runs(words):
    """Index ranges [s, e) of runs of vocalised words; short unvocalised gaps without Urdu words are bridged."""
    runs, s, last = [], None, None
    for i, w in enumerate(words):
        if s is not None and w[:1] in '"“(' and last == i - 1:
            runs.append((s, last + 1)); s = None      # a new quotation starts
        if is_ar_word(w):
            if s is None: s = i
            last = i
            if w[-1:] in '"”)' and w[:1] not in '"“(':
                runs.append((s, last + 1)); s = None  # quotation closed
        elif s is not None and (urdu_word(w) or i - last > 2):
            runs.append((s, last + 1)); s = None
    if s is not None: runs.append((s, last + 1))
    return runs


def plain_arabic_line(words):
    """A whole line of unvocalised Arabic (hadith typed without harakat)."""
    core = [w for w in words if w.strip('"\'“”()،۔.:!؟?')]
    return len(core) >= 2 and not any(urdu_word(w) for w in core) and \
        sum(w.lstrip('"“(').startswith(('ال', 'لا', 'من', 'فی', 'ما', 'ان', 'علی', 'اللہ', 'و')) for w in core) >= 1


def split_trail(words):
    """Keep trailing punctuation/quotes outside the marked span."""
    head = words[0]; tail = words[-1]
    lead = re.match(r'^["“(]*', head).group(0)
    trail = re.search(r'["”)۔،:.]*$', tail).group(0)
    inner = ' '.join(words)
    inner = inner[len(lead):len(inner) - len(trail)] if trail else inner[len(lead):]
    return lead, inner, trail


def good(Q, f):
    """A match is usable when it is clean at both ends; short ones must be near-exact."""
    return Q.clean(f[1], f[2]) and (f[2] - f[1] >= 12 or f[0] >= 0.95)


def terms_of(block):
    return [l.split(':', 1)[1].split('|')[0].split('>')[-1].strip()
            for l in block if re.match(r'^(حدیث|دعا|قول):', l)]


PREAMBLE = re.compile(r'^((?:فَقَدْ|فقد)\s+)?(?:قَالَ|قال)\s+(?:اللّٰهُ|اللہ|النَّبِیُّ|النبی)\s+.*?(?:تَعَالٰ[یى]|تعالیٰ|وَسَلَّمَ|وسلم):?\s+')
ELLIPSIS = re.compile(r'\s*(?:\.\.\.|…|۔۔۔)\s*')


def fits(Q, f, text):
    """A Qur'an match to use: near-exact, clean at both ends, and covering the whole quotation."""
    if not f or f[0] < 0.9 or not good(Q, f): return False
    n = len(norm(text).replace(' ', ''))
    if not 0.85 <= (f[2] - f[1]) / max(1, n) <= 1.15: return False
    # first and last words must be the same words (no words of the book dropped or swapped at the ends)
    # Only spelling-level differences are corrected: same number of words, each word nearly the same.
    # A wording difference (the author quoting loosely) is left as printed and reported for checking.
    tw, cw = norm(text).split(), norm(Q.text(f[1], f[2])).split()
    return len(tw) == len(cw) and all(a == b or ratio(a, b) >= 0.8 for a, b in zip(tw, cw))


_H = None
def is_hadith(text, quran_score):
    """True when the passage is closer to a hadith than to any ayah (so it is not reported as an ayah)."""
    global _H
    if _H is None:
        from arabic import Hadith
        _H = Hadith()
    h = _H.find(text, top=1)
    return bool(h) and h[0][0] >= quran_score


FORMULAS = {norm('الحمد لله رب العالمين'), norm('والحمد لله رب العالمين')}
PAGE_SURAHS = {}   # page -> surahs of ayat already quoted on that page (and the page before)


def choose(Q, f, cited, page):
    """Of all places where the matched words occur, take the one the book cites (surah and ayah, else surah),
    else one in an ayah or surah already quoted nearby (a phrase like لو کانوا یعلمون occurs in several ayat)."""
    occ = Q.occurrences(f[1], f[2])
    if cited:
        for test in (lambda s: Q.ayah(s) == cited, lambda s: Q.surah(s) == cited[0]):
            for s, e in occ:
                if test(s): return (f[0], s, e), True
    near = [a for p in range(page - 35, page + 1) for a in PAGE_SURAHS.get(p, [])]
    for test in (lambda s, a: Q.ayah(s) == a, lambda s, a: Q.surah(s) == a[0]):
        for a in reversed(near):
            for s, e in occ:
                if test(s, a): return (f[0], s, e), not cited
    return (f[0],) + occ[0], not cited


def mark(inner, Q, report, page, after='', decisions=None, cited=None):
    def cited_in(ref):
        """None when nothing is cited; else whether the cited ayah lies inside ref (\"9:119\" or \"17:18-21\")."""
        if not cited: return None
        su, ay = ref.split(':'); a = [int(x) for x in ay.split('-')]
        # every ayah number in the citation counts: (بنی اسرائیل ۱۸، ۱۹), (… ۱۸ تا ۲۱)
        par = re.match(r'[^()]*\(([^)]*)\)', after)
        nums = {int(x.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')))
                for x in re.findall(r'[0-9۰-۹]+', par.group(1))} if par else set()
        nums.add(cited[1])
        return int(su) != cited[0] or any(a[0] <= n <= a[-1] for n in nums)
    """Markup for one Arabic quotation. `after` is the text that follows it (for a citation)."""
    if ELLIPSIS.search(inner):
        return ' ... '.join(mark(x, Q, report, page, '', decisions) for x in ELLIPSIS.split(inner) if x.strip())
    m = PREAMBLE.match(inner)
    if m and len(inner) > m.end():
        return f'«{inner[:m.end()].strip()}» ' + mark(inner[m.end():], Q, report, page, after, decisions)
    key = (page, norm(inner))
    dec = (decisions or {}).get(key)
    if dec and dec[0] != 'keep':
        s, e = Q.phrase(*dec)
        report.append(f'DECIDED p{page} {Q.ref(s, e)} (owner): {inner} → {Q.text(s, e)}')
        return f'﴿{Q.ref(s, e)}|{Q.text(s, e)}﴾'
    cited = cited or cited_surah(after)
    if norm(inner) in FORMULAS and not cited:      # closing praise of a sermon, not a quotation
        report.append(f'ARABIC p{page}  {inner}')
        return f'«{inner}»'
    f = Q.find(inner) if len(norm(inner).split()) >= 2 else None
    if fits(Q, f, inner):
        f, ok = choose(Q, f, cited, page)
        ref = Q.ref(f[1], f[2]); canon = Q.text(f[1], f[2])
        PAGE_SURAHS.setdefault(page, []).append(Q.ayah(f[1]))
        if norm(canon) != norm(inner):
            report.append(f'QURAN  p{page} {ref} [{f[0]:.2f}]\n   old: {inner}\n   new: {canon}')
        if ok and cited and cited_in(ref) is False:      # right surah, wrong ayah number
            ok = False
        if not ok:
            report.append(f'CITE   p{page} the words are {ref}, but the book cites {SURAHS[cited[0] - 1].replace("_", " ")} {cited[1]} '
                          f'({cited[0]}:{cited[1]}): {after[:40].strip()}\n   text: {canon}')
        return f'﴿{ref}|{canon}﴾'
    if dec and dec[0] == 'keep':
        report.append(f'KEPT   p{page} (owner: keep as printed) {inner}')
    elif f and f[0] >= 0.78 and not is_hadith(inner, f[0]):
        if False:
            report.append(f'KEPT   p{page} (owner: keep as printed) {inner}')
        else:
            alts = '\n'.join(f'   alt {i + 1}: {Q.ref(g[1], g[2])} [{g[0]:.2f}] {Q.text(*Q.span(Q.ref(g[1], g[2])))}'
                             for i, g in enumerate(Q.alternatives(inner)))
            report.append(f'DIFFERS p{page}\n   book: {inner}\n{alts}')
    else:
        report.append(f'ARABIC p{page}  {inner}')
    return f'«{inner}»'


AYAH_MARK = re.compile(r'﴿(\d+):(\d+)[^|﴾]*\|([^﴾]*)﴾')


def fragment(Q, text, ref):
    """(ref, Qur'an words) when `text` is a run of whole words inside ayah `ref`, else None."""
    try:
        s, e = Q.span(ref)
    except (AttributeError, IndexError):
        return None
    q = norm(text).replace(' ', '')
    i = Q.flat.find(q, s, e) if q else -1
    while i >= 0 and not Q.clean(i, i + len(q)):   # e.g. وصبرو first hits inside آمنوا اصبروا
        i = Q.flat.find(q, i + 1, e)
    if i < 0: return None
    return Q.ref(i, i + len(q)), Q.text(i, i + len(q))


def recheck(m, Q, report, page, decisions):
    """An ayah marked by hand: replaced by the verified text, or (wording differs) reported to the owner."""
    n = len(report)
    # the book's own citation after the ayah wins over the reference written while transcribing
    book = cited_surah(m.string[m.end():])
    new = mark(m.group(3), Q, report, page, m.string[m.end():] if book else '', decisions,
               cited=book or (int(m.group(1)), int(m.group(2))))
    if new.startswith('«') and len(norm(m.group(3)).split()) <= 3:
        # a word or two of the marked ayah quoted for comment (tafsir): too short to search the whole
        # Qur'an, but exact within the ayah the transcriber named
        frag = fragment(Q, m.group(3), f'{m.group(1)}:{m.group(2)}')
        if frag:
            report[n:] = []
            ref, canon = frag
            if norm(canon) != norm(m.group(3)):
                report.append(f'QURAN  p{page} {ref} [fragment]\n   old: {m.group(3)}\n   new: {canon}')
            return f'﴿{ref}|{canon}﴾'
    if new.startswith('«') and not any(r.startswith(('DIFFERS', 'KEPT')) for r in report[n:]):
        report[n:] = []
        alts = '\n'.join(f'   alt {i + 1}: {Q.ref(g[1], g[2])} [{g[0]:.2f}] {Q.text(*Q.span(Q.ref(g[1], g[2])))}'
                         for i, g in enumerate(Q.alternatives(m.group(3))))
        report.append(f'DIFFERS p{page} (marked {m.group(1)}:{m.group(2)} while transcribing)\n   book: {m.group(3)}\n{alts}')
    return new


# the author's signature and the colophon at the end of a sermon are Urdu, not quotations
SIGNATURE = re.compile(r'^\(?(اشرف علی|حکیم الامت (مجدد الملت )?حضرت مولانا اشرف علی|بحمد اللہ تمت|بحمد اللہ تمام)')


def process(lines, Q, report, page, decisions=None):
    """Return new lines for one page's text part."""
    out = []
    for line in lines:
        if ANY_MARK.search(line) and decisions:
            # already marked: apply any owner decision made since the last run to its «…» passages
            def apply(m):
                key = (page, norm(m.group(1)))
                dec = decisions.get(key)
                if not dec or dec[0] == 'keep': return m.group(0)
                return mark(m.group(1), Q, report, page, '', decisions)
            line = re.sub(r'«([^»]*)»', apply, line)
        # ayat marked while transcribing (﴿ref|text﴾) are checked like unmarked ones; the ref is the citation
        line = AYAH_MARK.sub(lambda m: recheck(m, Q, report, page, decisions), line)
        if not line.strip() or line.startswith(('#', '[', '===')) or '\t' in line or ANY_MARK.search(line) or SIGNATURE.match(line):
            out.append(line); continue
        words = line.split(' ')
        spans = arabic_runs(words)
        if not spans and plain_arabic_line(words):
            spans = [(0, len(words))]
        new, pos = [], 0
        for s, e in spans:
            lead, inner, trail = split_trail(words[s:e])
            if len(inner.split()) < 2: continue
            new.extend(words[pos:s])
            after = trail + ' ' + ' '.join(words[e:])
            new.append(lead + mark(inner, Q, report, page, after, decisions) + trail)
            pos = e
        new.extend(words[pos:])
        out.append(' '.join(new))
    return out


def read_decisions(vdir):
    """quran-decisions.tsv: page, the book's words, and `keep` or `<ref>` + tab + the Qur'an words to use."""
    path = os.path.join(vdir, 'quran-decisions.tsv'); out = {}
    if os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if not l.strip() or l.startswith('#'): continue
            f = l.rstrip('\n').split('\t')
            out[(int(f[0]), norm(f[1]))] = ('keep',) if f[2] == 'keep' else (f[2], f[3])
    return out


def main():
    vdir = sys.argv[1]; write = '--write' in sys.argv
    Q = Quran(); report = []; decisions = read_decisions(vdir)
    ndir = os.path.join(vdir, 'page-notes')
    for fn in sorted(os.listdir(ndir)):
        if not fn.endswith('.txt'): continue
        path = os.path.join(ndir, fn)
        src = open(path, encoding='utf-8').read().split('\n')
        out, block, page, in_terms = [], [], None, False
        def flush():
            out.extend(process(block, Q, report, page, decisions)); block.clear()
        for l in src:
            m = re.match(r'^=== \d+ \| (\d+)', l)
            if m:
                flush(); page = int(m.group(1)); in_terms = False; out.append(l); continue
            if l.strip() == '## terms':
                flush(); in_terms = True; out.append(l); continue
            (out if in_terms or page is None else block).append(l)
        flush()
        if write and out != src:
            open(path, 'w', encoding='utf-8').write('\n'.join(out))
    order = ['DIFFERS', 'CITE', 'DECIDED', 'KEPT', 'QURAN', 'ARABIC']
    titles = {'DIFFERS': "Book's ayah differs from the Qur'an: owner to decide (closest ayat given)",
              'CITE': "Words match an ayah, but not the surah the book cites",
              'DECIDED': "Replaced as the owner decided", 'KEPT': "Kept as printed (owner's decision)",
              'QURAN': "Spelling corrected to the Qur'an text", 'ARABIC': "Other Arabic (hadith, dua, verse)"}
    for k in order:
        rows = [r for r in report if r.split()[0] == k]
        print(f'\n## {titles[k]} ({len(rows)})\n')
        for r in rows: print(r)
    print('\n# ' + ', '.join(f"{k}: {sum(r.split()[0] == k for r in report)}" for k in order), file=sys.stderr)


if __name__ == '__main__':
    main()
