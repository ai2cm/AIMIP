# Which ACE recipe should we submit?

Working notes, 2026-08-26 to 2026-09-02.

We have an atmosphere emulator, ACE, in two generations. The newer one (ACE2.2) beat the
older one (ACE2.1) on most measures, but it changed about seven things at once, so we could
not say which changes mattered. This is a record of training four more models to find out,
and of what we decided as a result.

**In one paragraph.** Two of the seven differences were worth testing. The first — training
on a different span of years — turned out not to matter, so we can drop it and describe the
experiment more simply. The second — letting the model carry near-surface temperature and
wind in its own state, rather than reconstructing them afterwards — matters a great deal, so
it stays. Along the way we found that the newer recipe is far more sensitive to its random
starting point than the old one, which has consequences for how many models we need to train.

---

## The vocabulary

Five terms carry most of the report.

**Emulator.** A neural network trained to reproduce the atmosphere's behaviour, given sea
surface temperatures as input. It is far cheaper to run than a physics-based climate model.

**Rollout.** Letting the emulator run forward freely for years, feeding its own output back
in as the next input. Errors compound, so a long rollout is a demanding test.

**Prognostic vs. diagnostic.** A *prognostic* field is part of the model's own evolving
state — the model predicts it, then reads it back the next step. A *diagnostic* field is
reconstructed afterwards from the state, by a small separate network, and never fed back.
Prognostic fields participate in the physics; diagnostic ones are read off it.

**Seed.** The random number that initialises the network before training. Two models trained
identically but from different seeds end up different. How different is a property of the
recipe, and it turns out to matter here.

**The four models.**

| name | what it is | changes vs ACE2.2 |
|---|---|---|
| **ACE2.1** | the older generation, already submitted to the AIMIP intercomparison | ~7 |
| **ACE2.2** | the newer generation; better overall, and the model we would otherwise submit. One seed. | — |
| **P1** | ACE2.2's recipe with ACE2.1's choice of training years. Three seeds. | 1: the training years |
| **P2** | P1, *plus* near-surface fields made diagnostic instead of prognostic. One seed. | 2: the training years **and** the near-surface treatment |

**The variants form a chain, not a fan:** ACE2.2 -> P1 (change the training years) -> P2 (also
deprognostify the near-surface fields). P2 was built on P1 rather than directly on ACE2.2 so
that it would have a three-seed spread to be judged against, since ACE2.2 has only one seed.
The consequence is that P1, not ACE2.2, is the only clean control for the near-surface
question -- comparing P2 to ACE2.2 conflates the two changes. Everywhere else in this report
ACE2.2 is the reference, since it is the model the variants were trying to improve on.

---

## What we tested

Two questions, each isolating one difference between the generations.

**1. Does the choice of training years matter?** ACE2.2 trained on 1979–2013; ACE2.1 on
1979–2008 with 2009–2014 held back for checking. The shorter span is cooler and contains less
of the warming trend, which we expected to hurt. P1 answers this.

**2. Do near-surface fields need to be part of the model's state?** ACE2.2 made 2 m
temperature, 2 m humidity and the 10 m winds prognostic. ACE2.1 reconstructed them afterwards.
P2 answers this.

## How we measured

Every model ran the same 36-year rollout, 1979 to 2014, started from eight days in January
1979 and compared against the ERA5 reanalysis. Three choices need explaining.

**This period is in-sample.** 1979–2014 is training or validation data for every model here,
so these numbers rank configurations against each other — they are not a test of
generalisation. The genuine held-out period is 2015–2024, which the intercomparison scores
and which is deliberately untouched by every decision in this report.

**Two complementary measures.** *Time-mean error* asks whether the model's average climate is
right. *Annual-mean error* asks whether it gets each year right, so it carries the long-term
trend as well as year-to-year swings. A model can do well on one and badly on the other, and
in the intercomparison they are scored separately.

