# Flag Quiz

A desktop flag-guessing quiz built with Python and PyQt5. You're shown a random country's flag and have to identify it — either by typing the name into a searchable dropdown or picking from four multiple-choice options.

**Features:**
- 194 UN-recognised countries
- Two answer modes: dropdown (type to search) or multiple choice (4 options)
- Live score tracking (correct / total)
- Finite mode (custom number of flags, default 30) or infinite mode (cycles through all flags endlessly without repeats)
- Results summary screen at the end of a finite quiz

---

## Quickstart

**Requirements:** Python 3.10+, Windows

### 1. Clone the repo

```
git clone https://github.com/your-username/flag-quiz.git
cd flag-quiz
```

### 2. Run the setup script

```
scripts\setup.bat
```

This will:
- Install [uv](https://docs.astral.sh/uv/) if it isn't already
- Create a virtual environment and install dependencies
- Download all flag images locally into `flags/`

### 3. Launch the app

```
uv run python -m flag_quiz.main
```

---

## Re-downloading flags

If flag images are missing or you want to re-fetch them:

```
uv run python scripts/download_flags.py --force
```
