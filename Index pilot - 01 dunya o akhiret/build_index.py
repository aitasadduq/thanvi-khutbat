"""Build an Urdu back-of-book index from per-page transcripts.

Input: directory of *.txt files with blocks
    === <pdf_page> | <printed_page>
    ...text...
    ## terms
    <Type>: <Head> > <Sub>
Output: index.json (structured) and index.html (printable, RTL).
"""
import sys, os, re, json, html
from collections import defaultdict

SRC, OUT = sys.argv[1], sys.argv[2]
TOC = sys.argv[3] if len(sys.argv) > 3 else None

TYPE_MAP = {
    'موضوع': 'topics', 'قاعدہ': 'sayings', 'قاعدہ فقہیہ': 'sayings', 'قول': 'sayings',
    'آیت': 'ayat', 'حدیث': 'hadith', 'شخصیت': 'people', 'حکایت': 'stories',
    'مثال': 'parables', 'مقام': 'places', 'کتاب': 'books', 'شعر': 'poetry', 'دعا': 'hadith',
}
SECTIONS = [
    ('topics', 'اشاریۂ موضوعات'), ('ayat', 'اشاریۂ آیات قرآنی'), ('hadith', 'اشاریۂ احادیث و ادعیہ'),
    ('people', 'اشاریۂ شخصیات'), ('stories', 'اشاریۂ حکایات و واقعات'), ('parables', 'اشاریۂ تمثیلات'),
    ('places', 'اشاریۂ مقامات'), ('books', 'اشاریۂ کتب'), ('poetry', 'اشاریۂ اشعار'),
    ('sayings', 'اشاریۂ اقوال و قواعد'),
]

