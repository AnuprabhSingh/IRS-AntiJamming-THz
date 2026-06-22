# IRS-Assisted Anti-Jamming Communications in THz Wideband Systems
## A Fuzzy WoLF-PHC Learning Approach with Hybrid Beamforming

**Anuprabh Singh** · Department of Electronics and Communication Engineering, NIT Warangal  
`anuprabh.2004@gmail.com`

---

Wideband THz links (100 GHz, 10 GHz bandwidth) are acutely vulnerable to adaptive jamming because their narrow, directional beams make them easy to target once the jammer learns the transmitter's behavior. This repository contains the full simulation code and pre-computed results for a paper that closes this gap using three synergistic mechanisms:

- **SPDP-RIS** — a 256-element (16×16) sub-array phase-dependent partial-connection intelligent reflecting surface that compensates THz beam squint across all 64 subcarriers
- **Sub-connected hybrid beamforming** — 64 antennas, 8 RF chains; SVD analog precoder + per-subcarrier MVDR digital precoder
- **Fuzzy WoLF-PHC** — a reinforcement learning controller that converges to a *mixed (stochastic) strategy*, making the transmitter inherently unpredictable to a jammer that monitors action history

The central claim: **unpredictability is a security property**. A jammer that cannot predict the defender's power allocation cannot focus its interference effectively. WoLF-PHC's mixed strategy provides this unpredictability as an algorithmic guarantee, not an ad-hoc patch.

---

## Results

Evaluated over **5 independent random seeds × 600 training episodes** each.

| Method | Rate (bits/s/Hz) | SINR Protection | Variance |
|--------|:----------------:|:---------------:|:--------:|
| **Fuzzy WoLF-PHC (proposed)** | **11.87 ± 0.55** | **81.6% ± 3.9%** | Lowest |
| Classical Q-Learning | 8.25 ± 1.28 | 49.0% ± 14.4% | High |
| Fast Q-Learning | 8.05 ± 1.68 | 45.5% ± 18.7% | High |
| DQN | 8.23 ± 2.40 | 49.1% ± 25.7% | Highest |
| AO Baseline | 7.89 ± 0.78 | 43.2% ± 7.7% | Low |
| No IRS | 5.48 | 18.8% | — |

**+50% rate and +89% SINR protection** over the AO baseline. Pre-computed results and all 10 publication figures are in [`outputs_joint_ao/`](outputs_joint_ao/).

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/AnuprabhSingh/IRS-AntiJamming-THz.git
cd IRS-AntiJamming-THz

# 2. Install dependencies (Python 3.11+)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3a. Regenerate all figures from pre-computed data (~30 seconds)
PYTHONPATH=src python scripts/generate_joint_ao_plots.py

# 3b. Full re-run from scratch (~30-60 min on a modern CPU)
python run_all.py
```

Figures are written to `outputs_joint_ao/ieee_plots/` as both PDF and PNG.

---

## System Model

```
                        Jammer (2 ant.)
                             |
  BS ──────────────────────── UE_1 ... UE_4
  64 ant., 8 RF chains    direct path (NLoS penalty: 20 dB)
       |
     [IRS]
  256 elements (16×16)
  SPDP: 64 sub-arrays (8×8)
  TTD + phase shifters
```

**Signal model** at user k, subcarrier m:

```
y_k[m] = (g_ru,k^H Φ[m] G[m] + g_bu,k^H) w_k[m] √P_k s_k     ← desired
        + Σ_{i≠k} (g_ru,k^H Φ[m] G[m] + g_bu,k^H) w_i[m] √P_i s_i   ← IUI
        + √P_{J,k} h_{J,k}^H z_k j_k                              ← jamming
        + n_k                                                       ← noise
