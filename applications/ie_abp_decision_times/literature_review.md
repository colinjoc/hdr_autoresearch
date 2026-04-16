# Literature Review — An Bord Pleanála decision times

Scope: Irish planning-appellate decision-time trends 2015-2025. Prepared in advance of the E00 baseline audit and the Phase 1 tournament. Themes follow the compact four-theme version of the Phase 0 rubric appropriate for a descriptive-analytical project.

## Theme 1 — Irish planning law and the statutory objective period (SOP)

An Bord Pleanála (ABP, "the Board") is the Irish national planning-appellate body, established by the Local Government (Planning and Development) Act 1976 and now reconstituted as An Coimisiún Pleanála (ACP, "the Commission") by Part 17 of the Planning and Development Act 2024 which commenced 18 June 2025. The Board's primary statutory function is to decide appeals against local-authority planning decisions, Strategic Infrastructure Development (SID) applications, Large-scale Residential Development (LRD) applications, Local Authority Own-Development (LAOD) cases, and referrals under section 5 of the Planning and Development Act 2000.

Section 126 of the Planning and Development Act 2000 sets a **statutory objective period** (SOP) of 18 weeks for the disposal of most appeals and referrals; 4 months for certain environmental cases; and project-specific SOPs for fast-track categories — 16 weeks for Strategic Housing Development (SHD, 2017–2021) and for LRD (2021–present), 18 weeks (with extensions) for SID, and case-specific timelines for derelict-site levy, vacant-site levy and Residential Zoned Land Tax (RZLT) appeals. Critically, the SOP is an **objective**, not a mandatory deadline: failure to meet it does not vitiate the decision (see P011 Simons 2019 §17.12; P034 McKillen v ABP). This means the binding constraint on ABP's timing is reputational and political, not judicially enforceable.

The SOP regime was introduced as an efficiency target in 1992 (under the 1992 Amendment Act) and has since been the standard by which ABP's own annual reports measure throughput. Compliance historically hovered around 70–80% (see Annual Report 2018 Fig. 3: 81% in 2011, 80% in 2013, 79% in 2014, 64% in 2017, 43% in 2018). The 2017 transition to a new case-management IT system (Plean-IT) is identified by the Board itself (P015) as the proximate trigger for the initial compliance collapse.

Between 2017 and 2021 the planning caseload was transformed by the introduction of Strategic Housing Development (SHD) under the Planning and Development (Housing) and Residential Tenancies Act 2016 (P030), which diverted 100+-unit residential applications from the normal two-stage appellate process into a direct SHD application to ABP. SHD was repealed in February 2022 and replaced by Large-scale Residential Development (LRD) which reverted to the two-stage local-authority-first model but retained a 16-week ABP appellate SOP (P029). Both regimes produced extraordinary JR filing rates (P032 OPR SHD Inside Report: roughly 40% of major SHD decisions faced JR). The Planning and Development Act 2024 (P028) further codifies statutory timelines: for example, 48 weeks for SIDs, 26 weeks for LAPs, and 48 weeks for Section 37B private applications.

The 2019 Supreme Court decisions in Connelly v ABP [2018] IESC 31 (P040) and Balz v ABP [2019] IESC 91 (P039) expanded the duty-to-give-reasons obligation on ABP, requiring longer inspector reports and more detailed Board decisions — a direct mechanical contributor to decision time. The July 2022 Heather Hill Management Company v ABP [2022] IESC 43 (P034) ruling narrowed locus standi somewhat but did not materially reduce JR filing rates.

## Theme 2 — Administrative delay, queueing theory and Parkinson's Law

Decision-time analysis in administrative agencies is a mature literature. Kleinrock's classical queueing theory (P001) and Little's Law (P002) apply naturally: if the intake rate is λ cases/week, the service rate is μ cases/week, and the number of on-hands cases is L, then at steady-state L = λ × W where W is the average weeks-to-dispose. When ρ = λ/μ → 1 (utilization approaches 1), Kingman's heavy-traffic formula (P065) shows W diverges hyperbolically: W ≈ (ρ/(1-ρ)) × (1/μ). Administrative agencies that operate close to capacity are therefore **inherently unstable** in the sense that small intake or productivity shocks produce disproportionately large delays. This is the headline mechanism we expect to find in ABP's 2018–2024 data.

Parkinson's Law (P003) — "work expands to fill the time available" — is the popular formulation of a more subtle result: administrative outputs tend toward a characteristic cycle time that depends on organisational culture, not on case complexity. Wilson (P072), Niskanen (P202) and Tullock (P203) generalise this in the budget-maximiser model: bureaucrats optimize for budget and reputation, not throughput, so voluntary speed-up is rare.

Adler and Gulland (P124) document user-experience consequences of delay in UK social-security tribunals; Halliday (P093) and Richardson & Machin (P094) investigate the feedback loop between judicial review and tribunal caseload — a JR-lodgement increases the decision-making burden on the agency both directly (defending the JR) and indirectly (prompting more cautious, slower decisions on similar cases). This feedback mechanism is exactly the dynamic conjectured for ABP in research question (e). Allen (P044) and Thomas (P045) provide UK case studies in asylum and planning-inspectorate decision times with methodological parallels for ABP.