# Heads that are spelling/wording variants of one heading.
MERGE = {
    'ارادۂ آخرت': 'ارادہ', 'ارادۂ دنیا': 'ارادہ', 'قصد و ارادہ': 'ارادہ',
    'شیخ کامل': 'شیخ کامل', 'شیوخ کاملین': 'شیوخ', 'شیخ محقق': 'شیوخ', 'مشائخ': 'شیوخ',
    'پیران باطل': 'شیوخ', 'پیران دنیا دار': 'شیوخ',
    'صحبت اہل اللہ': 'صحبت', 'صحبت علماء': 'صحبت', 'صحبت بد': 'صحبت', 'صحبت صادقین': 'صحبت',
    'صحبت عشاق': 'صحبت',
    'مراقبۂ موت': 'مراقبہ', 'مراقبۂ آخرت': 'مراقبہ',
    'موت کی یاد': 'موت', 'موت کی تمنا': 'موت', 'موت کا اشتیاق': 'موت',
    'طالب آخرت': 'طلب آخرت', 'طالب دنیا': 'طلب دنیا',
    'ترجیح دنیا': 'ترجیح دنیا علی الآخرۃ',
    'ریاء و عجب': 'ریاء', 'عجب': 'عجب',
    'نعمائے جنت': 'جنت', 'نعمائے آخرت': 'آخرت',
    'رضا بالقضاء': 'رضا', 'رضائے الٰہی': 'رضا',
    'محبت الٰہی': 'محبت الٰہی', 'حب اللہ': 'محبت الٰہی', 'عشق الٰہی': 'محبت الٰہی',
    'محبت طبعیہ و عقلیہ': 'محبت',
    'علماء و طلبہ': 'علماء', 'علماء و دراویش': 'علماء', 'علماء پر اعتراض': 'علماء',
    'علماء سے سوال': 'علماء', 'علماء کی عزت': 'علماء', 'علماء کی خدمت': 'علماء',
    'قساوت قلب': 'قساوت قلب', 'منکر تقدیر': 'تقدیر',
    'کسب دنیا و حب دنیا': 'کسب دنیا', 'تعلق مع اللہ': 'نسبت مع اللہ',
    'طریق وصول الی اللہ': 'وصول الی اللہ', 'خدا تک پہنچنے کا راستہ': 'وصول الی اللہ',
    'زاہد خشک': 'زہد', 'قیامت': 'قیامت', 'حشر': 'قیامت',
    'اولاد کی موت': 'اولاد', 'تعلیم اولاد': 'اولاد', 'تعلیم اطفال': 'اولاد',
    'اطمینان بالدنیا': 'اطمینان بالدنیا', 'رضا بالدنیا': 'رضا بالدنیا',
    'عورتیں': 'عورتیں', 'مستورات': 'عورتیں',
    'حکیم الامتؒ کے احوال': 'حکیم الامتؒ (ذاتی احوال)',
    'وعظ کی تاریخ': 'مواعظ (تاریخ و مقام)',
    'اہل سنت': 'اہل سنت والجماعت', 'امر بالمعروف': 'امر بالمعروف و نہی عن المنکر',
    'انفاق': 'انفاق فی سبیل اللہ', 'بدعات': 'بدعت', 'بدعت و جہالت': 'بدعت',
    'تجدید ایمان': 'تجدید ایمان و نکاح', 'تکلفات': 'تکلف', 'جزا': 'جزا و سزا',
    'دین دار': 'دیندار', 'دین داری': 'دیندار', 'رجا': 'رجاء', 'ذکر و شغل': 'ذکر',
    'سوال کرنا': 'سوال', 'حال و مقام': 'حال', 'حال و اعمال': 'حال', 'حال کے حصول کا طریقہ': 'حال',
    'جہنم': 'دوزخ', 'دوزخ میں تعذیب و تہذیب': 'دوزخ', 'دنیا کو آخرت پر ترجیح': 'ترجیح دنیا علی الآخرۃ',
    'مردے': 'مردہ', 'معجزہ': 'معجزات', 'ملازمت، زمینداری، تجارت': 'ملازمت', 'ملازمت و زراعت': 'ملازمت',
    'کبر': 'تکبر', 'رخصت': 'عزیمت و رخصت', 'عزیمت': 'عزیمت و رخصت', 'ہدایا': 'ہدیہ',
    'وظائف و نوافل': 'وظائف', 'معرفت الٰہی': 'معرفت', 'کشف و خواب': 'کشف', 'کشف و کرامات': 'کشف',
    'حزن': 'غم', 'فقر و فاقہ': 'فاقہ', 'عذاب قبر و دوزخ': 'عذاب قبر',
    'صغائر': 'گناہ صغیرہ و کبیرہ', 'صغیرہ گناہ': 'گناہ صغیرہ و کبیرہ', 'کبیرہ و صغیرہ': 'گناہ صغیرہ و کبیرہ',
    'شکوہ الٰہی': 'شکایت الٰہی', 'متکلمین و حکماء': 'متکلمین', 'نیکیاں': 'نیکی', 'نیک عمل': 'نیکی',
    'اعمال صالحہ': 'عمل صالح', 'لذات دنیوی': 'لذات دنیا', 'توجہ': 'توجہ شیخ', 'توجہ متعارف': 'توجہ شیخ',
    'سالکین کا دھوکہ': 'سالکین', 'زمیندار': 'زمینداری', 'اتباع': 'اتباع سنت', 'سنت': 'اتباع سنت',
    'رجاء': 'خوف و رجاء', 'خوف و خشیت': 'خوف',
}
PEOPLE_MERGE = {
    'حافظ ضامن شہیدؒ': 'حافظ محمد ضامن شہیدؒ', 'حضرت عباسؓ': 'حضرت عباس بن عبدالمطلبؓ',
    'مولانا فضل الرحمٰن گنج مرادآبادیؒ': 'مولانا شاہ فضل الرحمٰن گنج مرادآبادیؒ',
    'مولوی سعید احمد': 'مولوی سعید احمد تھانوی', 'سعید احمد تھانوی': 'مولوی سعید احمد تھانوی',
    'شیخ فرید الدین (گنج شکر یا عطار)ؒ': 'شیخ فریدؒ', 'ظفر احمد عثمانیؒ': 'مولانا ظفر احمد عثمانیؒ',
}
HONORIFIC_EXEMPT = {'شاہ ایران', 'شاہ جہان', 'حکیم سنائیؒ'}
_HON = re.compile(r'^((حضرت|حضرات|مولانا|مولوی|شیخ|امام|حاجی|شاہ|حافظ|خواجہ|قاضی|علامہ|سید|نواب|حکیم|راجہ)\s+)+')
class _H:
    def sub(self, r, h): return h if h in HONORIFIC_EXEMPT else _HON.sub(r, h)
HONORIFIC = _H()

