"""Shared helpers for Arabic text: normalisation, the Qur'an reference text and the hadith corpus.

Reference data lives in reference/ (not committed; fetch with tools/get_reference.sh):
  ara-quranindopak.json  Qur'an, Indo-Pak script (the text put on the site)
  ara-<book>.json        hadith collections with harakat (used only for checking)
Both come from the fawazahmed0 quran-api / hadith-api projects (public domain).
"""
import os, re, json, difflib
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, 'reference')

# Letters folded to one form, so Urdu-typed Arabic (ی ہ ک) matches the Arabic reference (ي ه ك).
FOLD = str.maketrans({'ك': 'ک', 'ي': 'ی', 'ى': 'ی', 'ه': 'ہ', 'ة': 'ہ', 'ۃ': 'ہ', 'ۂ': 'ہ', 'ھ': 'ہ',
                      'أ': 'ا', 'إ': 'ا', 'ٱ': 'ا', 'آ': 'ا', 'ؤ': 'و', 'ئ': 'ی', 'ۓ': 'ے', 'ٰ': 'ا'})
# Harakat, Qur'anic marks, tatweel, punctuation, bidi marks.
MARKS = re.compile(r'[ؐ-ًؚ-ٟۖ-ۭ࣓-ࣿـ‌-‏'
                   r'"\'“”‘’«»()\[\]{}،,.:؛!؟?\-۔﴿﴾]')


def norm(s):
    """Skeleton of an Arabic/Urdu string: no marks, folded letters, no alif/hamza, single spaces."""
    s = MARKS.sub('', s.translate(FOLD))
    s = s.replace('ء', '').replace('ا', '')          # imla'i vs rasm differences mostly involve alif
    return re.sub(r'\s+', ' ', s).strip()


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


# ---------------------------------------------------------------- Qur'an
class Quran:
    """Qur'an text with a character-level search on letter skeletons, so that a quotation is found even
    when it starts inside a word (اٰتُوا for وَاٰتُوا) or the typing differs by a letter."""
    K = 4

    def __init__(self):
        data = json.load(open(os.path.join(REF, 'ara-quranindopak.json'), encoding='utf-8'))['quran']
        simple = json.load(open(os.path.join(REF, 'ara-quransimple.json'), encoding='utf-8'))['quran']
        self.words = []          # (surah, ayah, word as printed)
        for v, sv in zip(data, simple):
            for w in self._rejoin(v['text'].replace('\u200f', '').split(), sv['text'].split()):
                self.words.append((v['chapter'], v['verse'], w))
        self.flat = []           # skeleton letters of the whole text
        self.where = []          # for each letter: (word index, index of the letter inside the printed word)
        for wi, (_, _, w) in enumerate(self.words):
            for ci, c in enumerate(w):
                if norm(c):
                    self.flat.append(norm(c)); self.where.append((wi, ci))
        self.flat = ''.join(self.flat)
        self.grams = defaultdict(list)
        for i in range(len(self.flat) - self.K + 1):
            self.grams[self.flat[i:i + self.K]].append(i)

    @staticmethod
    def _rejoin(toks, ref):
        """The Indo-Pak file splits some words after an iqlab mark (اَنۭۡ بَتَتۡ for اَنۢبَتَتۡ); rejoin them
        using the word division of the simple-script text. Stray mark-only tokens join the word before."""
        out, j, i = [], 0, 0
        while i < len(toks):
            t = toks[i]
            if not norm(t) and out:
                out[-1] += t; i += 1; continue
            if i + 1 < len(toks) and j < len(ref) and norm(t) != norm(ref[j]) and norm(t + toks[i + 1]) == norm(ref[j]):
                t = t + toks[i + 1]; i += 1
            out.append(t); i += 1; j += 1
        return out

    def find(self, text):
        """Best match for `text`: (score, start letter, end letter) or None."""
        q = norm(text).replace(' ', '')
        if len(q) < 6: return None
        votes = defaultdict(int)
        for k in range(len(q) - self.K + 1):
            for pos in self.grams.get(q[k:k + self.K], ()):
                votes[pos - k] += 1
        if not votes: return None
        best = None
        top = max(votes.values())
        for s0, v in sorted(votes.items(), key=lambda x: -x[1])[:40]:
            if v < top * 0.6: break
            if self.flat[s0:s0 + len(q)] == q:          # exact: prefer a clean one
                cand = (1.0, s0, s0 + len(q))
                if self.clean(s0, s0 + len(q)): return cand
                best = best if best and best[0] == 1.0 else cand
                continue
            for s in range(max(0, s0 - 3), s0 + 4):
                for L in range(max(4, len(q) - 4), len(q) + 5):
                    r = ratio(q, self.flat[s:s + L])
                    if not best or r > best[0]: best = (r, s, min(len(self.flat), s + L))
        return best

    def text(self, s, e):
        """Printed text for letters s..e-1: whole words, except a leading prefix the quotation left out
        (و، ف، ب ...) is cut, with ayah-end marks between ayat."""
        w0, c0 = self.where[s]; w1, _ = self.where[e - 1]
        out = []
        for wi in range(w0, w1 + 1):
            w = self.words[wi][2]
            if wi == w0 and c0 > 0:
                # keep from the first letter after the previous skeleton letter and its marks
                prev = max(ci for (x, ci) in self.where[s - 3:s] if x == wi) if any(x == wi for x, _ in self.where[s - 3:s]) else -1
                j = prev + 1
                while j < c0 and MARKS.match(w[j]): j += 1
                w = w[j:]
            out.append(w)
            if wi < w1 and self.words[wi + 1][1] != self.words[wi][1]:
                out.append('۝')
        return ' '.join(out)

    def clean(self, s, e):
        """True when the match starts at a word start (or after a one-letter prefix و ف ب ل ک) and ends at a word end."""
        ws, we = self.where[s][0], self.where[e - 1][0]
        before = [self.flat[i] for i in range(max(0, s - 3), s) if self.where[i][0] == ws]
        if len(before) > 1 or (before and before[0] not in 'وفبلک'): return False
        return e >= len(self.where) or self.where[e][0] != we

    def ref(self, s, e):
        (a1, b1, _), (a2, b2, _) = self.words[self.where[s][0]], self.words[self.where[e - 1][0]]
        if a1 != a2: return f'{a1}:{b1}-{a2}:{b2}'
        return f'{a1}:{b1}' if b1 == b2 else f'{a1}:{b1}-{b2}'

    def span(self, ref):
        """Letter range (s, e) covering a reference like 9:119 or 41:30-32."""
        m = re.match(r'(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$', ref)
        a1, b1 = int(m.group(1)), int(m.group(2))
        a2 = int(m.group(3) or a1); b2 = int(m.group(4) or b1)
        idx = [i for i, (wi, _) in enumerate(self.where) if (a1, b1) <= self.words[wi][:2] <= (a2, b2)]
        return idx[0], idx[-1] + 1


