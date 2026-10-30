# PLAN — read this first (resume point for every new chat or after compression)

This file is the single source of truth for **what to do next and which rules apply**. It overrides older
statements in `HANDOFF.md` where they differ (HANDOFF §2–3 describe the state on 2026-10-28; §9–10 are current).
Update the **Status** and **Next steps** sections at the end of every working session and after every owner decision.

---

## 1. Status (2026-10-29)

- **Volume 2 (علم و عمل) — in progress.** Folder `Vol 02 ilm o amal/`. PDF page = printed page + 1; text runs
  printed pp. 14–440 (8 sermons). `toc.tsv` done (253 rows, from the فہرست on PDF pp. 9–14; the book's in-text
  sub-headings sometimes differ from it and are kept as `##`). Reading images: `tools/halves.py` (see §3 step 2).
  Transcribed so far: printed pp. 14–205 (sermons 1–2 complete; sermon 3 کوثر العلوم started p. 199).

- **Volume 1 (دنیا و آخرت)**: full text of printed pp. 13–456 done; index built (2241 entries); site built.
  All owner corrections to ayat and citations are applied (see `reports/vol01-quran-check.md`, last section).
  2026-10-29: index → page highlighting and return-to-index-position added to the site (owner's request).
  **Approved by the owner on 2026-10-29.**
- Preview (private artifact, always republish to the same URL): https://claude.ai/artifact/BJf9yjkgpMPxrtyiVvyq5r
  Rebuild: `python3 -I tools/build_site.py <scratch>/art --artifact`, then publish `<scratch>/art/v01.html` to that URL.
- Branch: `claude/intelligent-rubin-6nl3vu` (push with `git push -u origin claude/intelligent-rubin-6nl3vu`).

## 2. Standing instructions from the owner (apply always)

**Working rules**
1. One volume at a time. Finish a volume, show it to the owner, and wait for an explicit go-ahead before the next.
2. Ask the owner when something is genuinely unclear; otherwise follow these rules.
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
   Vol 2 decisions applied (owner, 2026-10-30): p40 → 6:107 «وما انت علیہم بوکیل» (quran-decisions.tsv);
   p95 citation الفلق ۳ → ۴ with editor's note. Open CITE: p150 book cites البقرة ۱۰۱ for 2:102 (show at step 6).

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
6. Send the owner the `DIFFERS` and `CITE` lists (with alternatives) and the hadith findings; wait; record the
   decisions in `quran-decisions.tsv` / apply citation notes; rerun step 4 with `--write`.
7. `python3 -I tools/build_index.py "<vol dir>/page-notes" "<vol dir>" "<vol dir>/toc.tsv"`;
   add the volume to `VOLUMES` in `tools/build_site.py`; `python3 -I tools/build_site.py site`; browser check;
   republish the preview.
8. Update this file (Status, Next steps), commit, push, and ask the owner for review/approval.

## 4. Next steps

- Volume 2: continue transcription from printed p. 206 (PDF 207), file `page-notes/0207.txt`, batches of 8 pages.
- Still open with the owner: the master heading list for the index (HANDOFF §2); creating the public site repo
  `iatasadduq/thanvi-khutbat-site` and turning on GitHub Pages (only after the owner approves).