URDU_ORDER = 'ا آ ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ں و ہ ھ ء ی ے'.split()
RANK = {c: i for i, c in enumerate(URDU_ORDER)}
FOLD = str.maketrans({'ك': 'ک', 'ي': 'ی', 'ى': 'ی', 'ه': 'ہ', 'ة': 'ہ', 'ۃ': 'ہ', 'ۂ': 'ہ', 'أ': 'ا',
                      'إ': 'ا', 'ٱ': 'ا', 'ؤ': 'و', 'ئ': 'ی', 'ۓ': 'ے', 'ھ': 'ھ'})
STRIP = re.compile(r'''[\u064B-\u065F\u0670\u06D6-\u06ED\u0610-\u061A\uFDFA«»"'()\[\]،,.:؛!؟?\-]''')

def sort_key(s):
    s = STRIP.sub('', s.translate(FOLD))
    s = re.sub(r'^(ال|حضرت |مولانا |شیخ |امام |حاجی |شاہ |حافظ |خواجہ |قاضی |علامہ |سید )', '', s) if False else s
    return [RANK.get(c, 200 + ord(c) % 1000) if c != ' ' else -1 for c in s]

URDU_DIG = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ASCII_DIG = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
def ud(n): return str(n).translate(URDU_DIG)

def ranges(pages):
    ps = sorted(set(pages)); out = []; i = 0
    while i < len(ps):
        j = i
        while j + 1 < len(ps) and ps[j + 1] == ps[j] + 1: j += 1
        out.append(ud(ps[i]) if i == j else f'{ud(ps[i])}–{ud(ps[j])}')
        i = j + 1
    return '، '.join(out)

SURAHS = ('الفاتحة البقرة آل_عمران النساء المائدة الانعام الاعراف الانفال التوبة یونس ہود یوسف الرعد ابراہیم الحجر '
          'النحل بنی_اسرائیل الکہف مریم طہ الانبیاء الحج المؤمنون النور الفرقان الشعراء النمل القصص العنکبوت الروم '
          'لقمان السجدة الاحزاب سبا فاطر یٰس الصافات ص الزمر غافر حم_السجدة الشوریٰ الزخرف الدخان الجاثیة الاحقاف '
          'محمد الفتح الحجرات ق الذاریات الطور النجم القمر الرحمٰن الواقعة الحدید المجادلة الحشر الممتحنة الصف '
          'الجمعة المنافقون التغابن الطلاق التحریم الملک القلم الحاقة المعارج نوح الجن المزمل المدثر القیامة الدہر '
          'المرسلات النبا النازعات عبس التکویر الانفطار المطففین الانشقاق البروج الطارق الاعلیٰ').split()
SURAH_NO = {s.replace('_', ' ').translate(FOLD): i + 1 for i, s in enumerate(SURAHS)}
SURAH_NO.update({'فصلت': 41, 'الزلزال': 99, 'الاخلاص': 112, 'یس': 36, 'الشوری': 42, 'الاعلی': 87})

def parse_ayah(head):
    m = re.match(r'(.+?)\s+([۰-۹0-9][۰-۹0-9–\-،, ]*)', head)
    name = (m.group(1) if m else head).split('/')[0].strip()
    nums = m.group(2).strip() if m else ''
    first = re.findall(r'\d+', nums.translate(ASCII_DIG))
    no = SURAH_NO.get(name.translate(FOLD), 999)
    return name, nums, no, int(first[0]) if first else 0

entries = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))  # sec -> head -> sub -> pages
summaries = {}
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith('.txt'): continue
    page = None; in_terms = False
    for line in open(os.path.join(SRC, fn), encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'^=== (\d+) \| (\d+)', line)
        if m: page = int(m.group(2)); in_terms = False; continue
        if line.startswith('خلاصہ:') and page: summaries[page] = line[6:].strip()
        if line.startswith('## terms'): in_terms = True; continue
        if line.startswith('#'): in_terms = False; continue
        if not in_terms or ':' not in line or page is None: continue
        typ, rest = line.split(':', 1)
        sec = TYPE_MAP.get(typ.strip())
        if not sec: continue
        head, _, sub = rest.partition('>')
        head, sub = head.strip(), sub.strip()
        if sec == 'topics': head = MERGE.get(head, head)
        if sec == 'people': head = PEOPLE_MERGE.get(head, re.sub(r'\s*\(.*?\)\s*$', '', head))
        entries[sec][head][sub].add(page)

