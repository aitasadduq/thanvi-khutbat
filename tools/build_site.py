"""Build the reading website (GitHub Pages) from page-notes, toc.tsv and index.json.

Usage:
    python3 -I tools/build_site.py <out dir> [--artifact]

Writes <out>/index.html (list of volumes) and <out>/vNN.html for every volume in VOLUMES.
Each volume page is self-contained: contents (فہرست), a one-page-at-a-time reader and the
index (اشاریہ). Routes are plain hashes: #contents, #index, #p25 (printed page 25),
#h7 (row 7 of toc.tsv, i.e. a heading of the contents list).
With --artifact the volume page is written without the <!doctype>/<html>/<head> wrapper,
for publishing a preview as a claude.ai artifact.
"""
import sys, os, re, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOLUMES = [
    {'no': 1, 'title': 'دنیا و آخرت', 'dir': 'Index pilot - 01 dunya o akhiret'},
    {'no': 2, 'title': 'علم و عمل', 'dir': 'Vol 02 ilm o amal'},
    {'no': 3, 'title': 'دین و دنیا', 'dir': 'Vol 03 deen o dunya'},
    {'no': 4, 'title': 'حقوق و فرائض', 'dir': 'Vol 04 huqooq o faraiz'},
]
TOTAL_VOLUMES = 32
# Where readers report mistakes: "new issue" page of the public site repository (prefilled with volume and page).
REPORT_URL = 'https://github.com/iatasadduq/thanvi-khutbat-site/issues/new'

URDU_DIG = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ORDINAL = {1: 'اول', 2: 'دوم', 3: 'سوم', 4: 'چہارم', 5: 'پنجم', 6: 'ششم', 7: 'ہفتم', 8: 'ہشتم',
           9: 'نہم', 10: 'دہم'}
def ud(n): return str(n).translate(URDU_DIG)
def esc(s): return html.escape(s, quote=True)

FOLD = str.maketrans({'ك': 'ک', 'ي': 'ی', 'ى': 'ی', 'ه': 'ہ', 'ة': 'ہ', 'ۃ': 'ہ', 'ۂ': 'ہ', 'أ': 'ا',
                      'إ': 'ا', 'ٱ': 'ا', 'ؤ': 'و', 'ئ': 'ی', 'ۓ': 'ے', 'آ': 'ا'})
STRIP = re.compile(r'''[ً-ٰٟۖ-ۭؐ-ؚ«»"'()\[\]،,.:؛!؟?\-]''')
def norm(s): return re.sub(r'\s+', ' ', STRIP.sub('', s.translate(FOLD))).strip()

# Arabic is marked in page-notes: ﴿9:119|ayah text﴾ (verified Qur'an text) and «…» (hadith, dua, other Arabic).
# Both are set in the same Arabic face. Unmarked words with full harakat (fatha..sukun) also get the Arabic face.
MARKUP = re.compile(r'﴿(\d+:[\d:-]+)\|([^﴾]*)﴾|«([^»]*)»')
VOWEL = re.compile(r'[\u064E-\u0652]')
SURAH_UR = None   # filled lazily from build_index's surah list when needed


def _plain(text):
    out = []
    for w in text.split(' '):
        out.append(f'<span class="ar">{esc(w)}</span>' if VOWEL.search(w) else esc(w))
    return ' '.join(out)


def inline(text):
    """Escape a line of text; marked Arabic in the Arabic face. Returns (html, whole line is Arabic)."""
    out, pos, ar_len = [], 0, 0
    for m in MARKUP.finditer(text):
        out.append(_plain(text[pos:m.start()]))
        if m.group(1):
            out.append(f'<span class="ar ay" title="{esc(m.group(1))}">{esc(m.group(2))}</span>')
        else:
            out.append(f'<span class="ar">{esc(m.group(3))}</span>')
        ar_len += len(m.group(0)); pos = m.end()
    out.append(_plain(text[pos:]))
    rest = re.sub(r'[\s"“”()۔،:]', '', MARKUP.sub('', text))
    return ''.join(out), ar_len > 0 and not rest


def read_volume(vdir):
    """Return {printed_page: {'pdf', 'lines', 'summary', 'heads'}} from page-notes/*.txt."""
    pages = {}
    ndir = os.path.join(vdir, 'page-notes')
    for fn in sorted(os.listdir(ndir)):
        if not fn.endswith('.txt'): continue
        cur = None; in_terms = False
        for line in open(os.path.join(ndir, fn), encoding='utf-8'):
            line = line.rstrip('\n')
            m = re.match(r'^=== (\d+) \| (\d+)', line)
            if m:
                cur = {'pdf': int(m.group(1)), 'lines': [], 'summary': None, 'heads': []}
                pages[int(m.group(2))] = cur; in_terms = False
                continue
            if cur is None: continue
            if line.strip() == '## terms': in_terms = True; continue
            if in_terms: continue
            if line.startswith('خلاصہ:'):
                cur['summary'] = line[len('خلاصہ:'):].strip(); continue
            if line.startswith('#'):
                level = 1 if line.startswith('# ') else 2
                for h in line.lstrip('#').split(' / '):
                    cur['heads'].append(h.strip())
                    cur['lines'].append(('h', level, h.strip()))
                continue
            if line.strip():
                cur['lines'].append(('t', 0, line.strip()))
    return pages


def read_toc(vdir):
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(vdir, 'toc.tsv'), encoding='utf-8')][1:]
    return [{'n': i + 1, 'khutba': k, 'title': t, 'page': int(p)} for i, (k, t, p) in enumerate(rows) if p]


def khutbas_of(toc):
    out = []
    for r in toc:
        if not out or out[-1]['name'] != r['khutba']:
            out.append({'name': r['khutba'], 'page': r['page'], 'rows': []})
        out[-1]['rows'].append(r)
    return out


