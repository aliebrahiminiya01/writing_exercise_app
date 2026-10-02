# Writing Exercise Studio

A distraction-free desktop app for writing exercises, built with Python and Qt (PySide6).
It counts words and characters, tracks progress toward a word target, times each writing session,
and keeps a local library of exercises grouped by category.

The app does **not** check spelling, correct grammar, rewrite sentences, or make writing suggestions,
and no text ever leaves your computer.

## Features

- **Exercise library** – create, rename, delete and switch between exercises, grouped by category
- **Live statistics** – word and character count, adjustable word target with a progress bar
- **Writing timer** – start, pause and reset a separate timer for each exercise
- **Rich text** – bold, italic, underline, font size and font colour
- **Right-to-left support** – switch each paragraph between LTR and RTL (e.g. for Persian or Arabic)
- **Search** – highlight every word that contains the search text
- **Repeated words** – a side panel lists words used more than once; click one to highlight it in the text
- **Light and dark theme**
- **Automatic saving**, plus a *Save now* button

### Keyboard shortcuts

| Action | macOS | Windows / Linux |
|--------|-------|-----------------|
| New exercise | ⌘N | Ctrl+N |
| Save | ⌘S | Ctrl+S |
| Bold / Italic / Underline | ⌘B / ⌘I / ⌘U | Ctrl+B / Ctrl+I / Ctrl+U |

## Requirements

- Python 3.10 or newer
- PySide6

## Run the app

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

- **macOS:** you can also double-click `install_and_run.command`.
- **Windows:** install the requirements first, then double-click `run_app.bat`.

## Run the tests

```bash
python3 -m unittest test_app -v
```

## Build a standalone app (macOS)

```bash
python3 -m pip install -r requirements-dev.txt
pyinstaller "Writing Exercise Studio.spec"
```

The app bundle is created in `dist/Writing Exercise Studio.app`.

## Where your data is stored

Exercises are saved in `~/.writing_exercise_studio/exercises.json` (inside your user home folder),
so removing the application folder does not remove your exercises.
If that file is ever damaged, the app keeps it as a backup (`exercises.unreadable-<date>.json`)
instead of overwriting it, and tells you where it is.

## Word counting

Words are counted locally. Contractions such as `don't` and hyphenated terms such as `well-written`
count as one word, and words in any language (e.g. Persian) are supported.

## Project structure

| File | Description |
|------|-------------|
| `app.py` | The whole application: data model, storage and Qt user interface |
| `test_app.py` | Unit tests for word counting and storage |
| `Writing Exercise Studio.spec` | PyInstaller build configuration |
| `app_icon.icns`, `app_icon.png` | Application icon |
