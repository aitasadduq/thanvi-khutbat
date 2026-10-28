# Handoff: Urdu index and full text of *Khutbat-e-Hakeem-ul-Ummat*

Written 2026-10-28 at the end of the first working session. Read this whole file before starting work.

## 1. The project

The owner (Imran) has 32 volumes of Maulana Ashraf Ali Thanvi's speeches (*Khutbat-e-Hakeem-ul-Ummat*). They are scanned Urdu books in Nastaliq script, about 14,400 pages in all. The goal is:

1. **Full text** of every page, transcribed by Claude from the page images, one page at a time with page markers.
2. **A back-of-book index** for every volume, merged into one master index. It has 10 separate sections (see §4).
3. **A free website on GitHub Pages.** It shows the books as text, not images. Each page number in the index links to that page of that volume. Entries where the term is a heading or the main topic are marked (see §5).

## 2. Decisions already made by the owner

| Topic | Decision |
|---|---|
| Source files | Use the PDFs in `scanned_version/` (named `Khutbaat-i-Hakeem-ul-Ummat-Vol-NN.pdf`). These are the same scans as the older copies, which the owner has deleted, but without the ahlehaq.org watermark. No better scans exist. |
| How the text is made | Full-text transcription by Claude, the same way as pages 13–44 of Volume 1 (§3). No outside OCR software. |
| Index sections | Keep all 10 sections separate, as in the pilot. |
| Hosting | GitHub, using GitHub Pages. No paid domain or hosting. Use the owner's **personal** GitHub account, username **iatasadduq** (email iatasadd@alumni.uwo.ca), not the company account. The project repository is the private repo `iatasadduq/thanvi-khutbat`. `GITHUB_SETUP.md` has the setup steps. |
| Source of scans | The archive.org item `Maktaba-Hakeem-ul-Ummat-Maulana-Ashraf-Ali-Thanvi-ra`, files `Khutbaat-i-Hakeem-ul-Ummat-Vol-NN.pdf` (01–32). Download URL: `https://archive.org/download/Maktaba-Hakeem-ul-Ummat-Maulana-Ashraf-Ali-Thanvi-ra/<file>`. The item also has archive.org's own OCR (`_djvu.txt`), but it was checked and is **unusable** for this Nastaliq text, mostly garbled. Don't rely on it. As of 2026-10-28, `scanned_version/` holds **all 32 volumes** (Vol-01 to Vol-32, about 760 MB). File sizes match archive.org's records, and page counts match the older copies. |
| Website content | The books are shown as text, not images. |
| Fonts | Urdu text in **Noto Nastaliq Urdu** (Google Fonts). Arabic quotations and ayat in **Amiri**. Avoid Jameel Noori Nastaleeq, because its licence for web use is unclear. |

**Still open, so ask the owner:**
- Index headings. In the pilot, Claude grouped topics under broader headings it chose itself. For example, the book's sub-heading ثمرۂ نیت went under **ارادہ**, and the topic of the passage on pp. 27–28 was named **بدنظری** where the text says نظر بد. Variant headings were also merged. The proposal is to draft one **master heading list** from the pilot, have the owner approve it, and use it for all 32 volumes.
- Whether the khutba-e-masura (the standard Arabic opening sermon) is transcribed in full or abbreviated. The pilot abbreviated it as `[خطبہ ماثورہ: الحمد للہ … ]`.
- Whether each text page on the website also links to its original scan.

## 3. What is already done (Volume 1, دنیا و آخرت)

Everything is in `Index pilot - 01 dunya o akhiret/`.

- **`page-notes/*.txt`** holds one block per printed page, covering printed pp. 13–456 (PDF pp. 14–457). Each file covers about 8 pages and is named after its first PDF page.
  - **Files `0014`, `0021`, `0027`, `0033` and `0039` contain the full verbatim text** of the first khutbah, **المراد**, printed pp. 13–44. This is the full-text work already done. Don't redo it, though it should be proofread.
  - **Files `0046` to `0447` contain only a one-line `خلاصہ` (summary) plus index terms** for each page. They do **not** contain full text. Those pages (printed 45–456) still need full transcription.
- **`toc.tsv`** is Volume 1's فہرست (contents list) transcribed: khutbah, heading, printed page.
- **`index.json` / `index.html`** is the pilot index: about 1,730 entries and 3,129 page references, built by `tools/build_index.py`. It is published privately at https://claude.ai/artifact/FA9UxnPJ5yCVvLot7ZHJjK
- **`tools/pairs.py`** crops page images and stitches them two per image for reading. **`tools/build_index.py`** builds the index.

### Page-note format (keep exactly this format)

```
=== <pdf_page> | <printed_page>
# <the book's own heading, when one starts on this page>
<full verbatim text of the page; Quran/Arabic as printed; Persian couplets as "line 1 / line 2" followed by the Urdu gloss in parentheses>
[حاشیہ: <footnote text>]
## terms
موضوع: <heading> > <sub-heading>
آیت: <surah name> <ayah no. in Urdu digits> > <short Arabic text>
حدیث: <short Arabic or Urdu text>
شخصیت: <name with honorific and ؒ/ؓ/علیہ السلام>
حکایت: <one-line description of the story>
مثال: <the analogy>
مقام: <place>
کتاب: <book>
شعر: <first line> (<poet>)
قول: / قاعدہ: <saying or maxim>
```