```

**Optimization problem** — jointly maximize sum-rate subject to:
- Per-user QoS: SINR_k[m] ≥ γ_min for all k, m
- Total power budget: Σ P_k ≤ P_max
- Unit-modulus IRS elements: |Φ_mm| = 1
- Sub-connected analog precoder (block-diagonal, constant-modulus)

This is non-convex and NP-hard. We decompose it via a **three-block AO framework**:

| Block | Variable | Method |
|-------|----------|--------|
| 1 | Power allocation {P_k} | RL (42 discrete actions) |
| 2 | IRS phases {Φ[m]} | Closed-form AO (Eq. 13) |
| 3 | Hybrid beamformer F_RF, f_BB | SVD (analog) + MVDR (digital) |

Blocks 2 and 3 alternate 3 times per RL step at negligible cost.

---

## Algorithm: Fuzzy WoLF-PHC

**Action space** — 42 actions: 7 power fractions × 6 allocation modes (equal, channel-proportional, inverse-channel, SINR-deficit, water-filling, max-power). The RL agent picks power; AO handles IRS phases automatically.

**State** — 3 normalized features in [0,1]:

| Feature | Captures |
|---------|----------|
| f_pj | Jammer pressure (mean + max per-user jammer power) |
| f_ch | Channel quality (mean strength + spatial spread) |
| f_sinr | SINR health (mean + worst-user SINR vs. threshold) |

**Fuzzy aggregation** — each feature is mapped to 3 triangular memberships (centers 0, 0.5, 1.0), giving 3³ = **27 fuzzy state components** ψ_ℓ. This smooths Q-value estimates across nearby states.

**Fuzzy Q-value:**
```
FQ(s, a) = Σ_ℓ ψ_ℓ(s) · Q_ℓ(s, a)        (weighted sum over 27 fuzzy states)
```

**WoLF update rule** — learn faster when losing, slower when winning:
```
ξ = ξ_win = 0.01    if E_π[Q] > E_π̄[Q]   (currently winning)
    ξ_loss = 0.04   otherwise               (currently losing)
```
Policy update shifts probability mass toward the best action by step δ = ξ · ψ_ℓ, then projects back to the simplex. The average policy π̄_ℓ accumulates via exponential smoothing, forming the WoLF performance benchmark.

**Why this beats deterministic methods against a smart jammer:**  
A deterministic policy has predictability score η → 1 as the jammer observes enough actions. The jammer model (Eq. 25) adds up to +18 dB jamming power at η = 1 and aligns its precoder with the user channels. WoLF-PHC's mixed strategy keeps η low, cutting the jammer's exploit boost to ≤ 3.6 dB.

---

## Simulation Parameters

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Center frequency | f_c | 100 GHz |
| Bandwidth | B | 10 GHz |
| OFDM subcarriers | M_sc | 64 |
| BS antennas | N | 64 |
| RF chains | N_RF | 8 |
| IRS elements | M | 256 (16×16) |
| IRS sub-arrays (SPDP) | Q | 64 (8×8) |
| Users | K | 4 |
| Jammer antennas | N_J | 2 |
| Max TX power | P_max | 40 dBm |
| SINR threshold | γ_min | 5 dB |
| Noise figure | F_NF | 10 dB |
| Temperature | T | 290 K |
| RL action space | \|A\| | 42 |
| Learning rate | α | 0.01 |
| Discount factor | γ | 0.9 |
| WoLF win rate | ξ_win | 0.01 |
| WoLF loss rate | ξ_loss | 0.04 |
| Training episodes | E | 600 |
| Evaluation seeds | — | 5 |

---

## Reproducing Paper Figures

All figures can be regenerated from the pre-computed JSON data in under 60 seconds:

```bash
PYTHONPATH=src python scripts/generate_joint_ao_plots.py
```

To re-run the underlying simulations yourself:

```bash
# Main comparison (Table II + Fig. 1): ~30-60 min
PYTHONPATH=src python scripts/run_joint_ao_results.py

# Parameter sweeps (Figs. 2-5): ~8-10 hours
PYTHONPATH=src python scripts/run_journal_sweeps.py

