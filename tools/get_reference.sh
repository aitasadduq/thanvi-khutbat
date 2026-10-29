#!/bin/bash
# Download the reference texts used by tools/arabic.py into reference/ (not committed; ~60 MB).
# Qur'an (Indo-Pak and simple script) and nine hadith collections, from the public-domain
# fawazahmed0/quran-api and fawazahmed0/hadith-api projects.
set -e
cd "$(dirname "$0")/.." && mkdir -p reference && cd reference
for e in ara-quranindopak ara-quransimple; do
  curl -sSL -o $e.json https://raw.githubusercontent.com/fawazahmed0/quran-api/1/editions/$e.json
done
for b in bukhari muslim abudawud tirmidhi nasai ibnmajah malik nawawi qudsi; do
  curl -sSL -o ara-$b.json https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/ara-$b.json
done
ls -la