Index terms are written **only** under `## terms`. Heading lines (`#`) record where the book's own sub-headings fall. They are needed for the main-topic marking in §5.

### Volume 1 page numbering
PDF page = printed page + 1. Check this for **each** new volume, because the offset may differ.

## 4. Index design (from `tools/build_index.py`)

There are 10 sections: موضوعات، آیات قرآنی (in surah order)، احادیث و ادعیہ، شخصیات، حکایات و واقعات، تمثیلات، مقامات، کتب، اشعار، اقوال و قواعد.
- Entries are sorted in Urdu alphabetical order. People are sorted ignoring honorifics (حضرت، مولانا، شاہ…), with listed exceptions such as شاہ جہان.
- Pages that run on are collapsed into ranges (۲۵–۲۸). All digits are in Urdu.
- The `MERGE` and `PEOPLE_MERGE` dictionaries list which variant headings are folded together. Extend them for each volume, and later replace them with the approved master heading list.
- Each locator is a **printed** page number. For the master index the locators become volume:page.

## 5. Website plan (not started)

- A static site on GitHub Pages, served from the public repo. For the website it needs **only the text**, not the PDFs.
- Each volume is a set of web pages of text. Every printed page has an anchor (e.g. `v01.html#p25`), and index links point to those anchors.
- **Main-topic marking:** each reference is labelled `heading` (the term is a heading in the book), `main` (discussed at length) or `mention` (a passing reference). Headings and main discussions show as **bold** page numbers. The pilot did not record this label yet, so add it during transcription.
- The index has a search box, as in the pilot page. Full-text search over all volumes comes later.

## 6. How to transcribe a volume (the workflow used in the pilot)

1. Extract the page images: `pdfimages -j "<volume>.pdf" <outdir>/p` (or `-png` for the JPEG2000 files in `scanned_version`).
2. Crop and stitch them two pages per image: `python3 -I tools/pairs.py <imgdir> <outdir> <n_pages>`. Each image is labelled "PDF n".
3. Read the page images and write `page-notes/NNNN.txt` in the format above, about 8 pages per file. Transcribe verbatim and keep the original spelling. Skip the running page number and the footer.
4. After each volume, rebuild the index: `python3 -I tools/build_index.py <page-notes dir> <out dir> <toc.tsv>`.
5. Check the coverage. Every printed page should have exactly one `===` block, with no gaps.

Quality notes:
- The scans are only 96 dpi, so read the Arabic and Persian carefully.
- Suggest that the owner spot-checks each volume, especially the quotations.

## 7. Cloud / repository setup (for working in a cloud session)

- A cloud session works from a GitHub repository, so the PDFs must be in the repo it clones. Each `scanned_version` PDF is about 25 MB, well under GitHub's 100 MB per-file limit. All 32 together come to roughly 0.8–1 GB, which is acceptable.
- Suggested layout:
  - a **private** repo holding the PDFs, page-notes and tools, because the scans may be under the publisher's copyright
  - a **public** repo with only the generated text and index pages for GitHub Pages
- Commit the page-notes after every batch, so that no work is lost if a session ends.

## 8. Next steps, in order

1. Confirm the volume list and the page offset for each PDF in `scanned_version/`.
2. Ask the owner about the open questions in §2, starting with the master heading list.
3. Transcribe the full text of Volume 1, pp. 45–456. The existing summaries and terms can serve as a cross-check. Add the heading/main/mention label to each term.
4. Continue with Volumes 2–32, one volume at a time, and commit after every batch.
5. Build the merged master index and the GitHub Pages site.

## 9. Session 2 (2026-10-28): website started

Owner's decisions this session:
- Build the site for **Volume 1 only** first; the owner reviews it before work moves to Volume 2.
- The site shows the **contents list (فہرست)** of each volume: every khutbah heading and sub-heading is a link to its page.
- Reading view: **one printed page at a time**, like the book (Next/Previous buttons, arrow keys, swipe, go-to-page box).
- Order: build the site first with what exists, then transcribe pp. 45–456 in batches and rebuild after each batch.
- Khutba-e-masura stays **abbreviated**. **No scans** on the site.

How the site is built:
- `python3 -I tools/build_index.py "<vol dir>/page-notes" "<vol dir>" "<vol dir>/toc.tsv"` (refreshes index.json)
- `python3 -I tools/build_site.py site` writes `site/index.html` (volume list) and `site/v01.html`.
  Add each new volume to `VOLUMES` in `tools/build_site.py`.
- `v01.html` routes on the hash: `#contents`, `#index`, `#p25` (printed page), `#h7` (row 7 of toc.tsv).
- Pages with only a `خلاصہ` show the summary with a notice that the full text is pending.
- Preview for the owner (private artifact): https://claude.ai/artifact/BJf9yjkgpMPxrtyiVvyq5r
  (rebuild with `--artifact` into a scratch folder and republish to the same URL).
