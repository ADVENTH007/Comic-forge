"""Download a small GGUF model once (needs internet this one time), then ComicForge runs fully offline.

    python fetch_model.py                       # the default 1.5B model (about 1.1 GB)
    python fetch_model.py qwen2.5-3b-instruct-q4_k_m.gguf
    python fetch_model.py --url https://.../any-model.gguf

Resumes if interrupted. Or skip this and copy any instruction-tuned .gguf file into the models/ folder.
"""
import argparse
import os
import sys

import requests

from comicforge.local_llm import MODELS_DIR, RECOMMENDED


def fetch(url: str, dest_dir: str = MODELS_DIR) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, url.rsplit("/", 1)[-1].split("?")[0])
    part = dest + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {"Range": f"bytes={have}-"} if have else {}
    with requests.get(url, stream=True, headers=headers, timeout=60) as r:
        if r.status_code == 416:                       # already complete
            os.replace(part, dest)
            return dest
        r.raise_for_status()
        if have and r.status_code != 206:              # server ignored Range: start over
            have = 0
        total = int(r.headers.get("content-length", 0)) + have
        with open(part, "ab" if have else "wb") as f:
            done = have
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r{done / 1e6:7.0f} / {total / 1e6:.0f} MB", end="", flush=True)
    os.replace(part, dest)
    print(f"\nsaved {dest}")
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", default="qwen2.5-1.5b-instruct-q4_k_m.gguf", help="a name from the list below")
    ap.add_argument("--url", help="download any GGUF url instead")
    ap.add_argument("--dir", default=MODELS_DIR)
    a = ap.parse_args()
    if a.url:
        url = a.url
    elif a.name in RECOMMENDED:
        url = RECOMMENDED[a.name]["url"]
    else:
        print("unknown name. choices:\n" + "\n".join(f"  {k}  ({v['note']})" for k, v in RECOMMENDED.items()))
        return 2
    try:
        fetch(url, a.dir)
    except requests.RequestException as e:
        print(f"download failed: {e}\nDownload the file in a browser instead and put it in '{a.dir}'.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