Queueing-model applications to courts and regulators are less common but well-established: Zhang (P063), Klein & Rosenfeld (P064), and Whitt (P066) adapt M/G/1 and GI/G/m models to tribunal caseload. The key conclusion is that a small number of long-tail cases can drive the mean weeks-to-dispose up substantially (M/G/1 variance term). For ABP, the long-tail cases are likely SHD/LRD/SID cases where JR risks trigger additional Board drafting and multi-member panel sign-off.

## Theme 3 — Capacity, staff and board-member composition at ABP

The single most-cited cause of the 2022–2024 ABP decision-time crisis in press and primary sources is capacity: specifically, the vacancy of Board-member seats in 2022 following the Farrell Report (P057) and subsequent Oireachtas Committee scrutiny (P056). By end-2022, only 5 of the 15 permanent Board-member seats were filled (see Q1 2025 resourcing overview, reproduced in `data/raw/q1_2025.txt` lines 416–488). The Indecon Organisational Capacity Review (P052) in October 2022 recommended 60+ additional FTE — acknowledged by DHLGH in the same month and phased in over 2023-2024.

By end-2024 the Board complement had been restored to 17 (temporarily over the 15-seat permanent establishment) and total FTE had grown from 202 (end-2022) to 290 (end-2024) — a 43% increase. Over the same period the total intake fell from 3,058 (2022) to 2,727 (2024) — a 10.8% decrease. The on-hands caseload fell from a peak of 3,616 cases in May 2023 to 1,576 at end-2024. The combined effect of +43% FTE and -10.8% intake should, under any queueing model, produce substantial compliance recovery. The actual data show this recovery is only partial — 25% SOP compliance in 2024 vs 28% in 2023 — and we need to test whether the gap is because the remaining backlog is dominated by long-tail cases (SHD/LRD/SID that take 44–124 weeks on average).

Board members are appointed by the Minister, typically for 5-year terms. The 2022-2024 crisis was precipitated by the Farrell Report's finding of potential conflicts of interest on the part of then-Deputy-Chair Paul Hyde, who resigned in July 2022, and subsequent scrutiny of other members' declarations. This triggered a wave of recusals, adding delay to many specific cases (P103 Dowling; P180 Bray timeline). Chairperson Dave Walsh commenced September 2022 and an interim crisis-management regime operated through 2023.

## Theme 4 — Comparable international planning agencies and judicial-review feedback

**UK Planning Inspectorate (PINS)** publishes decision times in its Annual Report (P047, P048). PINS's equivalent of the SOP is a statutory 22-week target for called-in applications and 12-week target for written-representations appeals. PINS 2023-24 reported ~26 weeks median for major appeals — consistent with an international baseline of 20–30 weeks for planning-appellate decisions in mature jurisdictions.

**Netherlands Raad van State** Administrative Jurisdiction Division (P049) is the closest Continental-European comparator: its average disposal time for planning appeals was ~40 weeks in 2023, but with a very different case-mix (no SHD-equivalent fast track).

**New Zealand Environment Court** (P050) and **Ontario Land Tribunal** (P051) operate on 10–18 month median cycles, with similar judicial-review pressure mechanisms. OLT's 2022-23 disposal statistics suggest ~28 weeks median.

Judicial-review feedback onto agency decision-time is theoretically clear (P093 Halliday; P094 Richardson & Machin) but empirically under-tested. Our research question (e) is close to novel in an Irish context. In our companion project (PL-2 at `/applications/ie_lrd_vs_shd_jr/`) we found a JR filing rate of 36% for LRD and 33% for SHD — orders of magnitude higher than the normal-planning-appeal JR rate (~0.3%). If JR lodgement causes the Board to spend longer on similar cases, we should see an association between JR-lodgement-rate-last-year and disposal-time-this-year in fixed-effects regressions controlling for case type.

The Courts Service Planning and Environment List (P041), established in November 2022, is the main intervention in the JR disposal cycle. It cut median JR disposal from ~70 weeks (2020-2022) to ~30 weeks (2023-2024, P042-P043). Its effect on ABP decision times is ambiguous — faster JR disposal should reduce the "remittal" delay channel but does not change the underlying reason-giving burden Balz/Connelly imposed.

## Summary of the most stylised facts from the lit review

1. ABP mean weeks-to-dispose rose from 18 (2017) to 23.3 (2018) to a trough of 20 (2021) before climbing to 26 (2022), 42 (2023) and 42 (2024).
2. SOP compliance fell from ~64% (2017) to 43% (2018), recovered to 73% (2020), fell to 57% (2021), 45% (2022), 28% (2023) and 25% (2024).
3. The 2020 "improvement" appears driven partly by the absence of SHD cases in disposal during COVID-affected processing slowdown.
4. SHD cases had the slowest mean decision times every year since 2018 (124 weeks in 2024 — a textbook long-tail).
5. Board-member vacancies in 2022 and the Farrell report (P057) produced the proximate organisational shock.
6. The P&E List (Nov 2022) reduced JR disposal time but did not visibly change ABP decision time.
7. Kingman's heavy-traffic formula (P065) predicts that if utilization ρ = λ/μ was close to 1 around 2022, a +20% intake shock produces much more than a +20% delay — which is what we see.
