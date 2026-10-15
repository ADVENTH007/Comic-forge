# ComicForge

Turn a story into a comic, locally. ComicForge splits your story into scenes, writes a Stable Diffusion prompt for each
one, draws every panel with your own **reForge / Forge / A1111**, and lays the panels out as comic pages with your
original text underneath.

Everything runs on your machine. Nothing is sent to a cloud service.

## Features

- **Cast library.** Write each character once, in detail (face, hair, eyes, outfit, marks, LoRA, negative tags). Characters
  are stored apart from any story and can be reused in all of them.
- **Full-detail injection.** A character's look is written word for word into every panel they appear in. No language
  model rewrites or shortens it.
- **Versions.** Remake the same story as many times as you like. The story, scenes and captions are shared; each version has
  its own images, style, seeds and checkpoint. Characters are frozen per version, so later edits never change an old comic.
- **Offline language model (optional).** A small GGUF model runs inside the app through llama.cpp and writes the scene tags.
  No server, no internet, CPU only, so your VRAM stays free for image generation.
- **Resumable.** Finished panels are skipped on re-runs. Redo a single panel at any time.
- **Export.** PNG pages, PDF and CBZ, in several layouts.
- **Reproducible.** Every panel saves the exact prompt and seed that produced it.

```
story ──► splitter ──► scenes ──► prompt builder ──► reForge txt2img ──► panels ──► comic pages
              │            ▲             ▲
      (offline LLM:        │      Cast library, frozen
       scene tags only)  you edit   into each version
```

## Requirements

- Python 3.10+
- reForge, Forge or A1111 started with the `--api` flag, with an SD 1.5 checkpoint loaded
- Optional, for the built-in language model: about 1 to 2 GB of disk for a `.gguf` model

## Quick start

**1. Start reForge with the API on.** In `webui-user.bat` set:

```
set COMMANDLINE_ARGS=--api --medvram --no-half-vae
```

(`--medvram --no-half-vae` suit a 4 GB GPU; `--api` is the part ComicForge needs.)

**2. Install ComicForge.**

```
Windows:      install.bat
Linux/macOS:  ./install.sh
```

**3. Run it.**

```
Windows:      run_ui.bat
Linux/macOS:  ./run_ui.sh
```

The UI opens at http://127.0.0.1:7870.

## Using the app

1. **Story**: paste your story, pick the number of panels and split it into scenes. The story needs no character descriptions.
2. **Cast**: create your characters and tick the ones used in this story.
3. **Scenes**: edit captions, who appears in each panel, and the visual summary. *Show prompt* previews exactly what will be sent.
4. **Generate**: choose a version, connect to reForge, pick a checkpoint and size (512x640 is safe on 4 GB), and generate.
   To redo one panel, enter its number under *Only panel #* and tick *Overwrite*.
5. **Comic**: choose a layout and build the PNG pages, PDF and CBZ.

The text under each panel is your original wording, never shortened.

### Characters

Each character's fields are joined in a fixed order and written into the prompt of every panel they appear in (or every
panel, if *Inject in every panel* is ticked). They come before the scene tags, so they are never the part that gets pushed
out of the model's attention. Characters can also have a LoRA tag, their own negative tags and a seed.

SD 1.5 reads prompts in 75-token chunks. The Cast tab shows an approximate token count; for longer looks tick *Own chunk
per character* so a look is never cut in the middle.

A hand-written *prompt override* replaces the whole prompt. Put `{characters}` in it to insert the full look blocks.

### Versions

Each remake of a story is a version (`v001`, `v002`, ...). *Create new version* copies a version's settings and characters,
so only the images are new. Options:

- **Keep each panel's seed** for the same compositions in a new style or checkpoint.
- **Re-read the cast library** to pick up character edits.
- **Change art style** for the remake.

Projects created with ComicForge v1 are migrated into the cast library and `v001` automatically on first load.

### Offline language model

```
python fetch_model.py                                  # Qwen2.5 1.5B Instruct, about 1.1 GB
python fetch_model.py qwen2.5-3b-instruct-q4_k_m.gguf  # about 2 GB, better tags, slower
```

You can also copy any instruction-tuned `.gguf` file into `models/`, then choose *Built-in offline model* on the Story tab.

For a machine with no internet, run `python make_offline_bundle.py` once on a connected computer (same OS and Python
version). It fills `wheelhouse/` and `models/`; copy the whole folder across and run the installer.

If `llama-cpp-python` does not install for your Python version, ComicForge still works with the simple tag converter or
with an LLM server (Ollama, LM Studio, llama.cpp server) set on the Story tab.

## Command line

```
# new story with two characters, built-in model for scene tags
python -m comicforge.cli story.txt --name my-comic --panels 10 \
    --character "Mira=1girl, long silver hair, green eyes, red scarf" --cast mira --local-llm

# remake it as a new version
python -m comicforge.cli --name my-comic --reforge --keep-seeds --style Watercolor
python -m comicforge.cli --name my-comic --reforge --refresh-cast

# split only, then edit projects/my-comic/project.json by hand
python -m comicforge.cli story.txt --name my-comic --plan-only
```

Run `python -m comicforge.cli --help` for all options.

## Keeping characters consistent

SD 1.5 has no memory between images, so consistency comes from repetition:

- Use concrete tags in the Cast tab and keep them unchanged (versions freeze them for you).
- Train or download a LoRA for the character and set its tag.
- Use seed mode `character` or `fixed` to share noise between panels.
- Use one checkpoint for the whole comic.
- Expect to regenerate a few panels.

## Project layout

```
comicforge/                       application code
projects/_library/characters/     the cast, one JSON file per character
projects/<story>/project.json     story, scenes, which characters it uses
projects/<story>/versions/vNNN/   version.json, panels/ (PNG + prompt/seed sidecar), export/
models/                           the .gguf language model
tests/                            test suite
examples/                         sample story
```

## Tests

```
python tests/run_all.py
```

The tests run against a fake reForge server and a fake llama.cpp, so they need no GPU and no model. (`pytest tests/` also works.)

## Status and limits

- The pipeline, API client, layout, CLI, cast, versions and UI handler functions are covered by tests. The Gradio screens
  themselves and a real GGUF model have not been exercised end to end, so please open an issue if something misbehaves.
- Image quality and character likeness depend on your checkpoint, LoRAs and prompts.
- Prompts are tuned for SD 1.5 (short tag lists). SDXL works through the same API but may want more descriptive prompts.
- Use it for fiction and original characters, and respect the rights of anyone whose likeness or work you use.
