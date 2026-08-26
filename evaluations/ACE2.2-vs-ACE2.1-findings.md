# ACE2.2-ERA5 vs ACE2.1-ERA5: hypotheses for the E1–E5 differences

Exploratory analysis, 2026-08-26, from the regenerated 9-participant caches
(`v20260825` outputs). Working notes, not notebook results.

## Standing hypotheses

| # | hypothesis | explains | status / evidence |
|---|---|---|---|
| 1 | `global_mean_removal` gives ACE2.2 a global-mean pathway ACE2.1 lacks | E5 forced response (0.28→2.00 K per +4 K), E2 trends, part of E1 on the warm test decade | supported: gains constant across training boundaries; ACE2.2's historical gain (0.50) ≈ its +4 K gain (0.48); ACE2.1 responds to patterned warming (0.31) but not uniform (0.07). Gain is frequency-dependent: ~1.0 interannual, ~0.5 secular. **Confounded with the longer training period** (1979–2013 vs 1979–2008), plausibly worth +0.1–0.15 of gain by itself |
| 2 | Multi-step fine-tuning + larger trunk improved the core; near-surface fields additionally gained from becoming prognostic/jointly trained | E1: head-vs-head plev fields −10–18% (core share); near-surface fields −25–31% | supported circumstantially by the field-class split; FT vs architecture not separated |
| 3 | CRPS + noise conditioning preserves variance that MSE damps | E4 daily variability (tas −19%, pr −9%) | plausible, untested |
| 4 | ACE2.1's in-sample E3 temperature advantage is deterministic reproduction of the realized training-period responses (shared sampling noise with the ERA5 reference), plus a best-of-4-seed winner's curse | E3 tas/ts regression | supported: confined to 1979–2014 (parity on 2015–2024); entirely in the pattern component; magnitude tracks boundary-forced reproducibility (ts > tas > ta > hus > ps > winds); winds/pr improve in all periods |

## Refuted

- Prognostic-vs-diagnostic near-surface fields as the E5 driver (frozen head passes 84% of the core response)
- The same, or stochastic estimation noise, as the E3 driver (head-vs-head fields also regress; ACE2.2's member spread is smaller)
- Mean-channel damping of ENSO's global-mean pulse (uniform share of the E3 coefficient error: 0.0%)
- Training-span proximity effects (trend gains flat across every boundary)
- `residual_prediction` and CO₂ input as configuration differences (neither differs)

## Discriminating tests (not run)

1. Stage-1-checkpoint inference (2 jobs): separates multi-step FT from the rest; is the ~0.5 secular gain already present after pretraining?
2. Span-matched retrain (ACE2.2 recipe on 1979–2008): training-period share of the gain.
3. Channel-ablated retrain (no `global_mean_removal`, 1979–2013): prediction — uniform response collapses more than patterned, reproducing ACE2.1's 0.31/0.07 asymmetry.