# Regenerate all figures after any re-run
PYTHONPATH=src python scripts/generate_joint_ao_plots.py
```

| Figure | Description | Data source |
|--------|-------------|-------------|
| Fig. 1 (ieee_fig9) | Bar chart: rate & protection, all methods | `paper_results.json` |
| Fig. 2 (ieee_fig5) | Rate & protection vs. P_max | `sweep_pmax.json` |
| Fig. 3 (ieee_fig6) | Rate & protection vs. N_RIS | `sweep_nris.json` |
| Fig. 4 (ieee_fig7) | Rate & protection vs. SINR threshold γ_min | `sweep_sinr_target.json` |
| Fig. 5 (ieee_fig12) | Rate & protection vs. jammer power P_J | `sweep_pjammer.json` |
| Fig. 8 (ieee_fig8) | THz beam squint: array gain vs. frequency | Analytical |
| Fig. convergence (ieee_fig4) | Reward vs. training episode | `convergence_data.json` |

---

## Repository Structure

```
IRS-AntiJamming-THz/
│
├── src/irs_anti_jamming/           Core simulation package
│   ├── agents.py                   TabularQAgent, FastQAgent, FuzzyWoLFPHCAgent
│   ├── channel_model.py            Rician fading, ULA steering vectors, path loss
│   ├── system_model.py             SINR computation, MVDR beamformers, reward (Eq. 24)
│   ├── action_space.py             42-action hybrid space + AO IRS phase optimizer
│   ├── state.py                    3-feature normalization + fuzzy triangular memberships
│   ├── jammer.py                   Smart adaptive jammer (predictability-aware)
│   ├── environment.py              RL environment: action history, predictability score
│   ├── baselines.py                AOGreedyBaseline, NoIRSPowerOnlyBaseline
│   │
│   └── thz/                        THz wideband layer
│       ├── thz_config.py           THzSystemConfig, THzRLConfig, THzTrainEvalConfig
│       ├── thz_channel_model.py    Saleh-Valenzuela THz channel, near-field model
│       ├── thz_system_model.py     OFDM SINR, per-subcarrier evaluation
│       ├── thz_environment.py      THz RL environment (wraps channel + SPDP + HBF)
│       ├── thz_experiments.py      Training, evaluation, and sweep runners
│       ├── thz_action_space.py     42-action space for THz system
│       ├── thz_state.py            THz state aggregator
│       ├── spdp_ris.py             SPDP-RIS: beam-squint compensation, closed-form AO
│       ├── hybrid_beamforming.py   Sub-connected HBF, SVD analog precoder
│       ├── dqn_agent.py            DQN baseline (PyTorch or NumPy fallback)
│       └── d3qn_agent.py           Dueling D3QN
│
├── scripts/
│   ├── run_joint_ao_results.py     Train all 5 methods, save Table II data
│   ├── run_journal_sweeps.py       Parameter sweeps for all sweep figures
│   └── generate_joint_ao_plots.py  Generate all 10 IEEE figures from JSON
│
├── outputs_joint_ao/               Pre-computed results (5 seeds × 600 episodes)
│   ├── paper_results.json          Table II: rate & protection per seed + summary
│   ├── sweep_pmax.json             P_max sweep data
│   ├── sweep_nris.json             N_RIS sweep data
│   ├── sweep_sinr_target.json      SINR threshold sweep data
│   ├── sweep_pjammer.json          Jammer power sweep data
│   ├── sweep_sinr_cdf.json         SINR CDF data
│   ├── convergence_data.json       Training reward curves
│   ├── training_log.txt            Full training log from paper run
│   └── ieee_plots/                 10 figures × (PDF + PNG) = 20 files
│
├── paper/
│   ├── paper_ieee.tex              IEEE LaTeX source
│   └── paper.pdf                   Compiled 6-page manuscript
│
├── run_all.py                      Entry point: train + evaluate + plot
├── run_reproduce.sh                Shell entry point (portable)
├── requirements.txt
└── .gitignore
```

---

## Dependencies

```
numpy >= 1.24
matplotlib >= 3.8
scipy >= 1.10
torch >= 2.0       (optional — DQN falls back to a NumPy MLP if absent)
```

Python 3.11 or later is required. The code has been tested on Python 3.11 and 3.14.

Install:
```bash
pip install -r requirements.txt
```

For DQN with GPU acceleration, install PyTorch separately following [pytorch.org/get-started](https://pytorch.org/get-started/locally/).

---

## Citation

If you use this code or build on this work, please cite:

```bibtex
@article{singh2025irs,
  title   = {Intelligent Reflecting Surface Assisted Anti-Jamming
             Communications in {THz} Wideband Systems:
             A Fuzzy {WoLF-PHC} Learning Approach with Hybrid Beamforming},
  author  = {Singh, Anuprabh},
  journal = {arXiv preprint},
  year    = {2025},
  note    = {Code: \url{https://github.com/AnuprabhSingh/IRS-AntiJamming-THz}}
}
```

---

## References

The key prior works this builds on:

- **[Yang et al. 2021]** — IRS-assisted anti-jamming via fast RL (narrowband baseline this work extends)
- **[Su et al. 2023]** — Wideband precoding for RIS-aided THz communications (SPDP architecture)
- **[Bowling & Veloso 2002]** — WoLF-PHC: multiagent learning with variable learning rate
- **[Wu & Zhang 2019]** — IRS-enhanced wireless network via joint active and passive beamforming
