# Feature Candidates -- Domain Theory to Computable Proxies

*Maps domain-theory quantities to features computable from available signals (or their derivatives/combinations). This is the key bridge document between literature review and experiments.*

## Available Signals

| Signal | Physical / Scientific Meaning | Units | Type |
|--------|------------------------------|-------|------|
| [feature_1] | [description] | [units] | continuous / categorical |
| [feature_2] | ... | ... | ... |

## How to Add Candidates

For each candidate derived feature, document:

1. **Physics/domain quantity**: What theoretical concept does this capture?
2. **Why it matters**: How does this relate to the prediction target? What mechanism?
3. **Proxy from available signals**: The exact computation using your feature columns.
4. **Priority**: HIGH / MEDIUM / LOW with justification.
5. **Hypothesis link**: Which research queue question (Q#) tests this feature?

---

## Candidate Derived Features

### 1. [Feature Name]

**Domain quantity**: [What theoretical quantity this captures]
**Why it matters**: [Mechanism linking this to the prediction target. Cite literature.]
**Proxy from available signals**: [Exact computation, e.g., `feature_a / feature_b` or `finite_diff(feature_c, window=10)`]
**Priority**: [HIGH/MEDIUM/LOW] (Q#)

### 2. [Feature Name]

...

---

## Time-Series Feature Candidates (if applicable)

*These features capture temporal dynamics that tree models cannot access from single-timestep values.*

### Derivatives at Multiple Scales

**Why it matters**: Rate of change is often more predictive than absolute value. Different processes evolve on different timescales.
**Proxy**: For key signals, compute `(x[t] - x[t-w]) / w` at windows of [short], [medium], [long] timesteps.
**Feature count**: [N signals x M windows] features

### Rolling Statistics (Mean, Std)

**Why it matters**: Rolling mean captures trend; rolling std captures volatility/instability.
**Proxy**: For key signals, compute rolling mean and std over [short], [medium], [long] windows.
**Feature count**: [N signals x 2 stats x M windows] features

### Lag Features

**Why it matters**: Tree models have no temporal awareness. Lag features are the only way they access historical context.
**Proxy**: For each signal, include values at t-1, t-5, t-10, t-20, t-40, t-100.
**Feature count**: [N signals x L lags] features

### Interaction Features

**Why it matters**: Products/ratios of signals capture domain-specific compound indicators that tree models cannot learn from axis-aligned splits.
**Proxy**: [Domain-motivated products, e.g., signal_a * signal_b]
**Feature count**: [K] features

### Log-Transforms

**Why it matters**: Exponential processes span orders of magnitude. Log-transform compresses range and linearizes growth for tree splits.
**Proxy**: `log(|signal| + epsilon)` for signals with exponential dynamics.
**Feature count**: [J] features

---

## Feature Priority Summary

| Priority | Feature Group | Count | Hypothesis | Expected Mechanism |
|----------|--------------|-------|------------|--------------------|
| 1 | [group] | [N] | Q# | [mechanism] |
| 2 | ... | ... | ... | ... |

---

## Corrections and Updates

*Document any corrections to feature candidates discovered during experiments. If a feature has the wrong formulation, note the correction here and link to the experiment that discovered it.*
