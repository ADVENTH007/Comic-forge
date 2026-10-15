"""Run this ONCE on a computer with internet. It collects everything ComicForge needs into
folders inside this one (wheelhouse/ for Python packages, models/ for the language model).
Copy the whole comicforge folder to the offline machine; install.bat / install.sh then install
from those folders without touching the network.

    python make_offline_bundle.py            # default 1.5B model
    python make_offline_bundle.py --model qwen2.5-3b-instruct-q4_k_m.gguf

The Python version and OS of this machine must match the offline one (wheels are specific to both).
llama-cpp-python is fetched as a prebuilt CPU wheel so no compiler is needed on the target.
"""
import argparse
import subprocess
import sys

from comicforge.local_llm import RECOMMENDED
from fetch_model import fetch

CPU_WHEELS = "https://abetlen.github.io/llama-cpp-python/whl/cpu"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5-1.5b-instruct-q4_k_m.gguf", choices=list(RECOMMENDED))
    ap.add_argument("--skip-model", action="store_true")
    a = ap.parse_args()
    pip = [sys.executable, "-m", "pip", "download", "-d", "wheelhouse"]
    subprocess.check_call(pip + ["-r", "requirements.txt"])
    subprocess.check_call(pip + ["-r", "requirements-llm.txt", "--extra-index-url", CPU_WHEELS,
                                 "--only-binary", ":all:"])
    subprocess.check_call([sys.executable, "-m", "pip", "download", "-d", "wheelhouse", "pip", "setuptools", "wheel"])
    if not a.skip_model:
        fetch(RECOMMENDED[a.model]["url"])
    print("\nBundle ready. Copy this whole folder to the offline machine and run the installer.")


if __name__ == "__main__":
    main()