**Errors are combined as median per-field ratios**, and the top model layer is excluded. Both
choices matter enough to state plainly: the obvious alternative — averaging each field's
error after dividing by that field's variability — is dominated by whichever fields vary
least naturally. Here that is the top of the atmosphere, where ACE has a known moisture-drift
problem: ACE2.2's top-layer humidity error is 4.3× ACE2.1's, and on its own it flips the sign
of the headline comparison. Comparing field by field and taking the median avoids letting four
fields out of 28 decide the answer.

---

## What we found

### The training span does not matter

![Time-mean error](figures/fig1-overall-skill.png)

P1 uses ACE2.1's training years and ACE2.2's everything-else. If the shorter, cooler span
were a real handicap, P1 would sit clearly worse than ACE2.2. It does not — ACE2.2 lands at
0.977 against a P1 three-seed average of 0.990, well inside the range P1's own seeds produce
(0.879–1.088). The same holds for annual-mean error, and for surface temperature, 2 m
temperature and El Niño response taken individually.

**On these two measures we can adopt ACE2.1's training split** — the experiment gets simpler
to describe at no measured cost in mean climate or annual error. What we *cannot* say is that
the span provably has no effect: with three seeds the measurement cannot resolve anything
smaller than the seed spread.

**And the trend is a real exception**, treated in its own section below. There P1's average
falls between the two generations rather than matching ACE2.2, in the direction predicted for
a shorter, cooler training period. That is why this conclusion is scoped to the two error
measures rather than stated as a general verdict on the split.

### The newer generation is better in-sample, as expected

Both figures put ACE2.1 at the worse end: 1.121 on time-mean error, the highest of the six
models, against 0.977 for ACE2.2 and 0.990 for the P1 average. That is consistent with the
full intercomparison evaluations, which ranked ACE2.2 first of nine participants on most
surface fields.

On annual-mean error the picture is closer — ACE2.1 0.982 against ACE2.2 0.956 and a P1
average of 0.982 — so the newer generation's advantage is clearer in the mean climate than in
year-to-year and long-term variation.

![Annual-mean error](figures/fig2-annual-error.png)

One caveat specific to this period. Being in-sample favours ACE2.1 in a particular way: it was
trained with a deterministic objective, which reproduces the specific weather that actually
happened rather than a plausible sample of it. Its clear win on El Niño response here
(0.104 against 0.128–0.130) is likely this effect, and it does not carry over to the held-out
decade, where the two are level.

### The trend, in the familiar view

![Global-mean temperature by year](figures/fig6-tas-timeseries.png)

The scalar annual-mean error compresses a whole time series into one number, so here is the
series itself — global-mean 2 m temperature, year by year, over the in-sample period. These
are the same rollouts as every other figure in this report, so all six models appear and none
of them carries the forcing-convention offset the production simulations do.

| | trend | share of observed | mean offset | annual error |
|---|---|---|---|---|
| ERA5 (observed) | 0.156 K/decade | — | — | — |
| ACE2.2 | 0.079 | **51%** | +0.059 K | 0.118 |
| P1 seed 0 | 0.073 | 46% | −0.034 K | 0.111 |
| P1 seed 2 | 0.070 | 45% | +0.005 K | 0.110 |
| P2 | 0.068 | 44% | +0.010 K | 0.113 |
| ACE2.1 | 0.056 | **36%** | +0.054 K | 0.139 |
| P1 seed 1 | 0.050 | 32% | +0.005 K | 0.136 |

**Every model warms too slowly**, reproducing between a third and half of the observed
in-sample trend. That is the single most visible feature of the figure and it is common to
both generations.

**ACE2.2 reproduces the most of it and ACE2.1 the least** — 51% against 36%. This is the
in-sample counterpart of the forced-response gap seen in the intercomparison, and it is
consistent with the leading explanation for it: ACE2.2 has an explicit global-mean pathway
that ACE2.1 lacks.

**P1 does not inherit all of that advantage.** Averaging its three seeds — 46%, 45% and 32%
— gives 41%, which falls between ACE2.1's 36% and ACE2.2's 51%. Since the training span is
the *only* difference between P1 and ACE2.2, the span is the natural explanation, and the
direction is the one predicted for a shorter, cooler period. Taking the two generations'
15-point difference as the whole effect, P1 retains about a third of it: (41 − 36) / (51 − 36).

