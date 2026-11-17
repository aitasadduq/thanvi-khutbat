# PLAN — read this first (resume point for every new chat or after compression)

This file is the single source of truth for **what to do next and which rules apply**. It overrides older
statements in `HANDOFF.md` where they differ (HANDOFF §2–3 describe the state on 2026-10-28; §9–10 are current).
Update the **Status** and **Next steps** sections at the end of every working session and after every owner decision.

---

## 1. Status (2026-11-16)

- **Report review tool:** `python3 -I tools/review_reports.py` opens a local browser UI for corrections, Qur'an checks and hadith checks. Corrections show the actual page transcription (or contents row), with the original reconstructed from the report's literal replacement; report explanations stay under Report details. Both panes scroll to the highlighted change beside the scan. Adjacent-page report offsets, cross-volume source references and multi-row contents summaries are supported. Accept/Reject saves an inline `<!-- review: ... -->` marker in the existing report without removing the entry; manual edits are saved as Review edit text. It does not apply or revert `page-notes/` edits. Regenerating a Qur'an/hadith report replaces its inline review markers.
- **Volume 23 (راہ نجات) — done, awaiting the owner's review.** Folder `Vol 23 rah e najat/`. PDF page = printed
  page + 1; text printed pp. 17–400 (10 sermons: الاستغفار 17, آثار الحوبۃ فی اسرار التوبۃ 42, استمرار التوبۃ علیٰ تکرار
  الحوبۃ 92, تفصیل التوبۃ 139, ضرورۃ التوبۃ 170, اول الاعمال 201, الافتضاح 242, العبرۃ بذبح البقرۃ 266, اطاعۃ الاحکام مع
  فضل دار حدیث خیر الانام 356, الظلم 373), all transcribed (files 0018, 0043, 0093, 0140, 0171, 0202, 0243, 0267, 0357,
  0374). `toc.tsv` regenerated from the page headings (573 rows; consecutive repeats of a heading across a page break
  collapsed). mark_arabic: DIFFERS 0, CITE 0 (two citations corrected with editor's notes: ہود ۴۴ → ۵۲ on p. 17,
  القیمۃ ۵۶ → المدثر ۵۶ on p. 140; one Arabic couplet on p. 82 written as one «… … …» mark). Hadith check:
  `reports/vol23-hadith-check.md` (12 differs, all the book's wording). Corrections: `reports/vol23-corrections.md`
  (rows for the owner, e.g. «بر سیر» p. 348 unidentified book, a probably missing line between pp. 378/379, 24:28
  and 2:286 printed without a word their glosses translate). Index built (1874 entries); site rebuilt
  (`site/v23.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/8tzXXV6eqdSHcpqLsjBqun
- **Volume 22 (ذکر و فکر) — done, awaiting the owner's review.** Folder `Vol 22 zikr o fikr/`. PDF page = printed
  page + 1; text printed pp. 21–440 (11 sermons: تفصیل الذکر 21, المراقبہ 43, القاف 67, شرط التذکر 127, رطوبۃ اللسان 151,
  شرف المکالمہ 175, راحت القلوب 197, جلاء القلوب 242, ذم النسیان 335, التثبیت بمراقبۃ المبیت 389, زکوٰۃ النفس 411), all
  transcribed (files 0022, 0044, 0068, 0128, 0152, 0176, 0198, 0243, 0336, 0390, 0412). `toc.tsv` regenerated from the
  page headings (493 rows; changes logged). mark_arabic: DIFFERS 0, CITE 0 (36:69 split word joined; النور ۳۶ citation
  corrected to ۳۶ تا ۳۸ with editor's note); 26 Arabic lines marked; «درکارند» added to the Persian words and the ضابط's
  signature to SIGNATURE in `mark_arabic.py` (Vols 19–21 output unchanged). Hadith check: `reports/vol22-hadith-check.md`
  (16 differs, all the book's wording). Corrections: `reports/vol22-corrections.md` (rows for the owner, e.g. «حال» →
  «مآل» p. 420, «تخلیہ» p. 441, 6:75 «المؤمنین» for «الموقنین»). Index built (2109 entries); site rebuilt
  (`site/v22.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/9X55LMbFzx83GJChJApYoN (not watched: remote session).
- **Volume 21 (تدبیر و توکل) — done, awaiting the owner's review.** Folder `Vol 21 tadbeer o tawakkul/`. PDF page =
  printed page + 1; text printed pp. 17–456 (12 sermons: اجابۃ الداعی 17, التوکل 58, الاصابۃ فی معنی الاجابۃ 97,
  الفصل والانفصال 115, شفاء العی 163, العمل للعلماء 195, التیسیر للتیسیر 228, القرض 275, الشکر 318, تحقیق الشکر 342,
  التنبہ 378, فوائد الصحبۃ 402), all transcribed (files 0018, 0059, 0098, 0116, 0164, 0196, 0229, 0276, 0319, 0343,
  0379, 0403). `toc.tsv` regenerated from the page headings (524 rows; changes logged). mark_arabic: DIFFERS 0, CITE 0;
  8 Arabic lines marked; Persian couplet words added to `mark_arabic.py` (Vols 19–20 output unchanged). Hadith check:
  `reports/vol21-hadith-check.md` (19 differs, all the book's wording). Corrections: `reports/vol21-corrections.md`
  (several "confirm" rows for the owner, e.g. 31:31 for the الشکر khutba ayah, ذوالنون «بصری», «گوں» p. 455). Index
  built (2120 entries); site rebuilt (`site/v21.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/RooyXSnd9Fx4TDHu8m431A (not watched: remote session).
- **Volume 20 (حقوق الزوجین) — done, awaiting the owner's review.** Folder `Vol 20 huqooq uz zaujain/`. PDF page =
  printed page + 1; text printed pp. 11–440 (10 sermons: حقوق البیت 11, الکمال فی الدین للنساء 52, رفع الالتباس 111,
  اصلاح النساء 141, کساء النساء 162, العاقلات الغافلات 243, عضل الجاہلیہ 288, الاستماع والاتباع 312, منازعۃ الہویٰ 350,
  غایۃ النجاح فی آیۃ النکاح 387), all transcribed (files 0012, 0053, 0112, 0142, 0163, 0244, 0289, 0313, 0351, 0388).
  `toc.tsv` (309 rows): 10 headings/pages set to the page (logged). mark_arabic: DIFFERS 0, CITE 0 (p. 324 «الیٰ قولہ»
  between 39:15 and 39:16 restored from the scan; two typing slips fixed). Hadith check: `reports/vol20-hadith-check.md`
  (16 differs, all the book's wording). Corrections: `reports/vol20-corrections.md`. Index built (1867 entries); site
  rebuilt (`site/v20.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/4AceXaakkPdmSpmjMUzPQV (not watched: remote session). `mark_arabic.py` now also skips date lines, «ظفر احمد عفا اللہ عنہ», «الملقب بہ…» and
  Persian couplet lines with Urdu letters (Vols 1–19 output unchanged). Sessions 2026-11-12 ran as a scheduled
  resume; the commit trailer now carries that session's link.

- **Volume 19 (آداب انسانیت) — done, awaiting the owner's review.** Folder `Vol 19 adab e insaniyat/`. PDF page =
  printed page + 1; text printed pp. 11–464 (11 sermons from ذم ہویٰ p. 11 to عمل الذرہ p. 427), all transcribed (files
  0012, 0049, 0093, 0127, 0157, 0180, 0214, 0264, 0322, 0359, 0403, 0415, 0428). `toc.tsv` (333 rows): headings and
  pages follow the text (6 spellings, 5 pages, one split heading joined, 17 missing rows such as «تمہید» added; all
  logged). mark_arabic: DIFFERS 0, CITE 0 (a p. 160 ayah placeholder filled from the scan). Hadith check:
  `reports/vol19-hadith-check.md` (26 differs, all the book's wording). Corrections: `reports/vol19-corrections.md`
  (pp. 11–428 were corrected while transcribing in earlier sessions but not logged row by row). Index built (2095
  entries); site rebuilt (`site/v19.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/2aGLUwHUzPnSpUDSGHPbnz (not watched: this remote session cannot watch artifacts).
- **2026-11-11 tool fixes:** (1) `build_index.py`: from Vol 17 on, terms end in their sub-heading (`| تمہید`) instead of
  a heading/main label; that text had become part of the index head and split one term into many heads. It is now
  dropped (Vol 17: 2636 → 2352 entries, Vol 18: 2751 → 2493; indexes rebuilt). (2) `mark_arabic.py` skips bare
  citation lines «(البقرہ آیت نمبر ۴۴)», a Hijri date line and two Urdu lines it used to wrap as Arabic; 6 such
  citations in Vol 18 unwrapped, two broken «…) تمت بالخیر» lines fixed, and «» inside three Vol 4 editor's notes
  changed to plain quotes (rule 9). Republish the Vol 17 and 18 previews when convenient.
- **Volume 18 (مفاسد گناہ) — done, awaiting the owner's review.** Folder `Vol 18 mafasid e gunah/`. PDF page =
  printed page + 1; text printed pp. 17–448 (14 sermons: استخفاف المعاصی 17, ترک المعاصی 29, ترجیح المفسدہ علی المصلحہ 48,
  مضار المعصیۃ 64, الجناح 85, الکاف 106, تیسیر الاصلاح 181, الجلاء للابتلاء 205, تفاضل الاعمال 268, حب العاجلہ 294,
  تادیب المصیبۃ 340, ازالۃ الغفلۃ 352, مراقبۃ الارض 378, التہذیب 419), all transcribed (files 0018, 0030, 0049, 0065, 0086,
  0107, 0182, 0206, 0269, 0295, 0341, 0353, 0379, 0420). `toc.tsv`: 8 rows set to the printed headings/pages, «تفسیر آیت»
  (p. 434) made a heading (logged). mark_arabic: DIFFERS 0, CITE 0 (two split ayah words joined; three closing du'a
  formulas kept in `quran-decisions.tsv`). Hadith check: `reports/vol18-hadith-check.md` (13 differs, all the book's
  wording). All corrections are in `reports/vol18-corrections.md` (incl. two misplaced/swapped couplet glosses on
  pp. 386 and 427, a dropped word in 9:24 on p. 396). More couplet, story and person terms in all volumes were unified.
  Index built (2751 entries); site rebuilt (`site/v18.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/Buh4KW3L16J8NdAGsqP1u9
- **Volume 17 (سنت ابراہیم، خطبات حج و قربانی) — done, awaiting the owner's review.** Folder `Vol 17 sunnat e ibrahim/`.
  PDF page = printed page + 1; text printed pp. 15–375 (13 sermons: سنت ابراہیم 15, تکمیل الانعام 54, عود العید 84,
  ترغیب الاضحیہ 92, الضحایا 103, السوال فی شوال 130, تعظیم الشعائر 164, الحج المبرور 183, تحصیل المرام 212, التہذیب 244,
  روح العج والثج 274, روح الارواح 315, احکام حج 359 (a رسالہ by عبد الکریم گمتھلوی, with ذوالحجہ, عید and قربانی
  rulings)), all transcribed (files 0016, 0055, 0085, 0093, 0104, 0131, 0165, 0184, 0213, 0245, 0275, 0316, 0360).
  The page after 375 is a publisher's advertisement, not transcribed. `toc.tsv` (339 rows): 17 headings and 30 start
  pages changed to follow the printed pages, a missing «تمہید» row added (logged). mark_arabic: DIFFERS 0, CITE 0 (the
  closing «وآخر دعوانا…» on p. 83 written as a quoted dua, logged). Hadith check: `reports/vol17-hadith-check.md`
  (15 differs reviewed, all the book's wording or already indexed as variants). All corrections applied under the
  owner's rule are in `reports/vol17-corrections.md` (incl. pp. 208–209 carrying misplaced الضحایا text, kept as
  printed). More couplet, story and person terms in all volumes were unified. Index built (2636 entries); site
  rebuilt (`site/v17.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/Fg647oVDjbFxeezgtzwc8w
- **Volume 16 (برکات رمضان) — done, awaiting the owner's review.** Folder `Vol 16 barakat e ramazan/`. PDF page =
  printed page + 1; text printed pp. 14–464 (11 sermons: تطہیر رمضان 14, تقلیل المنام بصورۃ القیام 37, روح القیام 71,
  روح الصیام 115, روح الافطار 164 (with the عرضداشت «نور الصدور» pp. 209–214), روح الجوار 215, فی خیر مقدم 266,
  التہذیب 336, مثلث رمضان 372, اکمال العدۃ 400, اکمال الصوم والعید 428), all transcribed (files 0014, 0037, 0071, 0115, 0164, 0215, 0266, 0336,
  0372, 0400, 0428). `toc.tsv`: the sermon after التہذیب renamed «مثلث رمضان» (the فہرست called it «احوال واقعی»,
  which is the compiler's preface heading); 18 headings/pages changed to follow the printed pages; three heading
  misreadings fixed (all logged). mark_arabic: DIFFERS 0, CITE 0 (7:56 quoted without «رحمت» on p. 191 and the
  abridged 56:83–87 on p. 192 kept as printed in `quran-decisions.tsv`). Hadith check: `reports/vol16-hadith-check.md`
  (22 differs reviewed, all the book's wording, kept). All corrections applied under the owner's rule are in
  `reports/vol16-corrections.md` (misprints, misplaced glosses, date mismatches ۱۳۳۳/۱۳۳۴ and ۱۳۳۶/۱۳۵۲, «طلحہ» for
  ابو طلحہ, editor's «لم اجد» notes for hadith that are in the collections). More couplet, story and person terms in
  all volumes were unified. Index built (2937 entries); site rebuilt (`site/v16.html`). Preview (private artifact,
  republish to the same URL): https://claude.ai/artifact/B37zqH2ZJod8wctC22izF2
- **Volume 12 (محاسن اسلام) — done, awaiting the owner's review.** Folder `Vol 12 mahasin e islam/`. PDF page = printed
  page + 1; text printed pp. 11–440 (7 sermons), all transcribed (files 0011, 0075, 0124, 0184, 0266, 0300, 0347).
  `toc.tsv` headings follow the page where the فہرست differs (4 headings; a missing «تمہید» row added; each change
  logged). mark_arabic: DIFFERS 0, CITE 0 (three unfilled ayah placeholders filled; 2:261 words split by a space in the
  reference were joined). Hadith check: `reports/vol12-hadith-check.md` (17 differs reviewed, all the book's wording,
  kept). All corrections applied under the owner's rule are in `reports/vol12-corrections.md`. Many couplet, story,
  hadith and person terms in all volumes were unified (e.g. half-couplets completed where the other half is printed,
  «وحدت الوجود» → «وحدۃ الوجود», duplicate names for the same story merged). Index built (2048 entries); all volume
  indexes and the site rebuilt (`site/v12.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/BVo1Hr4sb48E3wPhTN3Wfx
- **Volume 15 (تسلیم و رضا) — done, awaiting the owner's review.** Folder `Vol 15 tasleem o raza/`. PDF page = printed
  page + 1; text printed pp. 11–448 (13 sermons: ارضاء الحق حصہ اول 11, حصہ دوم 48, طریق القرب 113, وحدۃ الحب 137,
  الوصل والفصل 173, فناء النفوس 214, نشر الرحمۃ 262, التعرف بالتصرف 274, شکر السوانح 314, اعانۃ النافع 319,
  افنا المحبوب 351, قطع التمنی 385, النفحات فی الاوقات 411), all transcribed (files 0011, 0048, 0113, 0137, 0173,
  0214, 0262, 0274, 0314, 0319, 0351, 0385, 0411). `toc.tsv`: missing «تمہید» rows added (6), five headings changed to
  the page spelling and three page numbers corrected (all logged). mark_arabic: DIFFERS 0, CITE 0 (the 9:55/9:85 blend
  on p. 150 kept as printed in `quran-decisions.tsv`; three ayah pairs split into per-verse marks). Hadith check:
  `reports/vol15-hadith-check.md` (34 differs reviewed, all the book's wording, kept). All corrections applied under the
  owner's rule are in `reports/vol15-corrections.md` (displaced translations, head/signature date mismatches, variant
  couplets, probable misprints). More couplet, story and hadith terms in all volumes were unified. Index built (2248
  entries); site rebuilt (`site/v15.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/FHT1wWjKUabF45g4NAFTiB

- **Volume 14 (جزا و سزا) — done, awaiting the owner's review.** Folder `Vol 14 jaza o saza/`. PDF page = printed
  page + 1; text printed pp. 11–388 (9 sermons: جمال الجلیل 11, حیوۃ طیبہ 62, an untitled short sermon «سلسلہ اشرف
  المواعظ کا پہلا وعظ» 88, اجر الصیام من غیر انصرام 93 (with its ضمیمہ), المعرق والرحیق 146, انوار السراج 215,
  طلب الجنۃ 240, آثار الربیع 281, المودۃ الرحمانیہ 354), all transcribed (files 0011, 0062, 0088, 0093, 0146, 0215,
  0240, 0281, 0354). The pages after 388 are publishers' letters (back matter), not transcribed. `toc.tsv` (290 rows):
  three headings changed to the spelling on the page (logged). mark_arabic: DIFFERS 0, CITE 0 (48:2 and 28:76 words
  split by a space were joined). Hadith check: `reports/vol14-hadith-check.md` (1 differs: the closing colophon, kept).
  All corrections applied under the owner's rule are in `reports/vol14-corrections.md`. More couplet, hadith and story
  terms in all volumes were unified. Index built (1910 entries); all volume indexes and the site rebuilt
  (`site/v14.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/AZXgzaDvYSboxagLKqJv2J

- **Volume 13 (دعوت و تبلیغ) — done, awaiting the owner's review.** Folder `Vol 13 dawat o tabligh/`. PDF page = printed
  page + 1; text printed pp. 11–376 (8 sermons: الدعوت الی اللہ 11, آداب التبلیغ 63, التواصی بالحق 120, التواصی بالصبر 174,
  ضرورت تبلیغ 215, اتباع علماء 272, التبشیر 296, الاستقامت 340), all transcribed (files 0011, 0063, 0120, 0174, 0215,
  0272, 0296, 0340). `toc.tsv` from the فہرست; four missing «تمہید» rows added (logged). mark_arabic: DIFFERS 0, CITE 0
  (multi-verse blocks rejoined with ۝; 2:261 split words joined; the colophon «بحمد اللہ تم» added to the tool's
  signature list). Hadith check: `reports/vol13-hadith-check.md` (5 differs, all the book's spelling, kept). All
  corrections applied under the owner's rule are in `reports/vol13-corrections.md`. The sermon ضرورت تبلیغ also appears
  in Vol 4 (file 0406); its terms were matched to the Vol 4 ones and the place name «گجنیر» unified. Index built
  (1410 entries); all volume indexes and the site rebuilt (`site/v13.html`). Preview (private artifact, republish to
  the same URL): https://claude.ai/artifact/1ZMBsQuupvf5fFb3AzbX5w

- **Volume 11 (حقیقت تصوف و تقویٰ) — done, awaiting the owner's review.** Folder `Vol 11 haqiqat e tasawwuf o taqwa/`.
  PDF page = printed page + 1; text printed pp. 11–528 (11 sermons; the فہرست says 526, the last sermon runs to 528),
  all transcribed (files 0011, 0042, 0099, 0133, 0181, 0221, 0291, 0349, 0396, 0448, 0496). `toc.tsv` headings follow
  the page where the contents differ, and missing «تمہید» rows were added (each change logged). The note that pp. 104–314
  might have been typed without the scan in view was checked: pp. 169, 240 and 300 match the scans word for word.
  mark_arabic: DIFFERS 0, CITE 0 (p. 222 citation corrected to المائدہ ۵۴ تا ۵۶; p. 467 «قل لهم قولا بلیغا» completed
  to 4:63; two leftover placeholders filled). Hadith check: `reports/vol11-hadith-check.md` (25 differs reviewed;
  p. 20 «وغیر مستغنی» → «ولا مستغنی», the rest the book's wording, kept). All corrections applied under the owner's
  rule are in `reports/vol11-corrections.md`. More couplet, hikayat and hadith terms in all volumes were unified.
  Index built (2778 entries); site built (`site/v11.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/48SobrXHcLF1UnWJQzPZVV

- **Volume 10 (فضائل صوم و صلوٰۃ) — done, awaiting the owner's review.** Folder `Vol 10 fazail e saum o salat/`. PDF page =
  printed page + 1; text printed pp. 15–448 (12 sermons), all transcribed (files 0015, 0074, 0088, 0109, 0146, 0163,
  0196, 0269, 0313, 0334, 0391, 0419). `toc.tsv` headings follow the page where the contents differ (each change logged).
  mark_arabic: DIFFERS 0, CITE 0 (2:261 words split by a space in the reference were joined). Hadith check:
  `reports/vol10-hadith-check.md` (23 differs reviewed, all the book's wording, kept). All corrections applied under the
  owner's rule are in `reports/vol10-corrections.md`. More couplet, hadith, book and place terms in all volumes were
  unified (both halves; e.g. رامپور → رام پور). Index built (2584 entries); all volume indexes and the site rebuilt
  (`site/v10.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/T5c9XYPbqtkxx3jY52CXeP

- **Volume 9 (فضائل صبر و شکر) — done, awaiting the owner's review.** Folder `Vol 09 fazail e sabr o shukr/`. PDF page =
  printed page + 1; text printed pp. 13–488 (12 sermons), all transcribed (files 0013, 0042, 0105, 0136, 0177, 0204,
  0254, 0296, 0341, 0383, 0436, 0485). mark_arabic: DIFFERS 0, CITE 0 (2026-10-31: the colophon «بحمد اللہ تمام» is now
  skipped like «بحمد اللہ تمت»). Hadith check: `reports/vol09-hadith-check.md` (30 differs reviewed; p75 «اتفعل» →
  «ابفعل» corrected, the rest the book's wording, kept). All corrections applied under the owner's rule are in
  `reports/vol09-corrections.md`. Ayat terms use the canonical surah names (الاسراء → بنی اسرائیل، فصلت → حم السجدة).
  Many Persian/Arabic couplet terms in all volumes were completed to both halves. Index built (3053 entries); site
  built (`site/v09.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/MrrAbN4mJS6Vrq8JPSNFsz

- **Volume 8 (حقیقت مال و جاہ) — done, awaiting the owner's review.** Folder `Vol 08 haqiqat e mal o jah/`. PDF page =
  printed page + 1; text printed pp. 13–464 (10 sermons), all transcribed (files 0013, 0052, 0121, 0167, 0222, 0252,
  0288, 0330, 0378, 0424). mark_arabic: DIFFERS 0, CITE 0 (2026-10-31: `mark_arabic.py` now skips the author's
  signature/colophon lines «اشرف علی», «بحمد اللہ تمت»; Vols 4 and 7 output unchanged). Hadith check:
  `reports/vol08-hadith-check.md` (13 differs reviewed, all the book's wording, kept). All corrections applied under
  the owner's rule are in `reports/vol08-corrections.md`, including two places where the printed text is out of
  order (pp. 374–375 / 381 and p463), noted on the pages, not moved. Index built (2740 entries); site built
  (`site/v08.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/LfqwJPk7zXvchNGH8BAKGj

- **2026-11-11 fix (Vols 9, 14–19):** from Vol 14 on, `آیت:` terms had been written as `C:V` numbers (e.g. `2:197`),
  which the index sorted to the end and did not merge with surah-name heads. All 1113 were rewritten to the canonical
  surah name with Urdu digits (`البقرة ۱۹۷`), indexes of Vols 9 and 14–18 and the site rebuilt. New terms are written
  the same way (convert with `cv2name.py`-style rewrite before commit). Republish the previews when convenient.

- **2026-10-31 tool fix (all volumes):** `build_index.py` did not know surahs 88–114 or some name spellings
  (طٰہٰ، الاسراء، صٓ، المؤمن …), so their ayat sorted to the end of the ayat index. The surah list is now complete,
  names are matched without harakat, and every `آیت:` term in all volumes was rewritten to one canonical surah name
  (e.g. البقرۃ/البقرہ → البقرة، الاسراء → بنی اسرائیل، فصلت → حم السجدة). Indexes of Vols 1–7 and the site rebuilt;
  only the order and merging of ayat index heads changed. Republish the previews when convenient.

- **Volume 7 (حقیقت عبادت) — done, awaiting the owner's review.** Folder `Vol 07 haqiqat e ibadat/`. PDF page =
  printed page + 1; text printed pp. 17–520 (15 sermons), all transcribed (files 0017, 0042, 0105, 0129, 0207, 0248,
  0278, 0307, 0318, 0343, 0374, 0401, 0436, 0469, 0491). mark_arabic: DIFFERS 0, CITE 0 (one "keep" decision in
  `quran-decisions.tsv`, p316 → 21:83 kept as the book's prayer form). Hadith check: `reports/vol07-hadith-check.md`
  (27 differs reviewed; p236 corrected). All corrections applied under the owner's rule are in
  `reports/vol07-corrections.md`, including one faded-scan restoration (p417) for the owner to check. Index built
  (3144 entries); site built (`site/v07.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/DAtJBuTqXcdcAjgTNNRmRQ

- **Volume 6 (نظام شریعت) — done, awaiting the owner's review.** Folder `Vol 06 nizam e shariat/`. PDF page =
  printed page + 1; text printed pp. 10–496 (13 sermons), all transcribed (files 0010, 0051, 0087, 0122, 0174, 0194,
  0221, 0254, 0295, 0341, 0364, 0399, 0436). `toc.tsv` start pages corrected to the scans (e.g. تکمیل الاسلام 341).
  mark_arabic: DIFFERS 0, CITE 0. Hadith check: `reports/vol06-hadith-check.md` (20 differs reviewed). All
  corrections applied under the owner's rule are in `reports/vol06-corrections.md`. Index built (3142 entries); site
  built (`site/v06.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/GRaqubimEqhWwoXJptsMbB
  Name forms of people were unified across all volumes during Vol 6 (e.g. حضرت شاہ ولی اللہ محدث دہلویؒ،
  مولانا سعید احمد تھانویؒ، حضرت ابو بکر صدیقؓ، حضرت عائشہ صدیقہؓ، امام ابو حنیفہؒ، ابلیس).

- **Volume 5 (خطبات میلاد النبی) — done, awaiting the owner's review.** Folder `Vol 05 milad un nabi/`. PDF page =
  printed page + 1; text printed pp. 13–424 (9 sermons), all transcribed (files 0013, 0048, 0098, 0130, 0177, 0261,
  0294, 0324, 0371). mark_arabic: DIFFERS 0, CITE 0. Hadith check: `reports/vol05-hadith-check.md`. All corrections
  applied under the owner's rule are in `reports/vol05-corrections.md`. Index built (2851 entries); site built
  (`site/v05.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/EdbtzMHmPrHbWS1QdFoLcp

- **Volume 4 (حقوق و فرائض) — done, awaiting the owner's review.** Folder `Vol 04 huqooq o faraiz/`. PDF page =
  printed page + 1; text printed pp. 13–478 (13 sermons), all transcribed (files 0013–0455). mark_arabic: DIFFERS 0,
  CITE 0, DECIDED 1 (`quran-decisions.tsv`, p466 → 34:37). Hadith check: `reports/vol04-hadith-check.md`. All
  corrections applied under the owner's rule are in `reports/vol04-corrections.md`. Index built (3094 entries); site
  built (`site/v04.html`). Preview (private artifact, republish to the same URL):
  https://claude.ai/artifact/SfvJPWAzGEEn5YzpRY3Pay
  Note: stray letters ڏ ڵ ڮ ڛ (pause marks from a copied Qur'an text) inside ﴿…﴾ break the word-count match in
  mark_arabic; remove them before running it.

- **Volume 3 (دین و دنیا) — done, awaiting the owner's review.** Folder `Vol 03 deen o dunya/`. PDF page = printed
  page + 1; text printed pp. 14–440 (10 sermons), all transcribed (files 0015–0401). mark_arabic: DIFFERS 0, CITE 0,
  KEPT 1 (`quran-decisions.tsv`). Hadith check: `reports/vol03-hadith-check.md`. All corrections applied under the
  owner's rule are in `reports/vol03-corrections.md`. Index built (2642 entries); site built (`site/v03.html`).
  Preview (private artifact, republish to the same URL): https://claude.ai/artifact/Fch8oGW9Fm6G3mUsvEddjG
  2026-10-30: `mark_arabic.py` fragment search now tries every occurrence inside the ayah (Vols 1–2 unchanged).

- **Volume 2 (علم و عمل) — done, awaiting the owner's review.** Folder `Vol 02 ilm o amal/`. PDF page = printed
  page + 1; text printed pp. 14–440 (8 sermons), all transcribed. `toc.tsv` 253 rows. mark_arabic: DIFFERS 0,
  CITE 0 (citations corrected by hand during transcription). Hadith check: `reports/vol02-hadith-check.md`.
  Every correction applied under the owner's 2026-10-30 rule is in `reports/vol02-corrections.md` (sent to the owner
  for review; revert what the owner rejects). Index built (2308 entries); site built (`site/v02.html`).
  Preview (private artifact, republish to the same URL): https://claude.ai/artifact/UtFxdNVPTdhCQ4YXpunQMu
  (rebuild as for Vol 1, publish `<scratch>/art/v02.html`).
  2026-10-30: `mark_arabic.py` now accepts one-to-three-word ayah fragments that lie inside the ayah marked while
  transcribing (tafsir of single words), and treats نبود/باش as Persian; Vol 1 output verified unchanged.

- **Volume 1 (دنیا و آخرت)**: full text of printed pp. 13–456 done; index built (2241 entries); site built.
  All owner corrections to ayat and citations are applied (see `reports/vol01-quran-check.md`, last section).
  2026-10-29: index → page highlighting and return-to-index-position added to the site (owner's request).
  **Approved by the owner on 2026-10-29.**
- Vol 1 preview (private artifact, always republish to the same URL): https://claude.ai/artifact/BJf9yjkgpMPxrtyiVvyq5r
  Rebuild: `python3 -I tools/build_site.py <scratch>/art --artifact`, then publish `<scratch>/art/v01.html` to that URL.
- Branch: `claude/intelligent-rubin-6nl3vu` (push with `git push -u origin claude/intelligent-rubin-6nl3vu`).

## 2. Standing instructions from the owner (apply always)

**Working rules**
1. One volume at a time, in order — **but do not stop between volumes** (owner, 2026-10-30, second instruction):
   finish a volume, log its corrections, then go straight on to the next until all 32 are done. The owner reviews
   the logs afterwards and names any correction to revert.
1a. **No decisions are waited for.** Ayat, citations, ahadith and anything else that needs a decision: apply the
   correction yourself and record it in `reports/volNN-corrections.md` (one file per volume: page, kind, book had,
   applied, why). Items left as printed but doubtful are recorded there too ("kept"). Ask the owner only if work
   is truly impossible without him.
1b. After every context compaction, re-read `CLAUDE.md` and this file before continuing.
2. Do not stop to ask (rule 1a); decide, apply, and log.
3. Commit after every 10 pages (owner, 2026-11-07) and push to the branch above (`git pull --rebase` first). No pull request unless asked.
   Commit messages end with:
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and
   `Claude-Session: <the current session link>` (2026-11-12: use the link of the session doing the work). No model name elsewhere.
4. Scans may be under copyright: keep PDFs in this private repo; the public site gets **text only, no scans**.
5. GitHub account: the owner's personal account **iatasadduq**.

**Text**
6. Transcribe every page verbatim from the page images (no outside OCR), one block per printed page,
   format in `HANDOFF.md` §3 (`=== <pdf> | <printed>`, `#` khutbah title, `##` sub-heading, `## terms`).
7. Khutba-e-masura is **abbreviated**: `[خطبہ ماثورہ: اَلْحَمْدُ لِلّٰهِ نَحْمَدُهٗ وَنَسْتَعِیْنُهٗ ... اَمَّا بَعْدُ فَاَعُوْذُ بِاللّٰهِ مِنَ الشَّیْطٰنِ الرَّجِیْمِ۔ بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِیْمِ]`.
8. **Arabic and Persian lines are read from sharp, enlarged crops**: `python3 -I tools/zoom.py <pdf> <pdf page> <top> <bottom> out.png`
   (full-resolution page, 3×), never only from the reduced reading images.
9. Mark Arabic while transcribing: `﴿surah:ayah|text﴾` for ayat (the tool fills in the verified text) and `«…»` for
   hadith, dua, Arabic verse/sayings. Footnotes as `[حاشیہ: …]`. Editor's notes as `[حاشیہ: (از مرتب) …]`
   (use plain quotes "…" inside notes, not «»).
   Hand-marked ayat are re-checked by `mark_arabic.py` (fixed 2026-10-29: it used to skip any line already
   marked): matching ayat get the verified text; a differing wording becomes «…» and is listed under DIFFERS.
   Vol 2 corrections so far: see `reports/vol02-corrections.md` (p40, p95, p150 applied).

**Ayat (Qur'an) — owner's rule**
10. Ayat on the site use the verified Qur'an text (Indo-Pak script, `reference/`). Spelling-level differences
    are corrected automatically.
11. **Every place where the book's ayah wording differs from the Qur'an must be flagged to the owner** with the
    3 closest ayat (`DIFFERS` in the report). Nothing is changed until the owner decides. Decisions go in
    `<vol dir>/quran-decisions.tsv` (`keep`, or reference + the Qur'an words to put in) and are applied by the tool.
12. **Every citation that names the wrong surah/ayah** (`CITE` in the report) is flagged to the owner. Owner's
    decision for Vol 1 (apply the same way unless told otherwise): correct the citation in the text and add a note
    `[حاشیہ: (از مرتب) کتاب میں اس آیت کا حوالہ "…" درج ہے؛ … اس لیے حوالہ درست کر دیا گیا ہے۔]` on that page.
    Ask before applying it in a new volume only if a case is different in kind.
13. When the same words occur in several ayat, the reference follows the book's citation, else the ayah under
    discussion nearby. Never split one quotation into separate ayah pieces.

**Owner's rule from 2026-10-30 (overrides "wait for the owner" in rules 11–12 and 14):** do not stop for
decisions. Apply the correction yourself — DIFFERS: put in the ayah the book means (its citation, else the
closest ayah, alt 1); CITE: correct the citation and add the editor's note; ahadith: correct reading errors and
clear wording slips to the collection's text — and log every change in `reports/volNN-corrections.md`
(page, kind, book had, applied, why). At the end of the volume send the owner that log; revert whatever the
owner rejects (DIFFERS decisions also go in quran-decisions.tsv so they survive reruns).

**Ahadith**
14. At the end of each volume run the hadith check; check every `differs` item against the scan (zoomed);
    fix real reading errors; the book's own wording stays as printed. Report the results to the owner.
15. Ahadith, duas and other Arabic are shown in the **same Arabic font as ayat** (Scheherazade New).

**Index**
16. 10 separate sections. Labels per term: `| heading` (a book heading), `| main` (main subject of the passage),
    unlabeled = mention. Heading/main page numbers are shown in bold.
17. A hadith/dua whose Arabic is not on the page (only translation/meaning) is listed under the sub-entry
    «ترجمہ یا مفہوم (عربی متن اس صفحے پر نہیں)».

**Site**
18. Per volume: contents (فہرست) where every heading and sub-heading links to its page; one printed page at a
    time like the book (buttons, arrow keys, swipe, go-to-page); linked index with sticky category buttons and
    search; an "report an error" link on every page (`REPORT_URL` in `tools/build_site.py`, the planned public repo
    `iatasadduq/thanvi-khutbat-site`, which must exist with Issues on before the link works).
    Index page links carry a locator (`#p164~3.12.4`): the page opens with the term highlighted (ayah by its
    reference, hadith/verse as the whole passage, otherwise the matching words). Returning to the index (top-bar
    button, the "back to index" button or the browser's back) restores the spot the reader clicked from.

## 3. Sequence for each volume (do in this order)

1. Check the page offset (PDF page vs printed page) and transcribe the فہرست into `toc.tsv`.
2. Extract page images (`pdfimages -png`, then `python3 -I tools/halves.py <imgdir> <outdir> <first> <last>` for
   enhanced half-page images; read these, not the two-page pairs), transcribe in batches of ≈8 pages with labelled `## terms`,
   using zoomed crops for Arabic/Persian (rule 8) and the markup of rule 9. Commit + push each batch.
3. `bash tools/get_reference.sh` if `reference/` is missing.
4. `python3 -I tools/mark_arabic.py "<vol dir>" > reports/volNN-quran-check.md`, read it, then `--write`.
5. `python3 -I tools/check_hadith.py "<vol dir>" > reports/volNN-hadith-check.md`; verify `differs` items on the scan.
6. Apply DIFFERS/CITE/hadith corrections yourself (rule 1a): DIFFERS decisions in `quran-decisions.tsv`, citation
   notes on the page, hadith slips fixed; log all in `reports/volNN-corrections.md`; rerun step 4 with `--write`.
7. `python3 -I tools/build_index.py "<vol dir>/page-notes" "<vol dir>" "<vol dir>/toc.tsv"`;
   add the volume to `VOLUMES` in `tools/build_site.py`; `python3 -I tools/build_site.py site`; browser check;
   republish the preview.
8. Update this file (Status, Next steps), commit, push, and continue with the next volume (no waiting).
   Preview watches (2026-11-07): a session can watch at most 10 artifacts for comments sent to Claude. Keep the 10
   newest volume previews watched: after publishing a new volume's preview, stop watching the oldest
   (`ArtifactComments` watch `on: false`) and watch the new one. Now watched: Vols 9–18; Vols 1–8 are not.

## 4. Next steps

- Volume 22 (ذکر و فکر): done (see Status).
- Volume 23 (راہ نجات): done 2026-11-12/13 (see Status). Vol 23 work from p. 313 on was committed to the session
  branch `ccr-bb695273-iwt8zr` (based on `claude/intelligent-rubin-6nl3vu`); merge it into the main working branch.
- Volume 24 (موت و حیات): started 2026-11-13. Folder `Vol 24 maut o hayat/`. PDF page = printed page + 1 (425 PDF
  pages); text printed pp. 18–424 (10 sermons, title pages found by ink density and read from the scans: ذکر الموت 18,
  رجاء اللقاء 38, السوق لاہل الشوق 79, خیر الحیات و خیر الممات 170, دواء العیوب المعروف بہ شام خورشید 252, الجمعین بین
  النفعین 298, شوق اللقاء 359, احکام و مسائل متعلق موت 389, اشرف المواعظ (پہلا وعظ) 407, (دوسرا وعظ) 417). `toc.tsv`
  holds the sermon rows only (regenerate from page headings at the end, as for Vol 23). Page images: scratchpad
  `img24/` (all pages), half-pages `h24/` made for pdf 1–80 (`halves.py img24 h24 <first> <last>`). Corrections log:
  `reports/vol24-corrections.md`.
  Done: ذکر الموت pp. 18–37 (file 0019), رجاء اللقاء pp. 38–78 (file 0039). Next: السوق لاہل الشوق from p. 79 (pdf 80)
  in `0080.txt`.
- Environment note (2026-11-11): in a fresh container `python3 -I` may find a broken system Pillow; fix with
  `python3 -m pip install --break-system-packages --ignore-installed pillow`. `pdfimages -f/-l` numbers its output
  from 000, so rename to `p-<pdf page - 1>` before `halves.py`.
- The owner can review the corrections, Qur'an checks and hadith checks with `python3 -I tools/review_reports.py`; use the status filters to revisit decisions. Applying accepted edits or reverting rejected `page-notes/` changes remains a separate step.
- Question answering (RAG) over the books: revised plan in `RAG_PLAN.md` (2026-11-06), awaiting the owner's go-ahead;
  transcription stays the priority.
- Still open with the owner: the master heading list for the index (HANDOFF §2); creating the public site repo
  `iatasadduq/thanvi-khutbat-site` and turning on GitHub Pages (only after the owner approves).