def render_page(no, pg, toc_here, khutba, first_title):
    """HTML for one printed page."""
    unmatched = {r['n']: r for r in toc_here}
    def take(text):
        k = norm(text)
        for n, r in list(unmatched.items()):
            t = norm(r['title'])
            if k == t or (len(k) > 3 and (t.startswith(k) or k.startswith(t))):
                del unmatched[n]; return n
        return None

    body, notes = [], []
    full = any(kind == 't' for kind, _, _ in pg['lines'])
    for kind, level, text in pg['lines']:
        if kind == 'h':
            n = take(text)
            hid = f' id="h{n}"' if n else ''
            cls = 'kt' if norm(text) in first_title else 'sh'
            tag = 'h2' if cls == 'kt' else 'h3'
            if not full: continue
            body.append(f'<{tag} class="{cls}"{hid}>{esc(text)}</{tag}>')
            continue
        m = re.match(r'^\[(حاشیہ|خطبہ ماثورہ|خطبہ):\s*(.*)\]$', text)
        if m and m.group(1) == 'حاشیہ':
            notes.append(f'<p>{inline(m.group(2))[0]}</p>'); continue
        if m:
            body.append(f'<p class="masura"><span class="lbl">{esc(m.group(1))}</span>'
                        f'<span class="ar">{esc(m.group(2))}</span></p>'); continue
        if ' / ' in text and len(text) < 160:
            parts = text.split(' / ')
            if len(parts) == 2 and parts[0].startswith('«') and parts[1].endswith('»') and '»' not in parts[0]:
                parts = ['«' + parts[0][1:] + '»', '«' + parts[1][:-1] + '»']
            misras = ''.join(f'<span>{inline(x.strip())[0]}</span>' for x in parts)
            body.append(f'<p class="sher">{misras}</p>'); continue
        h, ar = inline(text)
        body.append(f'<p class="arb">{h}</p>' if ar else f'<p>{h}</p>')

    if not full:
        # Text not transcribed yet: show the headings that start here, then the summary.
        heads = [f'<h3 class="sh" id="h{r["n"]}">{esc(r["title"])}</h3>' for r in toc_here]
        body = heads + [
            '<div class="pending"><p class="pl">اس صفحے کا مکمل متن ابھی تیار نہیں ہوا۔ فی الحال خلاصہ:</p>'
            f'<p>{inline(pg["summary"] or "")[0]}</p></div>']
    else:
        # Contents headings the transcription did not mark: anchor them at the top of the page.
        body = [f'<span class="anchor" id="h{n}"></span>' for n in unmatched] + body
    # Every block (heading, paragraph, footnote) is numbered so an index link can point into it (see locate()).
    blocks = [x for x in body + notes if not x.startswith('<span')]
    for i, x in enumerate(blocks):
        y = re.sub(r'^(<\w+)', rf'\1 data-b="{i}"', x, count=1)
        if x in body: body[body.index(x)] = y
        else: notes[notes.index(x)] = y
    foot = f'<aside class="notes" aria-label="حواشی">{"".join(notes)}</aside>' if notes else ''
    status = '' if full else ' data-pending="1"'
    return (f'<article class="page" id="p{no}" data-p="{no}"{status}>'
            f'<header class="rh">{esc(khutba)}</header>'
            f'<div class="tx">{"".join(body)}</div>{foot}'
            f'<footer class="pn">{ud(no)}</footer></article>')


def ar_head(head):
    """A hadith index head: its Arabic words in the Arabic face, any Urdu description as it is."""
    from mark_arabic import urdu_word
    words, out, run = head.split(' '), [], []
    def flush():
        if run:
            t = ' '.join(run)
            arabic = len(run) >= 2 and (re.search('[ةهيىكأإؤ]', t) or any(w.startswith('ال') or w in ('لا', 'من', 'فی', 'علی', 'الی') for w in run))
            out.append(f'<span class="ar">{esc(t)}</span>' if arabic else esc(t))
            run.clear()
    for w in words:
        if urdu_word(w) or w in ('حضور', 'ﷺ', 'حدیث', 'قدسی') or w.startswith('('): flush(); out.append(esc(w))
        else: run.append(w)
    flush()
    return ' '.join(out)


# ---- Index links that point into the page -------------------------------------------------------------
# An index link is #p<page>~<locator>. The locator names a block of the page (data-b) and the words to highlight:
# "b" (the whole block) or "b.s.n[.s.n…]" (n words from word s). Words are counted over the block's text nodes,
# split on white space, exactly as the page script counts them.
from html.parser import HTMLParser

STOP = set(norm('کا کی کے میں سے کو نے اور ہے ہیں ہو یہ وہ کہ جو بھی تو پر ایک نہ نہیں تھا تھی تھے کر کرنا کرے '
                'ہی اس ان جس جن کسی کچھ اپنے اپنی اپنا یا لیے لئے بعد پھر اگر مگر جب تک ساتھ طرح والا والے والی '
                'حضرت حضور مولانا رحمہ اللہ علیہ صلی وسلم رضی عنہ تعالی فی من علی الی ما لا ان و ب ل '
                'مولوی شیخ امام حاجی شاہ حافظ خواجہ قاضی علامہ سید نواب صاحب الدین بن ابن عبد').split())
UNIT_MAX = 70     # an Arabic passage or couplet up to this many words is highlighted whole


class _Tokens(HTMLParser):
    """Words of a rendered page: (block, word no. in block, normalised word, unit). A unit is an Arabic span or a
    couplet, so a hit inside a hadith or verse is widened to the whole passage. titles: unit -> ayah reference."""
    def __init__(self):
        super().__init__(); self.out = []; self.stack = []; self.block = None; self.n = 0; self.units = 0
        self.titles = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        unit = None
        if 'data-b' in a: self.block = int(a['data-b']); self.n = 0
        cls = (a.get('class') or '').split()
        if (tag == 'span' and 'ar' in cls) or (tag == 'p' and ('sher' in cls or 'arb' in cls or 'masura' in cls)):
            self.units += 1; unit = self.units
            if 'ay' in cls and a.get('title'): self.titles[unit] = a['title']
        inherited = next((u for _, u in reversed(self.stack) if u), None)
        self.stack.append((tag, unit or inherited))
    def handle_endtag(self, tag):
        while self.stack:
            t, _ = self.stack.pop()
            if t == tag: break
    def handle_data(self, data):
        if self.block is None: return
        # innermost unit: an ayah span inside an Arabic paragraph is its own unit
        unit = next((u for _, u in reversed(self.stack) if u), None)
        for w in data.split():
            self.out.append((self.block, self.n, norm(w), unit)); self.n += 1


