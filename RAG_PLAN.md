# Plan: "Ask the Khutbat" — question answering over *Khutbat-e-Hakeem-ul-Ummat*

Revised plan, 2026-11-06. It replaces the earlier draft `rag_implementation_plan.md` (reviewed in the 2026-11-06
session; the changes are listed in §11). It does not change any rule in `PLAN.md`; transcription stays the first
priority, and nothing here touches the page-note format.

---

## 1. Goal

Readers ask a question in Urdu, English or Roman Urdu and get:

1. **Sources first:** the most relevant passages from the transcribed volumes, each with a link that opens the
   page on the reading site with the passage highlighted.
2. **An answer (optional layer):** a short answer written by an LLM **only from those passages**, in the reader's
   language, where every statement carries a citation such as [جلد ۲، ص ۱۶](v02.html#p16~…) and every quotation
   has been checked against the source.

When the LLM is unavailable or over its quota, the sources still appear and the feature works as search.

## 2. Principles

1. **$0 a month, few moving parts.** Build everything offline in the repo or in GitHub Actions. Run at most one
   small server for the LLM layer. No hosted database.
2. **The book's index first.** The 10-section index, the `heading`/`main`/`mention` labels, `toc.tsv` and the ayah
   references in `﴿surah:ayah|…﴾` are hand-made and precise; use them as retrieval signals alongside text search.
3. **Citations made by code, not by the model.** The model cites numbered excerpts; the server writes the links
   and drops anything it cannot back with an excerpt.
4. **One parser.** The RAG build and the site build read page-notes with the same code, so they never disagree.
5. **Measured, not guessed.** Weights and model choices are set from an evaluation set (§8).
6. **Honest coverage.** Every answer says which volumes were searched (now 1–11 of 32).

## 3. Current data (what the plan builds on)

| Source | Where | Notes |
|---|---|---|
| Page text | `<vol dir>/page-notes/*.txt` | `=== <pdf> \| <printed>` blocks, `#` sermon title, `##` sub-heading, `## terms`. 11 volumes, 5,069 pages so far; about 14,400 when all 32 are done. |
| Index terms | `## terms` lines in page-notes | 10 types (موضوع، آیت، حدیث، شخصیت، حکایت، مثال، مقام، کتاب، شعر، قول/قاعدہ), label `\| heading`, `\| main` or none (mention). |
| Built index | `<vol dir>/index.json` | Per section a list of `{head, pages, strong, subs}`. Keeps only "strong" vs not; the heading/main split must come from page-notes. |
| Contents | `<vol dir>/toc.tsv` | `خطبہ / عنوان / صفحہ`. |
| Ayat | `﴿15:1\|…﴾` in the text | Exact surah:ayah references, verified by `mark_arabic.py`. |
| Normalisation | `tools/build_index.py` | `TYPE_MAP`, `MERGE`, `PEOPLE_MERGE`, `FOLD`, `STRIP`. |
| Highlight links | `tools/build_site.py` | `#p<page>~<locator>` opens the page with words highlighted (block + word span). |

Volume 32 is not transcribed; it is not used until it is.

## 4. Architecture

```
                         OFFLINE (repo / GitHub Actions, on every push)
page-notes + toc.tsv ──► tools/khutbat_data.py (shared parser) ──► rag/build.py
                                                                     │
          ┌───────────────────────────┬──────────────────────────────┼─────────────────────────┐
          ▼                           ▼                              ▼                         ▼
   passages.jsonl              lexical index                 heads.jsonl                 vectors (int8)
 (chunks + page spans,      (BM25, Urdu tokenizer)    (all index heads + subs,     passages.npy, heads.npy
  sermon, terms, ayat)                                 pages, depth labels)         (bge-m3, 1024-d)

                                     ONLINE
 Static site (GitHub Pages) ── Phase 1: in-browser search over passages + heads (no server)
        │
        └── Phase 3: "سوال پوچھیں" drawer ──► API on a Hugging Face Space (FastAPI)
                                              1. route  2. retrieve (3 lists) → fuse → rerank
                                              3. LLM answer from top 4–6 passages
                                              4. map [n] → links, verify quotations
```

## 5. Data artifacts

### 5.1 Passages (`rag/data/passages.jsonl`)

Chunks of about 250–400 words, split at `#`/`##` headings so a chunk never spans two sermons, allowed to cross a
page break (then it records every page it covers). Footnotes `[حاشیہ: …]` stay with their page.

```json
{
  "id": "v02-0016-a",
  "vol": 2,
  "vol_title": "علم و عمل",
  "pages": [16, 17],
  "sermon": "الفاظ القرآن",
  "subheading": "تلاوت فرض کفایہ ہے",
  "text": "سو میں نے اس وقت ذکر قرآن کو مقدم کیا ہے۔ …",
  "ayat": ["15:1", "27:1"],
  "terms": [
    {"type": "موضوع", "head": "تلاوت قرآن", "sub": "فرض کفایہ", "depth": "heading", "page": 16},
    {"type": "موضوع", "head": "تجوید", "sub": "صحت و تجوید سے غفلت", "depth": "main", "page": 16}
  ],
  "sermon_meta": {"place": "کیرانہ", "date_hijri": "۲۳ شعبان ۱۳۳۴ھ"},
  "hash": "md5 of text"
}
```

- `text` keeps the verified Arabic. The `﴿ref|` wrapper is removed and the reference goes to `ayat`.
- The embedding input is `sermon | subheading | text`, not the whole term list, so passages don't all look alike to
  the model.
- `sermon_meta` comes from the first page of each sermon when it states place and date (optional, best effort).

### 5.2 Index heads (`rag/data/heads.jsonl`)

One row per index head and sub-entry across all volumes, with the merged form from `MERGE`/`PEOPLE_MERGE`:

```json
{"type": "حکایت", "head": "انگریز نے حمائل رومال سے پکڑی …", "sub": "",
 "refs": [{"vol": 2, "page": 17, "depth": "main"}, {"vol": 2, "page": 18, "depth": "main"}]}
```

About 30,000 rows when all volumes are done. These are searched by text and by vector (§6, list C), so a reader's
own wording ("love of Allah", «اللہ سے محبت») can reach a head written as «محبت الٰہی».

### 5.3 Sizes

At 14,400 pages and roughly 2 passages a page: about 30k passage vectors and 30k head vectors, 1024-d, int8
≈ 60 MB together. That fits in memory on any free host and is fast to search with numpy, so no vector database
is needed.

## 6. Retrieval

### 6.1 Normalisation (shared by indexing and queries)

`FOLD` + `STRIP` from `build_index.py`, plus: remove ZWNJ/ZWJ and tatweel, unify spacing variants
(کیلئے → کے لیے، اسلئے → اس لئے، چاہئے/چاہیے), Urdu and Arabic digits to ASCII for references, and a small
stop-word list (the `STOP` set in `build_site.py`).

### 6.2 Query routing (no LLM by default)

1. **Ayah reference** (`2:183`, `البقرة ۱۸۳`, "Baqarah 183"): look up `ayat` directly.
2. **Volume/page or sermon title**: open it directly.
3. **Roman Urdu** (Latin script plus common Urdu words): transliterate to Urdu with one small LLM call, since bge-m3
   handles Roman Urdu poorly. Urdu and English queries go straight to retrieval; bge-m3 matches English questions to
   Urdu text.

### 6.3 Three ranked lists

- **A. Lexical:** BM25 over passages, with the tokenizer above.
- **B. Dense:** bge-m3 cosine over passage vectors.
- **C. Index heads:** BM25 + dense over `heads.jsonl`. Every passage on a page that a matching head points to gets
  that head's rank. A sub-entry match counts more than a head-only match.

### 6.4 Fusion and ranking

1. Weighted reciprocal-rank fusion of A, B and C (start at equal weights, k = 60).
2. Depth as a small bonus, used to break near-ties: `heading` > `main` > mention > no term. It is never a penalty,
   because a passage with a passing mention can still be the best answer.
3. If the query names a category ("story", «حکایت», "parable"), boost passages carrying a term of that type.
4. Optional: rerank the top 30 with `BAAI/bge-reranker-v2-m3` (multilingual, runs on CPU), if §8 shows it helps.
5. Keep the top 4–6 passages, at most 2 from the same sermon, so that one long sermon doesn't fill the answer.

All weights are set from the evaluation set (§8), not by hand.

## 7. Answer generation

### 7.1 Prompt

```text
You answer questions about "Khutbat-e-Hakeem-ul-Ummat", the sermons of Maulana Ashraf Ali Thanvi رحمہ اللہ.
Use ONLY the numbered excerpts below.

1. Answer in the language of the question. In English keep key terms in Urdu/Arabic in parentheses.
2. After every statement cite its excerpt as [1], [2] … Cite nothing else; do not write links.
3. Quote Arabic and Urdu exactly as in the excerpt, inside «…» (or ﴿…﴾ for ayat).
4. If the excerpts do not answer the question, say so plainly. Do not use outside knowledge.
5. Report what Hazrat Thanvi says in these sermons. Do not issue rulings (fatwa).

Searched: volumes {coverage}.
[1] جلد ۲، ص ۱۶–۱۷ | الفاظ القرآن > تلاوت فرض کفایہ ہے
<text>
…
```

### 7.2 Post-processing on the server

1. Replace each `[n]` with the link of excerpt *n*: `[جلد ۲، ص ۱۶](v02.html#p16~<locator>)` (Urdu) or
   `[Vol. 2, p. 16](…)` (English). The locator is computed with the same code as the site's index links, so the
   page opens with the passage highlighted.
2. Drop citations to excerpts that were not sent.
3. Check every «…»/﴿…﴾ quotation: after normalisation it must occur in the cited excerpt. If it doesn't, replace it
   with the excerpt's own words or remove it, and log the case.
4. Add the fixed notes: «یہ فتویٰ نہیں؛ کسی مستند عالم سے رجوع کریں» and «تلاش شدہ: جلد ۱–۱۱».

### 7.3 Models

- The model name and provider are config, not code. Free tiers (Google AI Studio, Groq, others) and their
  limits change often; check them at deployment time. Use one primary and one fallback; on HTTP 429 or a
  timeout, use the fallback; if both fail, return the sources without an answer.
- Urdu takes several times more tokens than English, so the binding limit is usually **tokens per day**, not
  requests. Keep the context at 4–6 passages (about 2–3k words) and the answer short.
- Prompts sent to a free tier may be used by the provider to improve its products. Say so on the page.
- Stream the answer; show the sources before the answer arrives.

## 8. Evaluation (`rag/evaluate.py`)

### 8.1 Retrieval test set, generated from the index

- **Stories and parables:** each حکایت/مثال description, rephrased in Urdu and translated into English by an LLM
  once (stored in the repo), is a query whose answer pages are known. List C is switched off for this test so the
  index does not find its own entries.
- **People:** spelling and honorific variants of names in `شخصیات`.
- **Ayat:** references in several forms (`2:183`, «البقرة ۱۸۳», "Surah Baqarah verse 183").
- **Topics:** broad heads (صبر، ریاء، تجوید): pages labelled `heading`/`main` should rank above mentions.

Report Recall@5 and MRR for each list (A, B, C) and for the fused result, per language.

### 8.2 Hand-written set

About 60 questions written by a person (20 Urdu, 20 English, 20 Roman Urdu), with expected pages, including:

- "Why is reciting the whole Qur'an fard kifayah while learning Fatiha is wajib?" → Vol 2 p. 16;
- the Englishman who read الٓمّٓ as "alu" → Vol 2 pp. 17–18;
- questions the volumes don't answer (the expected answer is "not found").

### 8.3 Answer checks

For the hand-written set:

- every sentence has a citation;
- every citation's excerpt supports the sentence (judged by an LLM, then spot-checked by hand);
- every quotation passes §7.2 step 3;
- refusal is correct on the "not found" questions.

**Launch gate:** Recall@5 ≥ 0.9 on generated stories and ayat, ≥ 0.8 on the hand-written set, no unverified
quotation shown to a reader.

## 9. Phases

### Phase 0 — Shared parser (prerequisite)

- Move the page-note and term parsing out of `tools/build_index.py` into `tools/khutbat_data.py`, as functions:
  `read_pages(vol_dir)`, `parse_terms(lines)`, `normalise(s)`, plus `MERGE`, `PEOPLE_MERGE`, `TYPE_MAP`.
- `build_index.py` and `build_site.py` import it. Check: every volume's `index.json` and every `site/vNN.html` is
  byte-identical before and after.
- Expose the highlight-locator function from `build_site.py` so the RAG code can make the same links.

### Phase 1 — Search on the static site (no server, no keys)

- `rag/build.py` writes `passages.jsonl` and `heads.jsonl` for all finished volumes.
- Add a search page to the site: lexical search (lists A and C, text only) in the browser, over a compact JSON
  or MiniSearch-style index served as a static file (a few MB, gzipped), loaded on demand.
- Results show the passage, its sermon/sub-heading, matching index terms as badges, and a highlight link.
- This is the "full-text search" already planned in `HANDOFF.md` §5, and it stays useful even if the LLM layer is
  never deployed.

### Phase 2 — Vectors and evaluation (offline)

- Embed passages and heads with bge-m3 (`FlagEmbedding` or `sentence-transformers`), store int8 `.npy` files and
  hash-keyed caches so that only changed passages are embedded again.
- A GitHub Action rebuilds the data on every push that touches page-notes, `toc.tsv` or `MERGE`. Vectors are
  published as release assets or to the Space, not committed to git.
- Build the evaluation sets (§8.1, §8.2) and tune the fusion weights. Decide whether the reranker earns its place.

### Phase 3 — Answer API

- `rag/app.py`: FastAPI on a free Hugging Face Space (CPU). Loads the data at start, embeds the query, runs §6–§7.
- Endpoints: `POST /search` (sources only) and `POST /ask` (sources + streamed answer).
- Protection:
  - CORS limited to the site's domain;
  - Cloudflare Turnstile on `/ask`;
  - per-IP rate limit;
  - cache of answers to repeated questions;
  - keys only in Space secrets.
- The Space sleeps when idle. The drawer shows «سرور بیدار ہو رہا ہے…» and falls back to Phase 1 search if
  the API doesn't answer in time.
- Log questions (no IP addresses) to improve the evaluation set.

### Phase 4 — "سوال پوچھیں" drawer on the site

- A button in the top bar of `index.html` and every `vNN.html`. The drawer is RTL for Urdu and LTR for English,
  chosen from the text typed.
- Answer, then collapsible source cards («ماخذ») with the passage text and term badges.
- On the volume page a citation link jumps to the page through the existing hash router; elsewhere it opens
  `vNN.html#p…~…`.
- Each answer has a "report a wrong answer" link (same pattern as the page error link, `REPORT_URL`).
- **Launch after the owner has approved the public site** (`PLAN.md` §4) and the gate in §8.3 is met.

## 10. Files to add

```text
tools/
  khutbat_data.py      shared page-note / term parser and normalisation (Phase 0)
  build_index.py       existing — imports khutbat_data
  build_site.py        existing — imports khutbat_data; search page (P1) and drawer (P4)
rag/
  build.py             passages.jsonl, heads.jsonl, lexical index, browser search index (P1)
  embed.py             bge-m3 vectors with hash cache (P2)
  retrieve.py          routing, lists A/B/C, fusion, rerank (P2)
  answer.py            prompt, model calls with fallback, citation mapping, quote check (P3)
  app.py               FastAPI for the Hugging Face Space (P3)
  evaluate.py          test-set generation and scoring (P2)
  eval/                generated and hand-written questions with expected pages
  requirements.txt
.github/workflows/rag.yml   rebuild data on push (P2)
```

Generated data (`rag/data/`, vectors) is not committed; it is built by the workflow.

## 11. Changes from the earlier draft

| Earlier draft | This plan | Why |
|---|---|---|
| Qdrant Cloud for vectors and sparse search | numpy + BM25 files built in CI | Data is ~60 MB; a free cluster can be suspended when idle; one service and key fewer. |
| Cloudflare Worker or HF Space | HF Space only | The Python embedding and rerank stack doesn't run in a Worker. |
| Gemini 1.5 Flash + Groq Llama-3.3-70B with fixed limits | Model names in config, limits checked at deploy | Gemini 1.5 has been retired; free-tier limits change; Urdu token cost makes tokens/day the real limit. |
| FastEmbed bge-m3, `Qdrant/bm25` | FlagEmbedding/sentence-transformers; own Urdu tokenizer | Uncertain FastEmbed support; the stock BM25 tokenizer isn't made for Urdu. |
| Vol 32 thematic tables in routing | Not used | Vol 32 isn't transcribed. |
| Import `MERGE` etc. from `build_index.py` | Shared module `khutbat_data.py` | `build_index.py` runs at import (reads `sys.argv`). |
| Synonym table from `MERGE`/`PEOPLE_MERGE` | Search over all index heads (list C) | `MERGE` only covers the indexers' variants, not readers' wording. |
| LLM query analysis on every question | Only for Roman Urdu or weak results | Saves quota and latency; bge-m3 handles English and Urdu. |
| Additive score with fixed 0.5/0.2 and ×1.5/1.3/0.7 | Weighted RRF, depth as tie-break, optional reranker, tuned on eval | RRF scores aren't in [0, 1]; fixed constants swamp them; "mention" shouldn't be a penalty. |
| One chunk per page + prev/next snippets; metadata-heavy embedding text | 250–400-word passages across page breaks, split at headings; lean embedding text | Thoughts aren't cut at page ends; embeddings stay distinct. |
| Model writes the link `[جلد ۲، ص ۱۵](v02.html#p15)` | Model cites `[n]`; server writes highlight links | Links can't be invented; pages open with the passage highlighted. |
| — | Quotation check, fatwa note, coverage note | Accuracy of ayat/ahadith and responsible religious content. |
| — | Abuse protection (CORS, Turnstile, rate limit, cache) | A public endpoint can otherwise use up the free quota. |
| 25 benchmark questions | Generated test set from the index + 60 hand-written, launch gate | Enough cases to tune weights and catch regressions. |
| Ask widget first | Static search first (no server) | Useful even if the free LLM tiers disappear. |

## 12. Risks

| Risk | Mitigation |
|---|---|
| Free LLM tier cut or removed | Sources-only mode; provider is config; small context. |
| Wrong or invented quotation | Server-side quote check; only verified text shown. |
| Readers take answers as fatwa | Prompt rule + fixed note + links to the full page. |
| Text changes after owner reverts corrections | Data rebuilt on every push; hash-keyed embedding cache. |
| Poor Roman Urdu results | Transliteration step; Roman Urdu in the eval set. |
| Space cold start | "Waking up" message; fallback to static search. |
| Quota abuse | Turnstile, rate limit, CORS, cache. |
