#!/usr/bin/env bash
set -e
python3 -m venv venv
. venv/bin/activate
LLM_OK=1
if [ -d wheelhouse ]; then
  echo "Installing from the offline wheelhouse (no internet needed)."
  pip install --no-index --find-links wheelhouse -r requirements.txt
  pip install --no-index --find-links wheelhouse -r requirements-llm.txt || LLM_OK=0
else
  pip install --upgrade pip
  pip install -r requirements.txt
  # prebuilt CPU wheel first (no compiler needed)
  pip install --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary :all: -r requirements-llm.txt || LLM_OK=0
fi
if [ "$LLM_OK" = 0 ]; then
  echo "NOTE: the built-in language model runtime (llama-cpp-python) did not install for this Python version."
  echo "ComicForge still works: use the simple tag converter, or point it at an LLM server (Ollama / LM Studio)."
fi
if ls models/*.gguf >/dev/null 2>&1; then echo "Language model found in models/."; else
  echo "No language model yet. With internet run:  python fetch_model.py   (or copy a .gguf into models/)"; fi
echo "Done. Start reForge with --api, then run ./run_ui.sh"
