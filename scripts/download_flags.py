"""
One-time script to download flag images from flagpedia.net.
Run with:  uv run python scripts/download_flags.py

Saves ~195 PNG files to flags/<code>.png at 320x240 resolution.
"""

import sys
import time
from pathlib import Path

import requests

# flagpedia.net CDN — consistent 320-wide PNGs, public domain
BASE_URL = "https://flagcdn.com/w320/{code}.png"

FLAGS_DIR = Path(__file__).parent.parent / "flags" / "countries"

# All ISO 3166-1 alpha-2 codes used in countries.py
CODES = [
    "af", "al", "dz", "ad", "ao", "ag", "ar", "am", "au", "at", "az",
    "bs", "bh", "bd", "bb", "by", "be", "bz", "bj", "bt", "bo", "ba",
    "bw", "br", "bn", "bg", "bf", "bi", "cv", "kh", "cm", "ca", "cf",
    "td", "cl", "cn", "co", "km", "cg", "cd", "cr", "ci", "hr", "cu",
    "cy", "cz", "dk", "dj", "dm", "do", "ec", "eg", "sv", "gq", "er",
    "ee", "sz", "et", "fj", "fi", "fr", "ga", "gm", "ge", "de", "gh",
    "gr", "gd", "gt", "gn", "gw", "gy", "ht", "hn", "hu", "is", "in",
    "id", "ir", "iq", "ie", "il", "it", "jm", "jp", "jo", "kz", "ke",
    "ki", "kp", "kr", "kw", "kg", "la", "lv", "lb", "ls", "lr", "ly",
    "li", "lt", "lu", "mg", "mw", "my", "mv", "ml", "mt", "mh", "mr",
    "mu", "mx", "fm", "md", "mc", "mn", "me", "ma", "mz", "mm", "na",
    "nr", "np", "nl", "nz", "ni", "ne", "ng", "mk", "no", "om", "pk",
    "pw", "pa", "pg", "py", "pe", "ph", "pl", "pt", "qa", "ro", "ru",
    "rw", "kn", "lc", "vc", "ws", "sm", "st", "sa", "sn", "rs", "sc",
    "sl", "sg", "sk", "si", "sb", "so", "za", "ss", "es", "lk", "sd",
    "sr", "se", "ch", "sy", "tw", "tj", "tz", "th", "tl", "tg", "to",
    "tt", "tn", "tr", "tm", "tv", "ug", "ua", "ae", "gb", "us", "uy",
    "uz", "vu", "ve", "vn", "ye", "zm", "zw",
]


def download_flags(force: bool = False) -> None:
    FLAGS_DIR.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "flag-quiz/1.0 (educational project)"

    total = len(CODES)
    skipped = downloaded = failed = 0

    for i, code in enumerate(CODES, 1):
        dest = FLAGS_DIR / f"{code}.png"
        if dest.exists() and not force:
            skipped += 1
            print(f"[{i:3}/{total}] skip  {code}")
            continue

        url = BASE_URL.format(code=code)
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            downloaded += 1
            print(f"[{i:3}/{total}] ok    {code}  ({len(resp.content) // 1024} KB)")
        except requests.RequestException as exc:
            failed += 1
            print(f"[{i:3}/{total}] FAIL  {code}  — {exc}", file=sys.stderr)

        # Be polite to the CDN
        time.sleep(0.05)

    print(f"\nDone. Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    force = "--force" in sys.argv
    download_flags(force=force)