def esc(s): return html.escape(s)

out_json = {}
body = []
counts = {}
for sec, title in SECTIONS:
    heads = entries.get(sec, {})
    if not heads: continue
    if sec == 'ayat':
        order = sorted(heads, key=lambda h: (parse_ayah(h)[2], parse_ayah(h)[3], h))
    else:
        order = sorted(heads, key=(lambda h: sort_key(HONORIFIC.sub('', h))) if sec == 'people' else sort_key)
    counts[sec] = len(order)
    out_json[sec] = []
    body.append(f'<section id="{sec}"><h2>{title} <span class="n">({ud(len(order))})</span></h2>')
    letter = None
    body.append('<div class="cols">')
    for h in order:
        subs = heads[h]
        allp = set().union(*subs.values())
        if sec == 'ayat':
            name, nums, no, _ = parse_ayah(h)
            grp = f'سورۃ {name}' if no != 999 else name
        else:
            k = STRIP.sub('', (HONORIFIC.sub('', h) if sec == 'people' else h).translate(FOLD))
            grp = k[:1] if k else ''
            if grp == 'آ': grp = 'ا'
        if grp != letter:
            letter = grp
            body.append(f'<h3 class="letter">{esc(grp)}</h3>')
        named = {s: p for s, p in subs.items() if s}
        out_json[sec].append({'head': h, 'pages': sorted(allp),
                              'subs': [{'sub': s, 'pages': sorted(p)} for s, p in named.items()]})
        if sec == 'ayat':
            label = f'{esc(name)} {esc(nums)}' if nums else esc(name)
            texts = sorted(named, key=lambda s: min(named[s]))
            body.append(f'<div class="e"><span class="h">{label}</span> <span class="p">{ranges(allp)}</span>')
            for s in texts:
                body.append(f'<div class="s ar">{esc(s)} <span class="p">{ranges(named[s])}</span></div>')
            body.append('</div>')
            continue
        if len(named) <= 1 and len(allp) <= 3 and sec != 'topics':
            extra = f' — {esc(next(iter(named)))}' if named else ''
            body.append(f'<div class="e"><span class="h">{esc(h)}</span>{extra} <span class="p">{ranges(allp)}</span></div>')
            continue
        body.append(f'<div class="e"><span class="h">{esc(h)}</span> <span class="p">{ranges(allp)}</span>')
        for s in sorted(named, key=sort_key):
            body.append(f'<div class="s">{esc(s)} <span class="p">{ranges(named[s])}</span></div>')
        body.append('</div>')
    body.append('</div></section>')

toc_rows = []
if TOC:
    rows = [l.rstrip('\n').split('\t') for l in open(TOC, encoding='utf-8')][1:]
    seen = []
    for k, t, p in rows:
        if k not in [x[0] for x in seen]: seen.append((k, int(p)))
    for k, p in seen:
        toc_rows.append(f'<li><span>{esc(k)}</span><span class="p">{ud(p)}</span></li>')

total_loc = sum(len(p) for sec in entries.values() for h in sec.values() for p in h.values())
n_pages = len(summaries)
json.dump(out_json, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: v for k, v in counts.items()}, 'entries total', sum(counts.values()),
      'locators', sum(len(p) for sec in entries.values() for h in sec.values() for p in h.values()))