def page_tokens(article_html):
    t = _Tokens(); t.feed(article_html); return t.out, t.titles


def _eq(a, b):
    if not a or not b: return False
    if a == b: return True
    return len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a)) and abs(len(a) - len(b)) <= 3


def _unit(toks, u):
    idx = [k for k, t in enumerate(toks) if t[3] == u]
    if not idx or toks[idx[0]][0] != toks[idx[-1]][0]: return ''
    return f'{toks[idx[0]][0]}.{toks[idx[0]][1]}.{toks[idx[-1]][1] - toks[idx[0]][1] + 1}'


def _span(toks, i, j):
    """Locator for tokens i..j (same block), widened to the whole Arabic passage or couplet it lies in."""
    u = toks[i][3]
    if u and u == toks[j][3] and sum(t[3] == u for t in toks) <= UNIT_MAX:
        loc = _unit(toks, u)
        if loc: return loc
    return f'{toks[i][0]}.{toks[i][1]}.{toks[j][1] - toks[i][1] + 1}'


def _ayah_units(titles, surah, ayahs):
    out = []
    for u, ref in titles.items():
        parts = ref.split(':')
        if int(parts[0]) != surah: continue
        a = [int(x) for x in parts[1].split('-')]
        if not ayahs or set(range(a[0], a[-1] + 1)) & ayahs: out.append(u)
    return out


def locate(page, cands, ayahs=()):
    """Best place on a page for an index term. page: page_tokens(); cands: texts in order of preference
    (sub-entry, then head); ayahs: [(surah, {ayah numbers})] for a Qur'an entry. Returns a locator or ''."""
    toks, titles = page
    if not toks: return ''
    for surah, nums in ayahs:
        for u in _ayah_units(titles, surah, nums):
            loc = _unit(toks, u)
            if loc: return loc
    best, best_score = None, 0
    for rank, c in enumerate(cands):
        tw = norm(c).split()
        for i in range(len(tw)):
            for j in range(len(toks)):
                k, e = 0, j        # k term words matched, ending before page word e
                while i + k < len(tw) and e < len(toks) and toks[e][0] == toks[j][0]:
                    if _eq(tw[i + k], toks[e][2]): e += 1
                    elif e + 1 < len(toks) and toks[e + 1][0] == toks[j][0] and tw[i + k] == toks[e][2] + toks[e + 1][2]:
                        e += 2     # عبدالقادر in the term, عبد القادر on the page
                    elif i + k + 1 < len(tw) and tw[i + k] + tw[i + k + 1] == toks[e][2]:
                        e += 1; k += 1     # and the other way round
                    else: break
                    k += 1
                if not k: continue
                content = [w for w in tw[i:i + k] if w not in STOP and len(w) > 2]
                score = 2 * len(content) + 0.3 * (k - len(content)) - 0.1 * rank
                if score > best_score: best, best_score = (j, e - 1), score
    # a run of two content words, or the single content word of a one-word term (a name, a place)
    single = len([w for w in norm(cands[-1]).split() if w not in STOP and len(w) > 2]) <= 1
    if best and (best_score >= 3.5 or (single and best_score >= 1.9)):
        return _span(toks, *best)
    # No run of words: the block sharing most of the term's words, with those words marked.
    words = {w for c in cands for w in norm(c).split() if w not in STOP and len(w) > 2}
    per = {}
    for t in toks:
        if any(_eq(w, t[2]) for w in words): per.setdefault(t[0], set()).add((t[1], t[2]))
    if not per: return ''
    b = max(per, key=lambda b: (len({w for _, w in per[b]}), -b))
    return f'{b}' + ''.join(f'.{n}.1' for n in sorted(n for n, _ in per[b])[:12])


def ayah_refs(head):
    """[(surah, {ayahs})] from an ayat index head such as "البقرة ۲۱۹–۲۲۰" or "النساء ۴۳ / المائدة ۶"."""
    from arabic import SURAH_NO, _NAME_FOLD
    out = []
    for part in head.split(' / '):
        m = re.match(r'^(.*?)\s*([0-9۰-۹]+)?(?:\s*[-–]\s*([0-9۰-۹]+))?$', part.strip())
        no = SURAH_NO.get(m.group(1).translate(_NAME_FOLD)) if m else None
        if not no: continue
        a = [int(x.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))) for x in m.groups()[1:] if x]
        out.append((no, set(range(a[0], a[-1] + 1)) if a else set()))
    return out


def render_index(index, page_toks):
    sections = [('topics', 'موضوعات'), ('ayat', 'آیات قرآنی'), ('hadith', 'احادیث و ادعیہ'),
                ('people', 'شخصیات'), ('stories', 'حکایات و واقعات'), ('parables', 'تمثیلات'),
                ('places', 'مقامات'), ('books', 'کتب'), ('poetry', 'اشعار'), ('sayings', 'اقوال و قواعد')]
    def links(pages, strong=(), cands=(), ayahs=()):
        ps = sorted(set(pages)); out = []; i = 0; strong = set(strong)
        while i < len(ps):
            j = i
            while j + 1 < len(ps) and ps[j + 1] == ps[j] + 1: j += 1
            lab = ud(ps[i]) if i == j else f'{ud(ps[i])}–{ud(ps[j])}'
            b = ' class="b"' if strong & set(ps[i:j + 1]) else ''
            loc = locate(page_toks[ps[i]], cands, ayahs) if ps[i] in page_toks else ''
            out.append(f'<a href="#p{ps[i]}{"~" + loc if loc else ""}"{b}>{lab}</a>')
            i = j + 1
        return '<span class="pp">' + '، '.join(out) + '</span>'
    chips, secs, total = [], [], 0
    for key, title in sections:
        items = index.get(key, [])
        if not items: continue
        total += len(items)
        chips.append(f'<button type="button" class="chip" data-sec="ix-{key}">{title}</button>')
        rows, letter = [], None
        for e in items:
            if key != 'ayat':
                k = norm(re.sub(r'^((حضرت|حضرات|مولانا|مولوی|شیخ|امام|حاجی|شاہ|حافظ|خواجہ|قاضی|علامہ|سید|نواب|حکیم|راجہ)\s+)+', '', e['head'])
                         if key == 'people' else e['head'])
                g = k[:1]
                if g != letter:
                    letter = g; rows.append(f'<h4 class="lt">{esc(g)}</h4>')
            head = re.sub(r'\([^)]*\)', ' ', e['head'])
            ayahs = ayah_refs(e['head']) if key == 'ayat' else ()
            if key == 'people': head = re.sub(r'^(حضرت|حضرات|مولانا|مولوی|شیخ|امام|حاجی|شاہ|حافظ|خواجہ|قاضی|علامہ|سید)\s+', '', head)
            def cands(sub=None):
                c = [sub] if sub and not sub.startswith('ترجمہ یا مفہوم') else []
                return c + [x for x in re.split(r'\s*[:/،]\s*', head) if x.strip()] + [head]
            subs = ''.join(f'<li class="{"ar" if key == "ayat" else ""}">{inline(s["sub"])[0]} '
                           f'{links(s["pages"], s.get("strong", ()), cands(s["sub"]), ayahs)}</li>'
                           for s in e['subs'])
            hh = ar_head(e['head']) if key == 'hadith' else esc(e['head'])
            rows.append(f'<div class="ie"><span class="ih">{hh}</span> {links(e["pages"], e.get("strong", ()), cands(), ayahs)}'
                        + (f'<ul>{subs}</ul>' if subs else '') + '</div>')
        secs.append(f'<section class="ixs" id="ix-{key}"><h3>اشاریۂ {title} <small>({ud(len(items))})</small></h3>'
                    f'<div class="cols">{"".join(rows)}</div></section>')
    return ''.join(chips), ''.join(secs), total


