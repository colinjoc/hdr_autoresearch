# Scope check — diffusion_crooks_benchmark (Phase −0.5)

Reviewer mood: grouchy. Conflicts of interest: none.

## 1. Novelty

Not as clean as the proposal implies. The diffusion-as-nonequilibrium-thermodynamics identification is the *defining content* of Sohl-Dickstein 2015 — the ELBO per step IS the stepwise work increment in that paper, and annealed-importance-sampling-style Jarzynski checks have been done in similar score/energy-based generative contexts. Close comparators:

- **Sohl-Dickstein et al. 2015** already writes the ELBO as a Jarzynski-style trajectory average. They stop short of a histogram-level Crooks test but the identification you propose in §2(b) is *theirs*, not novel.
- **Jarzynski/Neal annealed importance sampling literature** (Neal 2001; Grosse et al. 2013; Masrani/Wu/Wood "Thermodynamic Variational Objective" 2019) — these explicitly test ⟨exp(−βW)⟩ = exp(−βΔF) on trained latent-variable models. The proposal does not cite them.
- **Boyd, Crutchfield, Gu 2022** — cited, but their "max-work = max-likelihood" result already *derives* what the proposal claims to empirically verify. Verifying a theorem on an optimised model is a consistency check, not a discovery.

So the "first empirical Crooks test on DDPM" framing is technically defensible only because nobody bothered plotting the histogram. That is a weak novelty claim.

## 2. Falsifiability of the three kill-outcomes

Shaky. The ELBO-to-work map in §2(b) is *assumed*, not derived in the proposal. If the mapping is simply "W_step := −log p + log q" then:

- Jarzynski ⟨exp(−βW)⟩ = exp(−βΔF) is **mathematically identical** to the ELBO inequality being tight, which is *guaranteed* for a well-trained DDPM up to the training gap. Outcome 1 is near-tautological.
- Crooks ratio linearity (outcome 2) is equivalent to the forward/reverse KL symmetry the model was *trained to enforce*. Again largely tautological.
- Outcome 3 is the definition of the ELBO. Circular.

These are consistency checks disguised as falsifiable predictions. A genuine test would vary β (requires a real temperature parameter in the SDE, not a free knob), or compare an *under-trained* DDPM where the identity should *fail* quantitatively — the proposal does not commit to this.

## 3. Venue

NJP is a stretch. NJP wants physics content; a consistency check between two already-equivalent formalisms on a toy CIFAR-10 DDPM reads as ML-methods. **TMLR is the honest primary target.** Entropy or JSTAT are other physics-adjacent fallbacks. Pitching NJP primary invites desk rejection for "insufficient physics novelty".

## 4. Killer objections

1. "This is a graphical restatement of the ELBO." (Lethal.)
2. No independent β — the temperature is set by training, so Crooks is untestable as a *fluctuation* relation; it is tested only at one point.
3. Comparators in Masrani 2019 / Grosse 2013 pre-empt the empirical novelty.
4. Scaling claim is absent: why CIFAR-10 T=1000 rather than a 1-D toy where analytic ΔF is known?

VERDICT: REFRAME
