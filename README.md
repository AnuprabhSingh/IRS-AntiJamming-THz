# IRS-Assisted Anti-Jamming Communications in THz Wideband Systems
### A Fuzzy WoLF-PHC Learning Approach with Hybrid Beamforming

**Author:** Anuprabh Singh, Department of Electronics and Communication Engineering, NIT Warangal  
**Contact:** anuprabh@student.nitw.ac.in

> Paper: [`paper/paper_ieee.tex`](paper/paper_ieee.tex) | Pre-built PDF: [`paper/paper.pdf`](paper/paper.pdf)

---

## Overview

This repository contains the full simulation code and pre-computed results for the paper. The system proposes a unified framework for **IRS-assisted anti-jamming in wideband THz communications**, jointly optimizing:

- **Transmit power allocation** (via Fuzzy WoLF-PHC RL)
- **SPDP-RIS phase shifts** (closed-form AO, beam-squint compensation)
- **Hybrid analog-digital beamforming** (SVD + MVDR, sub-connected architecture)

against a smart adaptive jammer at **f_c = 100 GHz, B = 10 GHz**.

The central insight is that **unpredictability is a security property**: the WoLF-PHC mixed strategy prevents the jammer from predicting and exploiting the defender's actions.

---

## Key Results (Table II)

| Method | Rate (bits/s/Hz) | SINR Protection |
|--------|-----------------|-----------------|
| **Fuzzy WoLF-PHC (proposed)** | **11.87 ± 0.55** | **81.6% ± 3.9%** |
| AO Baseline | 7.89 ± 0.78 | 43.2% ± 7.7% |
| Classical Q-Learning | 8.25 ± 1.28 | 49.0% ± 14.4% |
| Fast Q-Learning | 8.05 ± 1.68 | 45.5% ± 18.7% |
| DQN | 8.23 ± 2.40 | 49.1% ± 25.7% |

*Mean ± std over 5 independent seeds, 600 training episodes each.*

Pre-computed results are in [`outputs_joint_ao/`](outputs_joint_ao/) — including all 10 IEEE-format figures.

---

## Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/AnuprabhSingh/IRS-AntiJamming-THz.git
cd IRS-AntiJamming-THz

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3a. Just regenerate the figures from pre-computed data (~30 seconds)
PYTHONPATH=src python scripts/generate_joint_ao_plots.py

