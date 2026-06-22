#!/usr/bin/env python3
"""Run full paper reproduction: training + evaluation + plot generation.

Steps:
  1. scripts/run_joint_ao_results.py  — trains all 5 methods over 5 seeds (~30-60 min)
  2. scripts/generate_joint_ao_plots.py — generates all 10 IEEE figures

Results are written to outputs_joint_ao/.

Usage:
    python run_all.py
    python run_all.py --fast   # quick sanity check (fewer seeds/episodes)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = sys.executable  # Use whatever Python is running this script


def run(script: str, extra_args: list[str] = []) -> None:
    cmd = [PYTHON, str(ROOT / script)] + extra_args
    print(f"\n{'='*60}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"{'='*60}")
    rc = subprocess.call(cmd, cwd=ROOT, env={**__import__('os').environ, "PYTHONPATH": str(ROOT / "src")})
    if rc != 0:
        print(f"\nERROR: {script} exited with code {rc}")
        sys.exit(rc)


if __name__ == "__main__":
    extra = ["--fast"] if "--fast" in sys.argv else []

    run("scripts/run_joint_ao_results.py", extra)
    run("scripts/generate_joint_ao_plots.py")

    print("\n✓ Reproduction complete!")
    print("  Results : outputs_joint_ao/paper_results.json")
    print("  Figures : outputs_joint_ao/ieee_plots/")