**That fraction is a point estimate and should be read as one.** P1's three seeds span 32% to
46% — a range wider than the 15-point gap being divided — so the same arithmetic gives two
thirds if the weakest seed is excluded. Both endpoints are single seeds with no spread of
their own. The ordering is the finding; the fraction is an illustration of its size, not a
measurement of it, and resolving it would take several more seeds rather than one.

**The same ordering appears in four other fields**, so it is not an artifact of 2 m
temperature alone. Repeating the calculation on each field's annual series:

| field | P1 three-seed mean | ACE2.2 | z |
|---|---|---|---|
| 2 m temperature | 41% | 51% | +1.28 |
| surface temperature | 54% | 61% | +1.61 |
| 850 hPa temperature | 44% | 55% | +1.15 |
| 500 hPa height | 37% | 44% | +1.01 |
| precipitation rate | 126% | 140% | +2.02 |

**This is suggestive, not established, and the field count is misleading.** Every P1 seed
falls below ACE2.2 in every field, which is fifteen comparisons -- but they are not fifteen
tests. A model's fields are strongly correlated with one another, so a single model that
draws well scores well on all of them at once; the near-surface section below shows exactly
that happening in the other direction. The independent dimension is the seed, and there
ACE2.2 is one draw against P1's three. Under the null that all four are exchangeable, the
probability that ACE2.2 is the largest is 1/4, and five correlated fields do not compound it.
ACE2.2's configuration has one seed, so the comparison has no spread on that side at all.


**The offsets are small here**, between −0.034 and +0.059 K, where the production simulations
of the same two generations run +0.11 K and +0.19 K warm. That difference is the
forcing-convention effect described in the appendix: these rollouts are driven by the same
skin temperature the models trained on, while the production runs prescribe sea surface
temperature, which is warmer over ocean. It is a useful confirmation that the offset is a
forcing artifact rather than a model bias.

### Near-surface fields must stay in the model's state

![Near-surface penalty](figures/fig3-near-surface-penalty.png)

P2 reconstructs the four near-surface fields afterwards instead of evolving them. Over the
36-year rollout they get 2.1–2.9× worse — far outside anything the seeds produce, so this is
a real effect and the clearest result in the campaign.

**ACE2.1 itself confirms it independently.** P2 was built to imitate ACE2.1's treatment of
these fields, and it lands on ACE2.1's actual numbers to within 10%:

