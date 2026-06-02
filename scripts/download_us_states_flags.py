"""
One-time script to download US state flag images from flagcdn.com.
Run with:  uv run python scripts/download_us_states_flags.py

Saves 50 PNG files to flags/us_states/<code>.png
"""

import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://flagcdn.com/w320/{code}.png"
FLAGS_DIR = Path(__file__).parent.parent / "flags" / "us_states"

CODES = [
    "us-al", "us-ak", "us-az", "us-ar", "us-ca", "us-co", "us-ct", "us-de",
    "us-fl", "us-ga", "us-hi", "us-id", "us-il", "us-in", "us-ia", "us-ks",
    "us-ky", "us-la", "us-me", "us-md", "us-ma", "us-mi", "us-mn", "us-ms",
    "us-mo", "us-mt", "us-ne", "us-nv", "us-nh", "us-nj", "us-nm", "us-ny",
    "us-nc", "us-nd", "us-oh", "us-ok", "us-or", "us-pa", "us-ri", "us-sc",
    "us-sd", "us-tn", "us-tx", "us-ut", "us-vt", "us-va", "us-wa", "us-wv",
    "us-wi", "us-wy",
]


def download_us_state_flags(force: bool = False) -> None:
    FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "flag-quiz/1.0 (educational project)"

    total = len(CODES)
    skipped = downloaded = failed = 0

    for i, code in enumerate(CODES, 1):
        dest = FLAGS_DIR / f"{code}.png"
        if dest.exists() and not force:
            skipped += 1
            print(f"[{i:2}/{total}] skip  {code}")
            continue

        url = BASE_URL.format(code=code)
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            downloaded += 1
            print(f"[{i:2}/{total}] ok    {code}  ({len(resp.content) // 1024} KB)")
        except requests.RequestException as exc:
            failed += 1
            print(f"[{i:2}/{total}] FAIL  {code}  — {exc}", file=sys.stderr)

        time.sleep(0.05)

    print(f"\nDone. Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    force = "--force" in sys.argv
    download_us_state_flags(force=force)
