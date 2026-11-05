# PLAN — read this first (resume point for every new chat or after compression)

This file is the single source of truth for **what to do next and which rules apply**. It overrides older
statements in `HANDOFF.md` where they differ (HANDOFF §2–3 describe the state on 2026-10-28; §9–10 are current).
Update the **Status** and **Next steps** sections at the end of every working session and after every owner decision.

---

## 1. Status (2026-11-01; backward-pass update 2026-11-05)

- **Backward pass — Volume 31 (رحمت دو عالم) next (`agy/vol32-checks-and-site` / `kimi/volume-32-backwards`).** This branch is
  independent of the other AI's forward Volume 10 flow.
- **Volume 32 (فہرست خطبات حکیم الامت) — done, awaiting the owner's review.** Folder `Vol 32 fihrist/`. Volume 32 is a
  456-page master contents volume, not a sermon volume; PDF page = printed page + 1. `toc.tsv` records its major
  sections. All printed pp. 1–456 (PDF pp. 2–457) transcribed in 8-page batches (`0002.txt`–`0456.txt`); continuous
  coverage, unique page markers, page mapping and `## terms` validated across all 456 pages. Contents tables get
  high-level terms only, so their page references are not confused with sermon locations. `mark_arabic.py` (updated to
  skip tab-separated table rows): DIFFERS 0, CITE 0 (`reports/vol32-quran-check.md`). Hadith check:
  `reports/vol32-hadith-check.md` (differs 0). All corrections applied from zoomed scans are logged in
  `reports/vol32-corrections.md`. Index built (587 entries, 1175 locators); Volume 32 added to `VOLUMES` and site built
  (`site/v32.html`, `site/index.html`). Next on the backward pass: Volume 31 (`Vol 31 rehmat e do aalam/`).

- **Volume 10 (فضائل صوم و صلوٰۃ) — in progress.** Folder `Vol 10 fazail e saum o salat/`. PDF page = printed page + 1;
  page images in the scratchpad (`v10/h`). `toc.tsv` built (12 sermons, headings follow the page where the contents
  differ; each change logged). Transcribed: الصلوٰۃ (0015), نداء رمضان (0074), الصوم (0088), الصیام (0109), الفطر (0146),
  النسوان فی رمضان (0163), رمضان فی رمضان (0196), احکام العشر الاخیرہ (0269), printed pp. 15–312. Next: تطہیر رمضان (p. 313),
  عصم الصنوف 334, التہذیب نمبر ۱ 391, التہذیب نمبر ۲ 419. Corrections in `reports/vol10-corrections.md`.

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
3. Commit after every batch (≈8 pages) and push to the branch above. No pull request unless asked.
   Commit messages end with:
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and
   `Claude-Session: https://claude.ai/code/session_015uM8b6tEpHrmFhzz1XdWLQ`. No model name elsewhere.
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

## 4. Next steps

- Backward pass (separate branch `agy/vol32-checks-and-site` / `kimi/volume-32-backwards`): Volume 32 is complete (pp. 1–456 transcribed, checked, indexed, and built into `site/v32.html`). Next: start **Volume 31 (`Vol 31 rehmat e do aalam/`)** following §3 steps 1–8 (check PDF vs printed page offset, transcribe فہرست into `toc.tsv`, extract page images, transcribe in ~8-page batches with zoomed crops for Arabic/Persian, run `mark_arabic.py` and `check_hadith.py`, log corrections in `reports/vol31-corrections.md`, build index and site). Do not change or wait on the other AI's Volume 10 flow.
- Volume 10: continue from تطہیر رمضان (printed p. 313, new file `0313.txt`) to the end of the volume, logging corrections in `reports/vol10-corrections.md`; at the end run the §3 pipeline and add Vol 10 (`فضائل صوم و صلوٰۃ`, `Vol 10 fazail e saum o salat`) to VOLUMES.
- The owner will review `reports/vol02-corrections.md` … `reports/vol09-corrections.md` at leisure; revert anything the owner rejects.
- Still open with the owner: the master heading list for the index (HANDOFF §2); creating the public site repo
  `iatasadduq/thanvi-khutbat-site` and turning on GitHub Pages (only after the owner approves).
