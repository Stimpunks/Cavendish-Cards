#!/usr/bin/env python3
"""Run every Cavendish Cards build script in order, from one command.

Regenerates all derived files from the card files:
  build-starter-deck.py  -> cavendish-cards-starter-deck.md
  build-guidebook.py     -> cavendish-cards-guidebook.md
  build-placeholders.py  -> assets/playtest/**
  build-site.py          -> web/ (cards.json, guidebook.html, faces/) [gitignored]
  build-playtest-pdf.py  -> assets/playtest/cavendish-cards-playtest.pdf  [needs cairosvg + weasyprint]
  build-facilitator-pdf.py -> cavendish-cards-facilitator-sheet.pdf  [needs weasyprint]

Usage (from anywhere):
    python3 scripts/build-all.py

The PDF steps are optional: if their extra dependencies aren't installed they are
skipped with a note, and the run still succeeds. Any required step failing makes
this exit non-zero.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# (filename, required) — the PDF is optional (heavy third-party dependencies).
STEPS = [
    ("build-starter-deck.py", True),
    ("build-guidebook.py", True),
    ("build-placeholders.py", True),
    ("build-site.py", True),
    ("build-playtest-pdf.py", False),
    ("build-facilitator-pdf.py", False),
]


def main():
    print("Cavendish Cards: building all outputs\n")
    built, skipped, failed = [], [], []

    for script, required in STEPS:
        path = SCRIPTS_DIR / script
        print(f"running {script}")
        if not path.exists():
            (failed if required else skipped).append((script, "script not found"))
            print(f"  {'FAILED' if required else 'skipped'}: script not found\n")
            continue

        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, text=True)
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()

        if proc.returncode == 0:
            for ln in out.splitlines():
                print(f"    {ln}")
            print("  ok\n")
            built.append(script)
            continue

        missing_deps = "ModuleNotFoundError" in err or "ImportError" in err
        native_lib = "cairo" in err.lower() or "pango" in err.lower()
        detail = (err.splitlines()[-1] if err else out.splitlines()[-1]
                  if out else f"exit {proc.returncode}")
        if not required and (missing_deps or native_lib):
            print("  skipped: the PDF needs cairosvg + weasyprint and their native\n"
                  "           libraries (macOS: brew install cairo pango gdk-pixbuf libffi;\n"
                  "           then pip install cairosvg weasyprint)\n")
            skipped.append((script, "missing PDF dependencies"))
        elif required:
            print(f"  FAILED: {detail}\n")
            failed.append((script, detail))
        else:
            print(f"  skipped: {detail}\n")
            skipped.append((script, detail))

    print("-" * 44)
    print(f"built {len(built)}, skipped {len(skipped)}, failed {len(failed)}")
    for script, why in skipped:
        print(f"  skipped  {script}: {why}")
    for script, why in failed:
        print(f"  FAILED   {script}: {why}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