CSS = r'''
/* Layout: an Urdu book on a desk. Sticky top bar; contents rail on the right (wide screens) or a drawer
   (phones); the centre shows one framed printed page at a time, with running head and folio. */
:root{--desk:#e3e8e4;--paper:#fbfcf8;--ink:#1d2523;--muted:#5b6964;--rule:#c9d3ce;--frame:#8fa69e;
--accent:#1d5a52;--wash:#e8efeb;--warn:#8a5a12;--warnbg:#f6eedf;
--f-urdu:'Noto Nastaliq Urdu','Jameel Noori Nastaleeq','Urdu Typesetting',serif;
--f-ar:'Scheherazade New','Amiri','Traditional Arabic',serif;--bar:52px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--desk:#0e1312;--paper:#161d1b;--ink:#dce5e1;
--muted:#93a39d;--rule:#2b3633;--frame:#3e5650;--accent:#7cc3b6;--wash:#1c2624;--warn:#e0b467;--warnbg:#2a2418;color-scheme:dark}}
:root[data-theme="dark"]{--desk:#0e1312;--paper:#161d1b;--ink:#dce5e1;--muted:#93a39d;--rule:#2b3633;--frame:#3e5650;
--accent:#7cc3b6;--wash:#1c2624;--warn:#e0b467;--warnbg:#2a2418;color-scheme:dark}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-padding-top:calc(var(--bar) + 12px)}
body{margin:0;background:var(--desk);color:var(--ink);font-family:var(--f-urdu);font-size:15px;line-height:2.2;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--paper)}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ar,.arb{font-family:var(--f-ar)}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;display:flex;align-items:center;gap:8px 14px;flex-wrap:wrap;
min-height:var(--bar);margin-inline:calc(-1 * max(16px,env(safe-area-inset-left,0px)));
padding-inline:max(16px,env(safe-area-inset-left,0px));background:var(--paper);border-bottom:1px solid var(--rule)}
.bar .home{text-decoration:none;color:var(--ink);font-weight:700;font-size:16px;white-space:nowrap}
.bar .home small{color:var(--muted);font-weight:400;font-size:13px}
.bar nav{display:flex;gap:6px;margin-inline-start:auto;align-items:center;flex-wrap:wrap}
.btn{font:inherit;font-size:13px;line-height:2;border:1px solid var(--rule);background:var(--paper);color:var(--ink);
border-radius:6px;padding:2px 12px;text-decoration:none;cursor:pointer}
.btn[aria-current="true"]{background:var(--accent);border-color:var(--accent);color:var(--paper)}
#goto{display:flex;gap:4px}
#goto input{font:inherit;font-size:13px;width:6.5em;border:1px solid var(--rule);border-radius:6px;background:var(--paper);
color:var(--ink);padding:2px 8px;line-height:2}
.layout{display:grid;grid-template-columns:300px minmax(0,1fr);gap:28px;max-width:1220px;margin:0 auto;padding-block:20px 64px}
#side{position:sticky;top:calc(var(--bar) + 16px);max-height:calc(100vh - var(--bar) - 32px);overflow:auto;
background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:6px 14px 12px;font-size:13.5px;align-self:start}
#side h2{font-size:15px;margin:6px 0;color:var(--accent)}
#side details{border-top:1px solid var(--rule)}
#side summary{cursor:pointer;font-weight:700;padding:2px 0;list-style-position:inside}
#side summary a{color:var(--ink);text-decoration:none}
#side ol{list-style:none;margin:0 0 6px;padding:0}
#side li a{display:flex;justify-content:space-between;gap:10px;text-decoration:none;color:var(--ink);border-radius:4px;padding:0 6px;line-height:2.1}
#side li a span:last-child,.cl .pg{color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
#side a[aria-current="true"]{background:var(--wash);color:var(--accent);font-weight:700}
#side .close{display:none}
main{min-width:0}
.js .view{display:none}.js .view.on{display:block}
/* the printed page */
.page{background:var(--paper);max-width:46rem;margin:0 auto 28px;padding:18px clamp(14px,4vw,40px) 10px;
border:1px solid var(--rule);border-radius:3px;box-shadow:0 1px 0 var(--rule),0 10px 28px -18px rgba(20,40,35,.35)}
.js .page{display:none}.js .page.on{display:block}
.page .rh{text-align:center;color:var(--accent);font-size:13px;border-bottom:3px double var(--frame);padding-bottom:4px;margin-bottom:12px}
.page .tx{font-size:clamp(16px,2.2vw,19px);line-height:2.45;text-align:justify;min-height:22rem}
.page .tx p{margin:0 0 .35em}
.page .kt{font-size:1.45em;text-align:center;color:var(--accent);margin:.3em 0 .5em;text-wrap:balance;line-height:2.1}
.page .sh{font-size:1.08em;text-align:center;color:var(--accent);margin:.6em 0 .3em;text-wrap:balance}
.page .sh::before,.page .sh::after{content:"❖";font-size:.6em;color:var(--frame);margin-inline:.6em;vertical-align:middle}
.page .arb{text-align:center;font-size:1.12em;line-height:2.1}
.page .tx .ar{font-size:1.12em;line-height:2.2}
.report{display:block;text-align:center;font-size:12px;color:var(--muted);margin-top:4px}
.page .sher{display:grid;grid-template-columns:1fr 1fr;gap:0 2em;text-align:center;max-width:36rem;margin:.3em auto .5em}
@media (max-width:560px){.page .sher{grid-template-columns:1fr}}
.page .masura{text-align:center;background:var(--wash);border-radius:6px;padding:4px 10px}
.page .masura .lbl{display:block;font-size:.75em;color:var(--muted)}
.page .notes{border-top:1px solid var(--rule);margin-top:10px;padding-top:4px;font-size:13px;line-height:2.1;color:var(--muted)}
.page .notes p{margin:0}
.page .pn{text-align:center;border-top:3px double var(--frame);margin-top:12px;padding-top:2px;font-size:14px;color:var(--muted)}
.pending{background:var(--warnbg);border-radius:6px;padding:8px 14px;margin-top:8px}
.pending .pl{color:var(--warn);font-size:.8em;margin:0}
mark.hl{background:#f3dd8a;color:inherit;border-radius:3px;box-shadow:0 0 0 2px #f3dd8a}
.hlb{background:color-mix(in srgb,#f3dd8a 28%,transparent);border-radius:4px;box-shadow:0 0 0 4px color-mix(in srgb,#f3dd8a 28%,transparent)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) mark.hl{background:#6b5a1c;box-shadow:0 0 0 2px #6b5a1c}}
:root[data-theme="dark"] mark.hl{background:#6b5a1c;box-shadow:0 0 0 2px #6b5a1c}
.pp a.last{outline:2px solid var(--accent);outline-offset:1px;border-radius:3px}
#backix{display:block;width:fit-content;margin:0 auto 10px}
.flash{animation:fl 1.6s ease-out}
@keyframes fl{from{background:var(--wash)}to{background:transparent}}
@media (prefers-reduced-motion:reduce){.flash{animation:none}}
.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;max-width:46rem;margin:0 auto}
.pager .btn{font-size:14px;padding:4px 16px}
.pager .btn[disabled]{opacity:.4;cursor:default}
.pager .where{color:var(--muted);font-size:13px;text-align:center}
.hint{max-width:46rem;margin:8px auto 0;text-align:center;color:var(--muted);font-size:12px}
/* contents & index */
.sheet{background:var(--paper);border:1px solid var(--rule);border-radius:3px;padding:18px clamp(14px,4vw,40px);max-width:60rem;margin:0 auto}
.sheet h1{font-size:clamp(22px,4vw,30px);color:var(--accent);margin:0;text-align:center;text-wrap:balance;line-height:2}
.sheet .sub{text-align:center;color:var(--muted);margin:0 0 6px}
.status{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 18px;font-size:13px;color:var(--muted);margin-bottom:10px}
.status b{color:var(--ink)}
#resume{display:block;width:fit-content;margin:4px auto 12px}
.cl{columns:2 330px;column-gap:40px;column-rule:1px solid var(--rule)}
.cl section{break-inside:avoid-column;margin-bottom:12px}
.cl h3{margin:0;font-size:17px;display:flex;justify-content:space-between;gap:10px;border-bottom:3px double var(--frame)}
.cl h3 a{color:var(--accent);text-decoration:none}
.cl ol{list-style:none;padding:0;margin:2px 0 0}
.cl li a{display:flex;gap:6px;text-decoration:none;color:var(--ink);line-height:2.1}
.cl li a .t{order:0}
.cl li a .d{flex:1;border-bottom:1px dotted var(--rule);margin-bottom:.7em;min-width:1em}
.cl li a:hover .t{color:var(--accent)}
.ixbar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0 4px;position:sticky;top:var(--bar);z-index:5;
background:var(--paper);padding:6px 0;border-bottom:1px solid var(--rule)}
.ixs h3,.ixs{scroll-margin-top:calc(var(--bar) + 110px)}
.chip{font:inherit;font-size:13px;border:0;background:var(--wash);color:var(--ink);border-radius:6px;padding:0 10px;cursor:pointer;line-height:2.2}
#q{font:inherit;font-size:13px;margin-inline-start:auto;border:1px solid var(--rule);border-radius:6px;background:var(--paper);
color:var(--ink);padding:0 10px;width:220px;max-width:100%;line-height:2.2}
.ixs h3{font-size:19px;color:var(--accent);border-bottom:2px solid var(--accent);margin:22px 0 6px}
.ixs h3 small{color:var(--muted);font-size:13px}
.ixs .cols{column-width:300px;column-gap:32px;column-rule:1px solid var(--rule)}
.ixs h4.lt{margin:10px 0 0;color:var(--accent);font-size:17px;break-after:avoid}
.ie{break-inside:avoid;margin-bottom:3px}
.ie .ih{font-weight:700}
.ie ul{list-style:none;margin:0;padding-inline-start:16px;font-size:13.5px;line-height:2.05}
.ie li::before{content:"— ";color:var(--muted)}
.ie li.ar{font-size:15px}
.pp{font-size:12.5px;font-variant-numeric:tabular-nums}
.pp a{text-decoration:none}
.pp a.b{font-weight:700}
.pp a:hover{text-decoration:underline}
.note{font-size:12.5px;color:var(--muted);margin-top:16px;line-height:2.1}
.scrim{display:none}
@media (max-width:999px){
 .layout{grid-template-columns:minmax(0,1fr)}
 #side{position:fixed;z-index:20;top:0;bottom:0;right:0;width:min(340px,88vw);max-height:none;border-radius:0;
  padding-top:calc(env(safe-area-inset-top,0px) + 8px);padding-right:max(14px,env(safe-area-inset-right,0px));
  transform:translateX(105%);transition:transform .2s ease;box-shadow:-8px 0 30px -12px rgba(0,0,0,.4)}
 #side.open{transform:none}
 #side .close{display:inline-block;float:left}
 .scrim.open{display:block;position:fixed;inset:0;z-index:15;background:rgba(10,20,18,.35)}
}
@media (min-width:1000px){#tocbtn{display:none}}
@media (prefers-reduced-motion:reduce){#side{transition:none}}
'''

