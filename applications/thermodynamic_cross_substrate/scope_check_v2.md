# Scope Check v2 — thermodynamic_cross_substrate

Reviewer: fresh Phase −0.5 agent, cold read of `proposal_v2.md`. No access to v1 or prior verdict.

## 1. Novelty — is the Harada–Sasa extension to discrete SGD actually new?

The headline theorem is an extension of Harada–Sasa (2005) from continuous-time overdamped Langevin to discrete-time SGD. I am sceptical this is unploughed ground. Direct competitors the authors will have to eat:

- **Yaida (2018), "Fluctuation–dissipation relations for SGD"** (ICLR). Explicitly derives FDT-style identities for discrete-time SGD using the stationary distribution under constant learning rate. This is essentially the same measurement object the authors propose.
- **Kunin, Sagastuy-Brena, Ganguli et al. (2020–2021), "Neural mechanics"** and follow-ups. Maps SGD onto a stochastic differential equation with a specific fluctuation–response structure; derives a discrete-time correction.
- **Goldt & Seifert (2017, PRL)** — cited by the proposal. Already computes an entropy-production rate for a perceptron learning rule. The proposal proposes to *verify against* this but does not explain what is left to prove after Goldt–Seifert gives the answer in closed form.

If the "extension" is really "write down Yaida's FDR, divide numerator by denominator, call it φ," there is no theorem. The proposal does not say what the new inequality, identity, or closed form actually is. "Depends only on the measured spectrum and response" is how Harada–Sasa is already stated; the discretisation correction is not obviously a new mathematical object.

## 2. Falsifiability — are the three kill-outcomes real?

Outcome 1 (continuous-time limit fails) is a **self-check of the derivation**, not an empirical test. If the author writes the theorem correctly, the limit holds by construction. It cannot kill the paper; at worst it kills a draft of the proof. Border-tautological.

Outcome 2 (perceptron analytical agreement) is a genuine numerical check but, again, is a check that the authors did their algebra right — not a test of a physical claim.

Outcome 3 (ribosome calibration within 0.5) is the only one that could genuinely fail on empirical grounds. But "0.5" on a dimensionless fraction in [0,1] is enormous tolerance; φ = 0.4 vs φ = 0.9 would pass. This is weak.

The headline cross-substrate comparison — "two φ values measured under a shared protocol" — has **no kill condition**. The proposal explicitly disclaims it: "whether the two numbers are numerically close is itself a falsifiable empirical claim, not a theoretical one." Fine, but no threshold is given. Unfalsifiable in disguise.

## 3. Venue fit

PRE does publish Harada–Sasa extensions and SGD-as-thermodynamics papers. The framing fits. JSTAT fallback is plausible. No objection here — *if* the theorem is actually new.

## 4. Killer objections a real PRE reviewer will raise

1. **"This is Yaida 2018 with new notation."** The proposal does not differentiate from existing FDR-for-SGD work. A PRE reviewer will find Yaida in ten seconds.
2. **"Two data points is not a cross-substrate result."** One ribosome number (recovered, by design, from Kempes) and one training-run number is a demonstration, not evidence of a universal protocol. The headline claim is underpowered.
3. **"The Kempes re-extraction is circular."** If the calibration is designed to recover the published number, passing it is not evidence of anything.

VERDICT: REFRAME
