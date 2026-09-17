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
    python3 scripts/build-all.py --check

--check answers one question: was anything committed without being rebuilt?
It runs the same build, then reports any tracked file the build changed, and
exits 1 if there were any. Note that it *does* write -- it is the standard
"regenerate and diff" check, not a dry run. That is safe, because the builders
are idempotent: run twice on an unchanged tree and the second run touches
nothing. It compares git status before and after, so your own edits in
progress are not mistaken for stale output.

Suitable as a pre-commit hook (a full run is ~2s when nothing has changed):

    git config core.hooksPath hooks     # if you add one under hooks/

The PDF steps are optional: if their extra dependencies aren't installed they are
skipped with a note, and the run still succeeds. Any required step failing makes
this exit non-zero.

The PDFs need cairosvg/weasyprint plus native libraries, which Apple's system
Python cannot load: macOS strips DYLD_* when launching a SIP-protected binary,
so cffi never finds libcairo or libgobject. The fix is a Homebrew-Python venv.
Create it once:

    brew install cairo pango gdk-pixbuf libffi
    /opt/homebrew/bin/python3 -m venv ~/.venvs/cavendish-pdf
    ~/.venvs/cavendish-pdf/bin/pip install cairosvg weasyprint

This script then finds it on its own and runs the PDF steps with it, so the
print files stop drifting behind the deck. Override the path with
CAVENDISH_PDF_PYTHON if you keep the venv somewhere else.
"""

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# (filename, required, needs_pdf_deps)
STEPS = [
    ("build-starter-deck.py", True, False),
    ("build-guidebook.py", True, False),
    ("build-placeholders.py", True, False),
    ("build-site.py", True, False),
    ("build-playtest-pdf.py", False, True),
    ("build-facilitator-pdf.py", False, True),
]

DEFAULT_PDF_VENV = Path.home() / ".venvs" / "cavendish-pdf" / "bin" / "python"
# Homebrew's lib dir, where cairo/pango/gobject actually live.
BREW_LIBS = ["/opt/homebrew/lib", "/usr/local/lib"]


def git_status(root):
    """path -> two-char porcelain code, or None if git can't answer.

    Gitignored files are excluded by git, so the generated web/ outputs never
    show up here -- only tracked files and genuinely new untracked ones.
    """
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    status = {}
    for line in proc.stdout.splitlines():
        if len(line) > 3:
            status[line[3:].strip()] = line[:2]
    return status


def pdf_interpreter():
    """Path to a Python that can load the PDF native libs, or None."""
    override = os.environ.get("CAVENDISH_PDF_PYTHON")
    if override:
        return Path(override) if Path(override).exists() else None
    return DEFAULT_PDF_VENV if DEFAULT_PDF_VENV.exists() else None


def pdf_env():
    """Env for the PDF steps: point cffi at Homebrew's libraries.

    Safe to set here even though the same variable is stripped from this
    process -- dyld only strips it when launching a protected binary, and the
    venv interpreter is not one.
    """
    env = os.environ.copy()
    libs = [d for d in BREW_LIBS if Path(d).is_dir()]
    if libs:
        existing = env.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        env["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(
            libs + ([existing] if existing else []))
    return env


def main():
    check = "--check" in sys.argv[1:]
    root = SCRIPTS_DIR.parent

    before = None
    if check:
        before = git_status(root)
        if before is None:
            print("--check needs a git repository to compare against; "
                  "cannot verify here.")
            sys.exit(2)

    print("Cavendish Cards: building all outputs\n")
    built, skipped, failed = [], [], []

    pdf_python = pdf_interpreter()
    if pdf_python:
        print(f"PDF steps will use {pdf_python}\n")

    for script, required, needs_pdf in STEPS:
        path = SCRIPTS_DIR / script
        print(f"running {script}")
        if not path.exists():
            (failed if required else skipped).append((script, "script not found"))
            print(f"  {'FAILED' if required else 'skipped'}: script not found\n")
            continue

        if needs_pdf and pdf_python:
            argv, env = [str(pdf_python), str(path)], pdf_env()
        else:
            argv, env = [sys.executable, str(path)], None
        proc = subprocess.run(argv, capture_output=True, text=True, env=env)
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
            print("  skipped: no Python here can load the PDF native libraries.\n"
                  "           Apple's system Python never will -- SIP strips DYLD_*.\n"
                  "           Create the venv once and this step runs itself:\n"
                  "             brew install cairo pango gdk-pixbuf libffi\n"
                  "             /opt/homebrew/bin/python3 -m venv ~/.venvs/cavendish-pdf\n"
                  "             ~/.venvs/cavendish-pdf/bin/pip install cairosvg weasyprint\n")
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

    if not check:
        return

    after = git_status(root)
    changed = sorted(path for path, code in after.items()
                     if before.get(path) != code)
    print()
    if changed:
        print("STALE -- rebuilding changed these tracked files:")
        for path in changed:
            print(f"  {path}")
        print("\nThey were committed without being regenerated. Stage them.")
        sys.exit(1)

    if skipped:
        print("Up to date, but this check was PARTIAL -- these steps did not run:")
        for script, why in skipped:
            print(f"  {script}: {why}")
        print("Outputs they own could still be stale.")
        sys.exit(0)

    print("Up to date: every generated file matches its sources.")


if __name__ == "__main__":
    main()