JS = r'''
(function(){
const D=window.VOL, pages=[...document.querySelectorAll('.page')], byNo={};
pages.forEach(p=>byNo[+p.dataset.p]=p);
const nums=pages.map(p=>+p.dataset.p), first=nums[0], last=nums[nums.length-1];
const views={contents:document.getElementById('v-contents'),reader:document.getElementById('v-reader'),index:document.getElementById('v-index')};
const UD='۰۱۲۳۴۵۶۷۸۹', ud=n=>String(n).replace(/\d/g,d=>UD[d]);
const side=document.getElementById('side'), scrim=document.querySelector('.scrim');
const KEY='khutbat-v'+D.vol+'-last';
let cur=null;
function store(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function load(k){try{return localStorage.getItem(k)}catch(e){return null}}
function show(name){for(const k in views)views[k].classList.toggle('on',k===name);
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-current',b.dataset.view===name?'true':'false'));}
function tocAt(p){let r=null;for(const t of D.toc){if(t.page<=p)r=t;else break}return r}
function markSide(p){const t=tocAt(p);
 side.querySelectorAll('a[aria-current]').forEach(a=>a.removeAttribute('aria-current'));
 if(!t)return;const a=side.querySelector('a[href="#h'+t.n+'"]');
 if(a){a.setAttribute('aria-current','true');const d=a.closest('details');if(d&&!d.open)d.open=true;
  const r=a.getBoundingClientRect(),s=side.getBoundingClientRect();if(r.top<s.top||r.bottom>s.bottom)a.scrollIntoView({block:'center'});}}
function clearMarks(){document.querySelectorAll('mark.hl').forEach(m=>{const t=document.createTextNode(m.textContent);m.replaceWith(t);t.parentNode.normalize()});
 document.querySelectorAll('.hlb').forEach(b=>b.classList.remove('hlb'));}
// Locator from an index link: block, then (first word, number of words) pairs; words counted over text nodes.
function highlight(pg,loc){const n=loc.split('.').map(Number),blk=pg.querySelector('[data-b="'+n[0]+'"]');if(!blk)return null;
 if(n.length<3){blk.classList.add('hlb');return blk;}
 const want=new Set();for(let i=1;i+1<n.length;i+=2)for(let k=0;k<n[i+1];k++)want.add(n[i]+k);
 const w=document.createTreeWalker(blk,NodeFilter.SHOW_TEXT),nodes=[];while(w.nextNode())nodes.push(w.currentNode);
 let c=0,firstMark=null;
 for(const t of nodes){const re=/\S+/g,hits=[];let m;while((m=re.exec(t.data))){if(want.has(c))hits.push([m.index,m.index+m[0].length]);c++;}
  const runs=[];for(const h of hits){const r=runs[runs.length-1];if(r&&/^\s*$/.test(t.data.slice(r[1],h[0])))r[1]=h[1];else runs.push(h.slice());}
  for(let i=runs.length-1;i>=0;i--){const r=document.createRange();r.setStart(t,runs[i][0]);r.setEnd(t,runs[i][1]);
   const mk=document.createElement('mark');mk.className='hl';r.surroundContents(mk);firstMark=mk;}}
 if(n.length>3)blk.classList.add('hlb');
 return firstMark||blk;}
function openPage(p,target,loc){
 if(!byNo[p]){p=Math.min(Math.max(p,first),last);while(!byNo[p]&&p<last)p++;}
 clearMarks();
 if(cur)cur.classList.remove('on');cur=byNo[p];cur.classList.add('on');show('reader');
 document.getElementById('backix').hidden=!fromIndex;
 document.getElementById('where').textContent='صفحہ '+ud(p)+' — '+ud(first)+' تا '+ud(last);
 var rp=document.getElementById('report'); if(rp){var t='جلد '+VOL.vol+'، صفحہ '+p+': غلطی'; var b='جلد '+VOL.vol+'، صفحہ '+p+'\n\nغلط متن:\n\nصحیح متن:\n';
  rp.href=rp.getAttribute('href').split('?')[0]+'?title='+encodeURIComponent(t)+'&body='+encodeURIComponent(b);}
 document.getElementById('prev').disabled=p<=first;document.getElementById('next').disabled=p>=last;
 document.title=D.title+' · صفحہ '+ud(p);
 store(KEY,p);markSide(p);
 const el=target&&document.getElementById(target);
 if(el&&el.closest('.page')===cur){el.scrollIntoView({block:'start'});el.classList.add('flash');setTimeout(()=>el.classList.remove('flash'),1700);}
 else{window.scrollTo(0,0);const h=loc&&highlight(cur,loc);if(h)h.scrollIntoView({block:'center'});}}
// Where the reader was in the index when they followed a page link, to return there.
let fromIndex=null;try{fromIndex=JSON.parse(sessionStorage.getItem(KEY+'-ix'))}catch(e){}
document.getElementById('v-index').addEventListener('click',e=>{const a=e.target.closest('.pp a');if(!a)return;
 document.querySelectorAll('.pp a.last').forEach(x=>x.classList.remove('last'));a.classList.add('last');
 const all=[...document.querySelectorAll('.pp a')];fromIndex={y:window.scrollY,a:all.indexOf(a)};
 try{sessionStorage.setItem(KEY+'-ix',JSON.stringify(fromIndex))}catch(e){}});
function showIndex(){show('index');
 if(!fromIndex){window.scrollTo(0,0);return;}
 const a=document.querySelectorAll('.pp a')[fromIndex.a];
 if(a){a.classList.add('last');const ie=a.closest('.ie');
  if(!a.offsetParent)window.scrollTo(0,fromIndex.y);else{a.scrollIntoView({block:'center'});}
  if(ie){ie.classList.add('flash');setTimeout(()=>ie.classList.remove('flash'),1700);}}
 else window.scrollTo(0,fromIndex.y);}
function route(){const h=decodeURIComponent(location.hash.slice(1));let m;
 if((m=h.match(/^p(\d+)(?:~([\d.]+))?$/)))return openPage(+m[1],null,m[2]);
 if((m=h.match(/^h(\d+)$/))){const t=D.toc.find(t=>t.n==+m[1]);if(t)return openPage(t.page,h);}
 document.title=D.title;
 if(h==='index'){showIndex();return;}
 show('contents');window.scrollTo(0,0);
 const l=+load(KEY),r=document.getElementById('resume');
 if(l&&byNo[l]){r.hidden=false;r.href='#p'+l;r.textContent='صفحہ '+ud(l)+' سے پڑھنا جاری رکھیں';}}
function go(d){if(!cur)return;const i=nums.indexOf(+cur.dataset.p)+d;if(i>=0&&i<nums.length)location.hash='p'+nums[i];}
document.getElementById('prev').onclick=()=>go(-1);
document.getElementById('next').onclick=()=>go(1);
document.addEventListener('keydown',e=>{if(!views.reader.classList.contains('on')||e.target.closest('input'))return;
 if(e.key==='ArrowLeft'){go(1);e.preventDefault()}else if(e.key==='ArrowRight'){go(-1);e.preventDefault()}});
let sx=null,sy=0;
views.reader.addEventListener('touchstart',e=>{if(e.touches.length===1){sx=e.touches[0].clientX;sy=e.touches[0].clientY}},{passive:true});
views.reader.addEventListener('touchend',e=>{if(sx===null)return;const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;sx=null;
 if(Math.abs(dx)>70&&Math.abs(dx)>2*Math.abs(dy))go(dx>0?1:-1);},{passive:true});
document.getElementById('goto').addEventListener('submit',e=>{e.preventDefault();
 const v=document.getElementById('gotop').value.replace(/[۰-۹]/g,d=>UD.indexOf(d)).replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).trim();
 if(/^\d+$/.test(v))location.hash='p'+v;});
function drawer(o){side.classList.toggle('open',o);scrim.classList.toggle('open',o);document.getElementById('tocbtn').setAttribute('aria-expanded',o)}
document.getElementById('tocbtn').onclick=()=>drawer(!side.classList.contains('open'));
scrim.onclick=()=>drawer(false);side.querySelector('.close').onclick=()=>drawer(false);
side.addEventListener('click',e=>{if(e.target.closest('a'))drawer(false)});
const q=document.getElementById('q');
q.addEventListener('input',()=>{const v=q.value.trim();
 document.querySelectorAll('.ie').forEach(e=>e.hidden=!!v&&!e.textContent.includes(v));
 document.querySelectorAll('.ixs h4').forEach(h=>h.hidden=!!v);});
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>document.getElementById(c.dataset.sec).scrollIntoView({block:'start'}));
window.addEventListener('hashchange',route);route();
})();
'''


