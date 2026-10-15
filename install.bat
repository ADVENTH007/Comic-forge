@echo off
python -m venv venv
call venv\Scripts\activate.bat
set LLM_OK=1
if exist wheelhouse (
  echo Installing from the offline wheelhouse - no internet needed.
  pip install --no-index --find-links wheelhouse -r requirements.txt
  pip install --no-index --find-links wheelhouse -r requirements-llm.txt || set LLM_OK=0
) else (
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  pip install --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary :all: -r requirements-llm.txt || set LLM_OK=0
)
if "%LLM_OK%"=="0" (
  echo NOTE: the built-in language model runtime did not install for this Python version.
  echo ComicForge still works: use the simple tag converter, or an LLM server such as Ollama or LM Studio.
)
if exist models\*.gguf (echo Language model found in models\.) else (echo No language model yet. With internet run: python fetch_model.py  - or copy a .gguf into models\)
echo.
echo Done. Start reForge with --api, then run run_ui.bat
pause