# ---------------------------------------------------------------- hadith
HADITH_BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'nawawi', 'qudsi']
BOOK_NAMES = {'bukhari': 'صحیح بخاری', 'muslim': 'صحیح مسلم', 'abudawud': 'سنن ابی داؤد', 'tirmidhi': 'سنن ترمذی',
              'nasai': 'سنن نسائی', 'ibnmajah': 'سنن ابن ماجہ', 'malik': 'موطا مالک', 'nawawi': 'اربعین نووی',
              'qudsi': 'احادیث قدسیہ'}


class Hadith:
    def __init__(self):
        self.recs = []      # (book, number, normalised words)
        self.tri = defaultdict(set)
        for b in HADITH_BOOKS:
            p = os.path.join(REF, f'ara-{b}.json')
            if not os.path.exists(p): continue
            for h in json.load(open(p, encoding='utf-8'))['hadiths']:
                w = norm(h['text']).split()
                k = len(self.recs); self.recs.append((b, h['hadithnumber'], w, h['text']))
                for i in range(len(w) - 2): self.tri[(w[i], w[i + 1], w[i + 2])].add(k)

    def find(self, text, top=3):
        """Closest passages for `text`: [(score, book, number, matched normalised words, full text)]."""
        q = norm(text).split()
        if len(q) < 3: return []
        cnt = defaultdict(int)
        for i in range(len(q) - 2):
            for k in self.tri.get(tuple(q[i:i + 3]), ()): cnt[k] += 1
        qs = ' '.join(q); out = []
        for k, _ in sorted(cnt.items(), key=lambda x: -x[1])[:10]:
            b, n, w, full = self.recs[k]
            best = (0, '')
            starts = {i - j for j in range(len(q) - 2) for i in range(len(w) - 2)
                      if tuple(w[i:i + 3]) == tuple(q[j:j + 3])}
            for s in {max(0, x + d) for x in starts for d in (-1, 0, 1)}:
                for L in (len(q) - 1, len(q), len(q) + 1):
                    seg = ' '.join(w[s:s + L]); r = ratio(qs, seg)
                    if r > best[0]: best = (r, seg)
            out.append((best[0], b, n, best[1], full))
        return sorted(out, reverse=True)[:top]