def build_volume(v, artifact=False):
    vdir = os.path.join(ROOT, v['dir'])
    pages = read_volume(vdir)
    toc = read_toc(vdir)
    ks = khutbas_of(toc)
    index = json.load(open(os.path.join(vdir, 'index.json'), encoding='utf-8'))
    first_titles = {norm(k['rows'][0]['title']) for k in ks} | {norm(k['name']) for k in ks}
    vt = f'جلد {ORDINAL.get(v["no"], ud(v["no"]))}'
    title = f'خطبات حکیم الامت، {vt}'

    arts = []
    for no in sorted(pages):
        here = [r for r in toc if r['page'] == no]
        k = next((x['name'] for x in reversed(ks) if x['page'] <= no), '')
        arts.append(render_page(no, pages[no], here, k, first_titles))
    n_full = sum(1 for p in pages.values() if any(t == 't' for t, _, _ in p['lines']))
    full_nums = [n for n in sorted(pages) if any(t == 't' for t, _, _ in pages[n]['lines'])]

    side, cl = [], []
    for i, k in enumerate(ks):
        end = ks[i + 1]['page'] - 1 if i + 1 < len(ks) else max(pages)
        items = ''.join(f'<li><a href="#h{r["n"]}"><span>{esc(r["title"])}</span><span>{ud(r["page"])}</span></a></li>'
                        for r in k['rows'][1:])
        side.append(f'<details><summary><a href="#h{k["rows"][0]["n"]}">{esc(k["name"])}</a></summary><ol>{items}</ol></details>')
        citems = ''.join(f'<li><a href="#h{r["n"]}"><span class="t">{esc(r["title"])}</span><span class="d"></span>'
                         f'<span class="pg">{ud(r["page"])}</span></a></li>' for r in k['rows'][1:])
        cl.append(f'<section><h3><a href="#h{k["rows"][0]["n"]}">{esc(k["name"])}</a>'
                  f'<span class="pg">{ud(k["page"])}–{ud(end)}</span></h3><ol>{citems}</ol></section>')

    page_toks = {no: page_tokens(a) for no, a in zip(sorted(pages), arts)}
    chips, ix, ix_total = render_index(index, page_toks)
    full_range = f'{ud(full_nums[0])}–{ud(full_nums[-1])}' if full_nums else '—'
    data = json.dumps({'vol': v['no'], 'title': title,
                       'toc': [{'n': r['n'], 'page': r['page']} for r in toc]}, ensure_ascii=False)

    head = f'''<title>{esc(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="خطبات حکیم الامت مولانا اشرف علی تھانویؒ، {vt}: {esc(v['title'])} — متن، فہرست اور اشاریہ">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
<script>document.documentElement.classList.add('js')</script>
<style>{CSS}</style>'''
    body = f'''<div dir="rtl" lang="ur">
<header class="bar">
<button type="button" class="btn" id="tocbtn" aria-controls="side" aria-expanded="false">فہرست</button>
<a class="home" href="#contents">خطبات حکیم الامت <small>· {vt}: {esc(v['title'])}</small></a>
<nav aria-label="کتاب">
<a class="btn" href="#contents" data-view="contents">فہرست مضامین</a>
<a class="btn" href="#index" data-view="index">اشاریہ</a>
<form id="goto" role="search"><input id="gotop" inputmode="numeric" placeholder="صفحہ نمبر" aria-label="صفحہ نمبر پر جائیں"><button class="btn" type="submit">جائیں</button></form>
</nav></header>
<div class="scrim"></div>
<div class="layout">
<aside id="side" aria-label="فہرست"><button type="button" class="btn close">بند کریں</button><h2>فہرست مضامین</h2>{''.join(side)}</aside>
<main>
<section class="view" id="v-contents"><div class="sheet">
<h1>خطبات حکیم الامت</h1>
<p class="sub">حکیم الامت مولانا اشرف علی تھانویؒ · {vt}: {esc(v['title'])}</p>
<div class="status"><span><b>{ud(len(ks))}</b> مواعظ</span><span><b>{ud(len(toc) - len(ks))}</b> ذیلی عنوانات</span>
<span>صفحات <b>{ud(min(pages))}–{ud(max(pages))}</b></span><span>مکمل متن: <b>{ud(n_full)}</b> صفحات ({full_range})</span></div>
<a class="btn" id="resume" href="#p{min(pages)}" hidden></a>
<div class="cl">{''.join(cl)}</div>
<p class="note">کسی عنوان پر کلک کریں تو وہ صفحہ کھل جائے گا۔ صفحات کتاب کی طرح ایک ایک کر کے پڑھے جاتے ہیں: «اگلا صفحہ» اور «پچھلا صفحہ» کے بٹن، کی بورڈ کے تیر یا موبائل پر انگلی سے سوائپ۔ صفحہ نمبر کتاب کے مطبوعہ صفحات کے مطابق ہیں۔</p>
</div></section>
<section class="view" id="v-reader">
<a class="btn" id="backix" href="#index" hidden>→ اشاریہ میں واپس جائیں</a>
<div id="pages">{''.join(arts)}</div>
<nav class="pager" aria-label="صفحات"><button type="button" class="btn" id="prev">→ پچھلا صفحہ</button>
<span class="where" id="where"></span><button type="button" class="btn" id="next">اگلا صفحہ ←</button></nav>
<p class="hint">کی بورڈ: ← اگلا صفحہ، → پچھلا صفحہ</p>
<a class="report" id="report" href="{REPORT_URL}" target="_blank" rel="noopener">اس صفحے میں کوئی غلطی نظر آئے تو اطلاع دیں</a>
</section>
<section class="view" id="v-index"><div class="sheet">
<h1>اشاریہ</h1><p class="sub">{vt}: {esc(v['title'])} · {ud(ix_total)} اندراجات · صفحہ نمبر پر کلک کریں تو وہ صفحہ کھل جائے گا</p>
<div class="ixbar">{chips}<input id="q" type="search" placeholder="اشاریہ میں تلاش…" aria-label="اشاریہ میں تلاش"></div>
{ix}
<p class="note">جہاں کسی حدیث کا عربی متن صفحے پر نہیں بلکہ صرف اس کا ترجمہ یا مفہوم بیان ہوا ہے، وہ صفحہ «ترجمہ یا مفہوم» کے تحت درج ہے۔ آیات کا متن مستند مصحف سے لیا گیا ہے۔</p>
</div></section>
</main></div></div>
<script>window.VOL={data}</script>
<script>{JS}</script>'''
    if artifact:
        return head + '\n' + body
    return f'<!doctype html>\n<html lang="ur" dir="rtl">\n<head>\n<meta charset="utf-8">\n' \
           f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'


