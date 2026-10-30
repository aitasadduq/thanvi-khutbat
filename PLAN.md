# PLAN — read this first (resume point for every new chat or after compression)

This file is the single source of truth for **what to do next and which rules apply**. It overrides older
statements in `HANDOFF.md` where they differ (HANDOFF §2–3 describe the state on 2026-10-28; §9–10 are current).
Update the **Status** and **Next steps** sections at the end of every working session and after every owner decision.

---

## 1. Status (2026-10-30)

- **Volume 5 (خطبات میلاد النبی) — in progress.** Folder `Vol 05 milad un nabi/`. PDF page = printed page + 1;
  text printed pp. 13–≈424 (9 sermons: الظہور 13, السرور 48, النور 98, نور النور 130, المورد الفرسخی 177,
  راس الربیعین 261, المریع فی الربیع 294, الرفع والوضع 324, نقد اللبیب 371). `toc.tsv` done (226 rows). Reading images:
  `<scratch>/v05/h/NNN{a,b}.png`. Corrections log: `reports/vol05-corrections.md`. Transcribed so far: pp. 13–49 (sermon 1 complete, file 0013; sermon 2 السرور begun in 0048).

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

- Volume 5: continue transcription from printed p. 50 (PDF 51, sermon 2 السرور) in `page-notes/0048.txt`; new file at
  each sermon start (0048, 0098, 0130, 0177, 0261, 0294, 0324, 0371); then the §3 sequence, then Volume 6 and onward —
  no stopping between volumes.
- Owner will review `reports/vol02-corrections.md` (and later logs) at leisure; revert anything he rejects.
- Still open with the owner: the master heading list for the index (HANDOFF §2); creating the public site repo
  `iatasadduq/thanvi-khutbat-site` and turning on GitHub Pages (only after the owner approves).