| relative to ACE2.2 | 2 m temperature | 2 m humidity | 10 m eastward | 10 m northward |
|---|---|---|---|---|
| P2 (our variant) | +132% | +242% | +67% | +120% |
| ACE2.1 (the real model) | +156% | +210% | +79% | +143% |
| P1 (prognostic, ACE2.1's span) | -7% | +17% | -20% | -19% |

So the penalty is not an artifact of how P2 was implemented; it is the real generational
difference, measured two ways that share no code path. The third row is the control: P1 keeps
these fields prognostic while adopting ACE2.1's training span, and matches or beats ACE2.2 on
three of the four. The treatment is what matters, not the span.

The penalty grows with rollout length: on a five-year window 2 m temperature was 1.4× worse,
over 36 years it is 2.5×. That fits the mechanism, since a reconstruction network reading a
frozen state has no boundary-layer memory to carry forward, so the deficit compounds.

Three checks confirm it is not undertraining. P2's error curve has flattened, so more training
would not close it. P1's near-surface fields are already at final accuracy after two epochs,
because they were trained as part of the model rather than fitted at the end. And P2's own
state is *not* worse than P1's on the fields physically adjacent to 2 m temperature — the
information is there; the small reconstruction network cannot read it out as accurately as
evolving the field directly.

The cost is not confined to those four fields. Pressure levels near the ground, which the
intercomparison also scores, are about 9% worse in P2, while levels above 250 hPa are
unaffected. The deficit is graded by height.

**P2 is not better on the fields it did not change.** Removing four fields from the model's
state might have freed capacity for everything else, which would argue for some gentler
version of the change. Scored against ACE2.2 -- the model both variants modify -- P2 does look
better on the 30 fields it left alone:

| relative to ACE2.2 | 30 unchanged fields | better | near-surface |
|---|---|---|---|
| P1 seed 0 | 1.029 | 12/30 | 0.90x |
| P1 seed 1 | 0.835 | 22/30 | 0.74x |
| P1 seed 2 | 1.057 | 13/30 | 1.00x |
| P2 | 0.887 | 20/30 | 2.26x |

Two things dissolve it. P1 seed 1 reaches 0.835 with near-surface fields fully prognostic, so
scoring well across nearly every field is a whole-model property the seed alone produces;
with P2 at one seed its 20-of-30 count is one draw, not 20 tests, and against a seed spread of
0.121 it sits at z = -0.72. And the surface energy fluxes, where a mechanism would plausibly
live since the turbulent fluxes read 2 m temperature, humidity and the 10 m winds directly,
do not support one either: P2 beats ACE2.2 on only 4 of 8, and its apparent flux advantage
appears only against P1, which is itself worse than ACE2.2 there. P2 was recovering something
the split change cost, not improving on the model it started from.

The comparison in the figure above uses P1 rather than ACE2.2 as its reference, because P2
differs from ACE2.2 in two ways -- the training span and the near-surface treatment -- and
only P1 isolates the second.


### The top of the model drifts, and it is a seed lottery

![Top-layer drift](figures/fig5-top-layer-drift.png)

The aggregation problem above pointed at something worth reporting in its own right. At the
top model layer the newer models are much worse than ACE2.1 — but not consistently, and not
everywhere.

| relative to ACE2.1 | top-layer humidity | top-layer eastward wind |
|---|---|---|
| ACE2.2 | 4.33× | 3.82× |
| P1 seed 0 | 3.04× | 4.23× |
| P1 seed 1 | 1.48× | 1.09× |
| P1 seed 2 | 1.00× | 1.81× |
| P2 | 1.21× | 2.03× |

Three things stand out. The problem is **confined to the top layer** — one level down and
below, the newer models match or beat ACE2.1, and at the lowest layer ACE2.2 is 33% better.
It is **strongly seed-dependent**: P1's median seed-to-seed variation is 56% at the top layer
against 19% below it, and seed 2 lands at parity with ACE2.1 while seed 0 is three times
worse. And ACE2.1 shows the same instability for humidity and wind (49% and 60% across its
four seeds), so this is a longstanding weak spot the newer recipe has made worse on average
rather than a new failure.

Two consequences. **ACE2.2's top-layer drift is probably a bad draw, not inherent** — the same
recipe at seed 2 reaches ACE2.1's level, so the published figure reflects one seed rather than
the recipe's capability. And **it belongs in the seed-selection criteria**: because it is
confined to one layer, an aggregate over all fields either buries it or, if the aggregate is
unweighted, is swamped by it. Neither is useful. It should be checked as its own number.

### The random seed matters about equally in both recipes

![Seed spread](figures/fig4-seed-spread.png)

We checked whether the newer recipe — which trains against a probabilistic objective with
injected noise — is more sensitive to its random starting point than the older deterministic
one. It is not, as far as three and four seeds can tell: spreads of 11% and 9% of their
respective means, a variance ratio of 1.6, p = 0.69. The exception is the top model layer
above, where seed variation is several times larger in both recipes — the instability is
localised, not general.

This matters mainly because it is easy to get wrong. An earlier version of this analysis, using
the average-of-normalised-errors described above, put P1's spread at 27% against ACE2.1's 10%
and concluded the newer recipe was three times more seed-sensitive. That was the top-layer
artifact, not a property of the models.

---

## What we decided

**Near-surface fields stay prognostic.** This is the campaign's one decisive result, and it
holds whatever else is chosen.

**The training span is unresolved, and P1 is no longer the presumed submission.** P1 adopts
ACE2.1's span, which costs nothing on mean climate or annual error; but on reproduced
in-sample trend every P1 seed falls below ACE2.2, at p = 1/4 under exchangeability. That is
too weak to act on and too consistent to ignore, and it bears on E2, which the intercomparison
scores. The blocking gap is that ACE2.2 has a single seed, so its 51% may itself be a high
draw, and nothing in this round measures that.

**P2 is not adopted.** Its near-surface penalty is disqualifying for an intercomparison that
scores exactly those fields, and the compensating benefit it appeared to bring elsewhere did
not survive: measured against ACE2.2, P2's unchanged fields land inside the seed spread, and
P1 seed 1 improves on ACE2.2 by more than P2 does without touching the prognostic set.

**A fourth P1 seed remains open, and would not settle the trend question.** It narrows P1's
three-seed average only modestly, where the trend result needs several more seeds to resolve;
and seed selection cannot mitigate the loss in any case, since seeds sample around a mean the
configuration sets, and choosing the best-trend seed would mean tuning to a scored
intercomparison metric. The remaining argument is protocol symmetry with ACE2.1's best-of-four,
worth about 2% on the error measures.

## What we still do not know

- **Whether the training span costs trend skill, and how much.** P1's average falls between
  the two generations as predicted, and the ordering repeats across five fields, but ACE2.2 is
  a single draw and the fields are correlated, so the evidence stands at p = 1/4. This is the
  campaign's least resolved question, and the one with the clearest next measurement.
- **Why the top model layer drifts at all.** We established that it is confined to one
  layer, seed-dependent, and present in both recipes, but not what causes it. ACE has a known
  moisture-drift problem there; this quantifies it without explaining it.
- **Whether removing near-surface fields helps the core at all.** Measured against ACE2.2,
  P2's core lands inside the seed spread (z = -0.72), so the earlier suggestion that those
  fields "clutter" the model is unsupported by this evidence either way. Answering it would
  need seeds of the deprognostified configuration, which has one.
- **How much of any single model's score is its seed.** With ~12% seed spread and one seed
  each, ACE2.1's and ACE2.2's published numbers carry an unquantified uncertainty of that size.

---

# Technical appendix

Everything below is the working record: the original hypotheses, the runs, and the caveats
that apply to the intercomparison scores rather than to the decisions above.

## Measurement details

All models evaluated at the checkpoint their own training selected, on an eight-member
36-year rollout, one evaluation each, identical config and aggregator. ACE2.1 is scored
against the 2024-06-20 ERA5 build because its checkpoints reject the 2026-03-19 one -- the
vertical coordinate coefficients differ slightly between builds, and the difference is
numerically tiny.

| model | run | stage | fields |
|---|---|---|---|
| ACE2.1 RS3 | `long36-ace21-plevft` | plev FT | 35 |
| ACE2.2 | `long36-ace22-stage2` | 2 | 34 |
| P1 seeds 0/1/2 | `long36-p1-rs0/1/2` | 2 | 34 |
| P2 | `long36-p2-rs0` | 2 | 30 |
| P2 | `long36-p2-stage3` | 3 | 34 |

ACE2.1's run uses the pressure-level fine-tuned checkpoint, translated to the current config
schema; it is the submitted ACE2.1 model and the only one carrying near-surface fields. On all
28 fields it shares with the earlier `long36-ace21-rs3` backfill it reproduces that run exactly
(ratio 1.0000, range 1.000-1.000), which both validates the translation and confirms ACE2.1 is
deterministic -- noise conditioning is an ACE2.2 feature.

Aggregates use the fields common to all models compared, minus the top model layer, scored as
median per-field ratios. They also exclude the four near-surface fields **by choice**, not for
lack of data: those carry the campaign's largest effect and are reported on their own above, so
folding them into a cross-model average would double-count the same finding. Near-surface figures come from the 36-year rollout; the five-year
figure quoted for contrast is the 2009-2014 inline evaluation at stage 3, restricted to epochs
>= 8 where P2's reconstruction network has converged.

**Two known contaminants, neither re-run.** Both apply to ACE2.2, P1 and P2 only; ACE2.1 is
deterministic, as its two independent backfills reproducing each other exactly demonstrate.
These rollouts are unseeded --
`InferenceEvaluatorConfig` has a `seed` field the configs do not set -- so each draws its own
noise from these noise-conditioned models. Comparing P2's stage-2 and stage-3 runs on the 30
fields they share, which should differ only in the decoder, gives a 2.7% median difference.
Differences below roughly that size are not resolvable here. Part of that 2.7% is a second
effect: with `clip_latent_global_means: true` the latent global-mean envelope is a registered
buffer tracked during training and reset each epoch, which `parameter_init: frozen` does not
hold, so a stage-3 checkpoint's eval behaviour differs from its stage-2 parent even though the
weights are identical.

## Statistics behind the seed claim

Each seed scored as the median per-field ratio against the seven-model average, 24 fields,
top model layer excluded.

| | seeds | ICs | values | CV |
|---|---|---|---|---|
| ACE2.1 | 4 | 1 | 1.219, 1.113, 0.984, 1.064 | 9.0% |
| P1 | 3 | 8 | 0.918, 0.787, 0.985 | 11.2% |

Variance ratio 1.56 on df (2,3), two-sided p = 0.69 -- indistinguishable. ACE2.1's single-IC
figure bounds its seed spread from above, since ensemble averaging can only reduce it, so the
comparison is if anything conservative against the null.

On selection: expected best-of-N improves by E[Z(N)] x sd, so a fourth P1 seed is worth about
0.18 sd, roughly 2% of the mean. P1's expected best-of-3 still beats ACE2.1's expected
best-of-4 because P1's mean is better, not because its spread is wider.

**Superseded.** An earlier version of this section aggregated by averaging normalised errors
across fields, giving CVs of 26.7% and 9.7%, a variance ratio of 6.2, and a claim that the
newer recipe is markedly more seed-sensitive. That was driven by the top model layer -- see
"How we measured" -- and does not survive a robust aggregate. The same artifact produced an
earlier headline that ACE2.2 was 40% worse than ACE2.1, and an apparent core advantage for P2.

## Standing hypotheses

| # | hypothesis | explains | status / evidence |
|---|---|---|---|
| 1 | `global_mean_removal` gives ACE2.2 a global-mean pathway ACE2.1 lacks | E5 forced response, E2 trends, part of E1 on the warm test decade | supported: ACE2.2 reproduces 50% of ERA5's observed warming (+0.316 of +0.625 K, 2015–2024 vs 1979–2008) and warms +2.00 K under +4 K SST; ACE2.1 reproduces 31% of observed warming but only +0.275 K under +4 K, i.e. it responds to patterned warming and barely at all to a uniform shift. Both models reproduce the same fraction of observed warming inside and outside their training spans. ENSO's global-mean temperature signal is transmitted in full (no uniform component in the E3 coefficient error), so the shortfall is specific to low-frequency shifts. **Confounded with the longer training period** (1979–2013 vs 1979–2008). The size of that confound is not established: a regression-attenuation estimate gave ~7 percentage points, but attenuation describes noise in the *predictor*, and here time and the prescribed SSTs are exact, so the framing does not apply. Only the sign is robust — a shorter, cooler span should not *increase* the fraction reproduced. **Measured by P1:** on mean climate and annual error the span costs nothing. On reproduced in-sample trend P1's three-seed mean (41%) falls between ACE2.1 (36%) and ACE2.2 (51%) — the predicted direction, retaining roughly a third of the generational difference as a point estimate, but with P1's seeds spanning 32-46% the size is not resolved at n=3. So part of what this hypothesis attributes to `global_mean_removal` may belong to the training span; see the trend section |
| 2 | Multi-step fine-tuning + larger trunk improved the core; near-surface fields additionally gained from becoming prognostic/jointly trained | E1: head-vs-head plev fields −10–18% (core share); near-surface fields −25–31% | **confirmed for the near-surface half**, twice over: reverting those fields to stage-3 secondary diagnostics (P2) costs 67–242% on the 36-year rollout, and ACE2.1's own plev-FT checkpoint carries the same penalty (79–210%) within 10% of P2's. P1 holds those fields prognostic on ACE2.1's span and matches ACE2.2, so the gain is the treatment and not the span. FT vs architecture still not separated for the core half |
| 3 | CRPS + noise conditioning preserves variance that MSE damps | E4 daily variability (tas −19%, pr −9%) | plausible, untested |
| 4 | ACE2.1's in-sample E3 temperature advantage is deterministic reproduction of the realized training-period responses (shared sampling noise with the ERA5 reference), plus a best-of-4-seed winner's curse | E3 tas/ts regression | supported: confined to 1979–2014 (parity on 2015–2024); entirely in the pattern component; magnitude tracks boundary-forced reproducibility (ts > tas > ta > hus > ps > winds); winds/pr improve in all periods |
| 5 | Multi-step fine-tuning damps the low-frequency global-mean mode, buying rollout stability at some cost in forced response | the ~50% shortfall in both E5 and E2 metrics | open. The stage-1 probe has a *larger* +4 K response (+2.68 vs +2.00 K) but an incoherent historical trend and a detrended interannual global-mean tas spread of 0.455 K against ERA5's 0.122 K, so what fine-tuning removes may be undamped variance rather than usable signal. The final model ends up under-dispersed (0.054 K), consistent with over-damping. Discriminator, free from the campaign: across P1's three seeds a real trade predicts the lowest-bias seed has the weakest +4 K response; noise suppression predicts no relation |

## Refuted

- Prognostic-vs-diagnostic near-surface fields as the E5 driver (frozen head passes 84% of the core response)
- The same, or stochastic estimation noise, as the E3 driver (head-vs-head fields also regress; ACE2.2's member spread is smaller)
- Mean-channel damping of ENSO's global-mean pulse (uniform share of the E3 coefficient error: 0.0%)
- Training-span proximity effects (each model reproduces the same fraction of observed warming inside and outside its own training span: ACE2.1 41%/40%, ACE2.2 59%/52%)
- `residual_prediction` and CO₂ input as configuration differences (neither differs)

## Forcing-convention caveat on the AIMIP production runs

Both ACE2.1 and ACE2.2 train on `surface_temperature` from the ERA5 store, which is raw ERA5
skin temperature (`long_name: Skin temperature`, `short_name: skt`) in both the 2024 and 2026
builds — the SST-over-ocean merge is applied by ACE at run time via `OceanConfig`
(`interpolate: false`), not baked into the dataset. The AIMIP forcing prescribes actual SST,
which runs ~0.5 K warmer than skin over ocean.

So every AIMIP production run of either model is forced ~0.5 K warm over ~71% of the surface
relative to training — roughly 0.35 K in the global mean. Scaled by each model's own transfer
gain (ACE2.2 +2.00 K per +4 K, ACE2.1 +0.275 K), that is ~0.18 K of warm bias for ACE2.2 and
~0.02 K for ACE2.1: the model with a working mean channel inherits the offset, the inert one is
shielded from it. Applies only to the 15 AIMIP simulations and therefore to E1–E5; the inline
`long_36year` / `5year_outsample` entries and the backfill runs are forced from the training
store and are convention-matched.

## Discriminating tests (not run)

1. ~~Stage-1-checkpoint inference~~ — **run 2026-08-28; the pretrain-only checkpoint is not a
   usable stand-in.** Its +4 K response is larger (+2.68 K) but its time-mean bias is 65–222%
   worse on every near-surface field, its warming reproduction is incoherent (+130% in-sample,
   −317% on 2015–2024), and its detrended interannual global-mean tas spread is 0.455 K against
   ERA5's 0.122 K. Variants must be evaluated after all three stages.
2. Span-matched retrain (ACE2.2 recipe on 1979–2008): the training period's share of the observed-warming fraction.
3. Channel-ablated retrain (no `global_mean_removal`, 1979–2013): prediction — the +4 K uniform
   response collapses much more than the patterned historical warming, reproducing ACE2.1's
   asymmetry (31% of observed warming reproduced, but only +0.275 K under +4 K SST).