nav = ''.join(f'<a href="#{s}">{t.replace("اشاریۂ ", "")}</a>' for s, t in SECTIONS if s in counts)
page = f'''<title>Thanvi Dunya o Akhirat Index</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
/* Layout: a printed-book index — RTL, multi-column entries under alphabet letters, sticky section bar with search. */
:root{{--bg:#f6f8f5;--fg:#1a2420;--muted:#5d6b66;--rule:#d3dcd7;--accent:#1d5a52;--chip:#e6ede9;
--f-urdu:'Noto Nastaliq Urdu','Jameel Noori Nastaleeq','Urdu Typesetting',serif;--f-arabic:'Amiri','Traditional Arabic',serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#111715;--fg:#e2eae6;--muted:#97a6a0;--rule:#2c3733;--accent:#7cc3b6;--chip:#1c2522;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#111715;--fg:#e2eae6;--muted:#97a6a0;--rule:#2c3733;--accent:#7cc3b6;--chip:#1c2522;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font-family:var(--f-urdu);font-size:15px;line-height:2.3;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
body::before{{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}}
.wrap{{max-width:1180px;margin:0 auto;padding-block:24px 80px}}
header h1{{font-size:clamp(22px,4vw,30px);margin:0;color:var(--accent);font-weight:600;text-wrap:balance;line-height:2}}
header p{{color:var(--muted);margin:4px 0 0;font-size:14px}}
.stats{{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:10px;font-size:13px;color:var(--muted)}}
.stats b{{color:var(--fg);font-weight:600}}
nav{{position:sticky;top:env(safe-area-inset-top,0px);background:var(--bg);border-bottom:1px solid var(--rule);padding:8px 0;display:flex;flex-wrap:wrap;gap:6px;z-index:2;align-items:center}}
nav a{{text-decoration:none;color:var(--fg);background:var(--chip);border-radius:6px;padding:0 10px;font-size:13px}}
nav a:focus-visible,nav input:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
nav input{{margin-inline-start:auto;font:inherit;font-size:13px;padding:0 10px;border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--fg);min-width:0;width:200px;max-width:100%}}
h2{{font-size:22px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:4px;margin:40px 0 8px;font-weight:600}}
h2 .n{{font-size:14px;color:var(--muted)}}
.cols{{column-width:330px;column-gap:36px;column-rule:1px solid var(--rule)}}
h3.letter{{font-size:19px;margin:14px 0 2px;color:var(--accent);break-after:avoid}}
.e{{break-inside:avoid;margin:0 0 4px}}
.e .h{{font-weight:600}}
.s{{padding-inline-start:18px;font-size:14px;line-height:2.1}}
.s::before{{content:'— ';color:var(--muted)}}
.ar{{font-family:var(--f-arabic);font-size:16px;line-height:1.9}}
.p{{color:var(--muted);font-size:13px;font-variant-numeric:tabular-nums}}
.toc{{columns:2 260px;list-style:none;padding:0;margin:8px 0 0}}
.toc li{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px dotted var(--rule);break-inside:avoid}}
.note{{background:var(--chip);border-radius:8px;padding:10px 14px;font-size:13px;color:var(--muted);margin-top:14px;line-height:2.2}}
</style>
<div class="wrap" dir="rtl" lang="ur">
<header><h1>اشاریہ — خطبات حکیم الامت، جلد اول: دنیا و آخرت</h1>
<p>تمام حوالے کتاب کے مطبوعہ صفحات کے ہیں (پی ڈی ایف صفحہ = مطبوعہ صفحہ + ۱)۔ تجرباتی نسخہ برائے جائزہ۔</p>
<div class="stats"><span><b>{ud(sum(counts.values()))}</b> اندراجات</span><span><b>{ud(total_loc)}</b> صفحاتی حوالے</span><span><b>{ud(len(toc_rows))}</b> مواعظ</span><span><b>{ud(n_pages)}</b> صفحات</span></div></header>
<nav aria-label="اقسام اشاریہ">{nav}<input id="q" type="search" placeholder="تلاش کریں…" aria-label="اشاریہ میں تلاش"></nav>
<section><h2>فہرست مواعظ</h2><ul class="toc">{''.join(toc_rows)}</ul>
<div class="note">طریق کار: ہر صفحہ کو پڑھ کر اس کے موضوعات، آیات، احادیث، شخصیات، حکایات، تمثیلات، مقامات، کتب اور اشعار الگ الگ درج کیے گئے، پھر ہم معنی عنوانات کو یکجا کر کے اردو حروف تہجی کی ترتیب سے مرتب کیا گیا۔ آیات سورتوں کی ترتیب سے ہیں۔ صفحات کا تسلسل ہو تو «۲۵–۲۸» کی صورت میں لکھا گیا ہے۔</div></section>
{''.join(body)}
</div>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const v=q.value.trim();
document.querySelectorAll('.e').forEach(e=>{{e.hidden=!!v&&!e.textContent.includes(v)}});
document.querySelectorAll('h3.letter').forEach(h=>{{h.hidden=!!v}});}});
</script>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
