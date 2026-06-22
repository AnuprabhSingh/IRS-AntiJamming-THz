#!/bin/sh
# Reproduce all paper results from scratch.
# Requires Python 3.11+ and the dependencies in requirements.txt.
#
# Usage:
#   ./run_reproduce.sh           # full reproduction (~30-60 min)
#   ./run_reproduce.sh --fast    # quick sanity check
set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

echo "Python: $($PYTHON --version)"
echo ""
echo "Step 1/2: Training and evaluation (all 5 methods × 5 seeds)..."
PYTHONPATH=src $PYTHON scripts/run_joint_ao_results.py "$@"

echo ""
echo "Step 2/2: Generating IEEE figures..."
PYTHONPATH=src $PYTHON scripts/generate_joint_ao_plots.py

echo ""
echo "✓ Reproduction complete!"
echo "  Results : outputs_joint_ao/paper_results.json"
echo "  Figures : outputs_joint_ao/ieee_plots/"