# 3b. Full re-run from scratch (~30-60 min on modern CPU)
python run_all.py
```

**Output:** `outputs_joint_ao/ieee_plots/` — 10 publication figures (PDF + PNG).

---

## System Parameters

| Parameter | Value |
|-----------|-------|
| Center frequency f_c | 100 GHz |
| Bandwidth B | 10 GHz |
| BS antennas N | 64 |
| RF chains N_RF | 8 |
| IRS elements M | 256 (16×16 UPA) |
| IRS sub-arrays Q | 64 (8×8 SPDP) |
| OFDM subcarriers M_sc | 64 |
| Users K | 4 |
| Jammer antennas N_J | 2 |
| Max TX power P_max | 40 dBm |
| SINR threshold γ_min | 5 dB |
| RL action space \|A\| | 42 |
| Training episodes | 600 |
| Seeds | 5 |

---

## Repository Structure

```
IRS-AntiJamming-THz/
├── src/
│   └── irs_anti_jamming/           # Main simulation package
│       ├── agents.py               # TabularQ, FastQ, FuzzyWoLF-PHC
│       ├── channel_model.py        # Rician fading, ULA steering vectors
│       ├── system_model.py         # SINR, MVDR beamformers, reward
│       ├── action_space.py         # 42-action hybrid space + AO IRS optimizer
│       ├── state.py                # 3-feature state + fuzzy memberships
│       ├── jammer.py               # Smart adaptive jammer model
│       ├── environment.py          # RL environment (predictability tracking)
│       ├── baselines.py            # AO and No-IRS baselines
│       └── thz/                    # THz-specific layer
│           ├── thz_config.py       # THzSystemConfig, THzRLConfig
│           ├── thz_channel_model.py# Saleh-Valenzuela THz channel, near-field
│           ├── thz_system_model.py # OFDM SINR, per-subcarrier evaluation
│           ├── thz_environment.py  # THz RL environment
│           ├── thz_experiments.py  # Training & evaluation runners
│           ├── spdp_ris.py         # SPDP-RIS beam-squint compensation
│           ├── hybrid_beamforming.py # Sub-connected HBF, SVD analog precoder
│           ├── dqn_agent.py        # DQN (PyTorch / NumPy fallback)
│           └── d3qn_agent.py       # Dueling D3QN
├── scripts/
│   ├── run_joint_ao_results.py     # Main: train all methods, 5 seeds
│   ├── run_journal_sweeps.py       # Parameter sweeps (Figs 5–8, 12)
│   └── generate_joint_ao_plots.py  # Generate all 10 IEEE figures
├── outputs_joint_ao/               # Pre-computed results (included)
│   ├── paper_results.json          # Table II data (5 methods × 5 seeds)
│   ├── sweep_pmax.json             # Fig 2: P_max sweep
│   ├── sweep_nris.json             # Fig 3: N_RIS sweep
│   ├── sweep_sinr_target.json      # Fig 4: SINR threshold sweep
│   ├── sweep_pjammer.json          # Fig 5: Jammer power sweep
│   ├── sweep_sinr_cdf.json         # SINR CDF data
│   ├── convergence_data.json       # Training reward curves
│   └── ieee_plots/                 # All 10 figures (PDF + PNG)
├── paper/
│   ├── paper_ieee.tex              # IEEE LaTeX source
│   └── paper.pdf                   # Compiled 6-page paper
├── run_all.py                      # Entry point: full reproduction
├── run_reproduce.sh                # Shell entry point
├── requirements.txt
└── .gitignore
```

---

## Running Individual Steps

```bash
# Train all 5 methods over 5 seeds and save to outputs_joint_ao/paper_results.json
PYTHONPATH=src python scripts/run_joint_ao_results.py

# Run parameter sweeps for all figures (takes ~10 hours)
PYTHONPATH=src python scripts/run_journal_sweeps.py

# Regenerate all figures from existing JSON data
PYTHONPATH=src python scripts/generate_joint_ao_plots.py
```

---

## Algorithm: Fuzzy WoLF-PHC

The proposed agent maintains a **mixed (stochastic) policy** over a 42-action space (7 power fractions × 6 allocation modes). At each step:

1. **State** is compressed to 3 normalized features (jammer pressure, channel quality, SINR health) and mapped to 27 fuzzy memberships via triangular functions.
2. **Fuzzy Q-value** FQ(s,a) = Σ_ℓ ψ_ℓ(s) · Q_ℓ(s,a) aggregates per-fuzzy-state Q-tables.
3. **WoLF update**: learn faster when losing (ξ_loss = 0.04), slower when winning (ξ_win = 0.01) — converges to Nash equilibrium in self-play.
4. **Eval policy**: adaptive Boltzmann softmax + 3% uniform mixing floor → inherently unpredictable to the jammer.

---

## Dependencies

- **Python 3.11+**
- `numpy >= 1.24`, `matplotlib >= 3.8`, `scipy >= 1.10`
- `torch >= 2.0` (optional — DQN baseline falls back to NumPy if absent)

---

## Citation

If you use this code, please cite:

```bibtex
@article{singh2025irs,
  title   = {Intelligent Reflecting Surface Assisted Anti-Jamming Communications
             in {THz} Wideband Systems: A Fuzzy {WoLF-PHC} Learning Approach
             with Hybrid Beamforming},
  author  = {Singh, Anuprabh},
  journal = {arXiv preprint},
  year    = {2025}
}
```