def build_home():
    have = {v['no']: v for v in VOLUMES}
    items = []
    for n in range(1, TOTAL_VOLUMES + 1):
        if n in have:
            items.append(f'<li><a href="v{n:02d}.html"><b>جلد {ud(n)}</b><span>{esc(have[n]["title"])}</span></a></li>')
        else:
            items.append(f'<li class="off"><b>جلد {ud(n)}</b><span>زیر تیاری</span></li>')
    return f'''<!doctype html>
<html lang="ur" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>خطبات حکیم الامت</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{{--desk:#e3e8e4;--paper:#fbfcf8;--ink:#1d2523;--muted:#5b6964;--rule:#c9d3ce;--accent:#1d5a52}}
@media (prefers-color-scheme:dark){{:root{{--desk:#0e1312;--paper:#161d1b;--ink:#dce5e1;--muted:#93a39d;--rule:#2b3633;--accent:#7cc3b6;color-scheme:dark}}}}
body{{margin:0;background:var(--desk);color:var(--ink);font-family:'Noto Nastaliq Urdu',serif;line-height:2.2;
padding:24px max(16px,env(safe-area-inset-left,0px)) 64px max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:60rem;margin:0 auto;background:var(--paper);border:1px solid var(--rule);padding:20px clamp(14px,4vw,40px)}}
h1{{text-align:center;color:var(--accent);margin:0;font-size:clamp(24px,5vw,34px)}}
p{{text-align:center;color:var(--muted);margin:0 0 16px}}
ul{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}
li a,li.off{{display:flex;flex-direction:column;border:1px solid var(--rule);border-radius:6px;padding:4px 12px;text-decoration:none;color:var(--ink)}}
li a b{{color:var(--accent)}} li a:hover{{border-color:var(--accent)}}
li.off{{color:var(--muted);opacity:.7}} li span{{font-size:13px}}
</style></head><body>
<main><h1>خطبات حکیم الامت</h1><p>حکیم الامت مولانا اشرف علی تھانویؒ کے مواعظ — متن، فہرست اور اشاریہ</p>
<ul>{''.join(items)}</ul></main>
</body></html>
'''


if __name__ == '__main__':
    out = sys.argv[1]
    artifact = '--artifact' in sys.argv
    os.makedirs(out, exist_ok=True)
    for v in VOLUMES:
        path = os.path.join(out, f'v{v["no"]:02d}.html')
        open(path, 'w', encoding='utf-8').write(build_volume(v, artifact))
        print('wrote', path, os.path.getsize(path), 'bytes')
    if not artifact:
        open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(build_home())
