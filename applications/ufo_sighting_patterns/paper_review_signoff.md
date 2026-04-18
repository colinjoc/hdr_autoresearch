# Phase 3.5 Signoff Review

## Review of Remediation for Each Major Issue

### M1. Internet adoption correlation -- RESOLVED
E30 added. Pearson r = 0.91 (p < 10^-9) for growth phase 1990-2014. Full-period divergence (r = 0.72) discussed as platform fragmentation. The claim is now empirically grounded rather than asserted. Paper Sections 5.1, 6.1, and 7 updated.

### M2. Starlink fractional vs absolute rates -- RESOLVED
E31 added. Interrupted time series confirms significant intercept shift (p < 0.001). Paper now reports both absolute (1.30x) and fractional (1.23x) rates. ITS reveals significant negative post-Starlink slope (p = 0.016), showing attenuation -- a novel finding not in the original paper. E11/DISC02 discrepancy explained. Paper Sections 4.6, 5.4, and 6.3 updated.

### M3. Poisson overdispersion -- RESOLVED
E32 added. Dispersion ratio = 719, confirming massive overdispersion. Negative binomial model (AIC = 909 vs 47,344) now presented as primary. Coefficient moves from 0.66 to 0.73; z-score from meaningless 242.5 to appropriate 5.8. Paper Section 5.3, 6.4 updated. New Section 6.4 explicitly discusses the specification error.

### M4. Classifier null result framing -- RESOLVED
Section 5.5 retitled "Explained vs. Unexplained Classification: A Null Result." Text now explicitly states: "F1 = 0.33 is a practical null result: the classifier cannot meaningfully distinguish inherently explainable from unexplainable sightings." Section 6.5 added with discussion.

### M5. Cultural archetype claim -- RESOLVED
E33 added using within-database text mentions as cultural proxy. "Saucer" mention rate correlates r = 0.91 with Disk fraction; "orb" mention rate correlates r = 0.96 with Orb fraction. Both show strong temporal trends. Section 6.2 now presents quantitative evidence. Limitation noted: within-database proxy vs external cultural data.

### M6. Geocoded dataset temporal gap -- PARTIALLY RESOLVED
E34 added: state-level formation analysis from primary dataset (no geocoding needed). Finding: no latitude effect (r = -0.04, p = 0.80). Exact-coordinate Starlink-era spatial analysis still impossible without geocoding the primary dataset. Limitation clearly stated in Section 6.6.

## Review of Minor Issues

### m1. E11 vs DISC02 inconsistency -- RESOLVED
Both absolute and fractional rates now reported with clear labeling.

### m2. Permutation test E24 -- NOT ADDRESSED
The invalid permutation test remains in results.tsv. Low priority; does not appear in the paper text.

### m3. Clock-hour rounding smartphone claim -- NOT ADDRESSED
Minor interpretive point. Paper uses "digital clocks and timestamped devices" rather than claiming smartphone specifically. Acceptable.

### m4. Infrastructure proximity without population control -- RESOLVED
Section 5.3 now explicitly states these are "descriptive only" and "cannot distinguish elevated sighting rates from elevated population density." Section 6.6 reiterates.

## New Findings from Remediation

1. **Internet divergence post-2014**: Sighting volume decouples from internet adoption after 2014 (full-period r drops to 0.72), supporting the platform-fragmentation hypothesis.
2. **Starlink attenuation**: The ITS slope change (p = 0.016) reveals that Starlink's effect on formation reports faded over time -- a novelty-habituation pattern not previously documented.
3. **NB coefficient shift**: Correcting for overdispersion shifts the population coefficient from 0.66 to 0.73, somewhat closer to linearity though still sub-linear.
4. **No latitude gradient for formations**: Post-Starlink formation rates do not correlate with state latitude, suggesting reporting demographics dominate satellite visibility.

## Test Coverage

All five new experiments (E30-E34) have passing tests in `tests/test_review_experiments.py` (8/8 pass).

## Verdict

**APPROVED.** All six major issues have been addressed (five fully resolved, one partially). The paper's claims are now supported by quantitative evidence. The two unaddressed minor issues (m2, m3) do not affect the paper's conclusions. The paper correctly frames the classifier result as a null finding, the Starlink analysis as controlled ITS, and the Poisson regression as properly specified negative binomial.
