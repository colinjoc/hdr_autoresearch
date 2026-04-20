# Knowledge Base: Asset Correlation Regimes

Stylised facts from the literature, each tagged with the paper IDs (see `papers.csv`) that establish it. These are the empirical checkpoints that any correlation model we fit should be able to reproduce or refute on our own 2004–2026 panel.

## Cross-asset correlation behaviour in general

1. **Cross-country equity correlations rise in joint lower tails but not upper tails** — an asymmetry between bear-market correlations and bull-market correlations of roughly 0.3 vs 0.1 depending on country pair and sample [P002, P008].

2. **Naive Pearson correlations are upward-biased in high-volatility windows** even when the true data-generating correlation is unchanged; the bias is exactly the Forbes–Rigobon heteroskedasticity effect, and the correction is to scale by the ratio of high-vol to low-vol variance [P001].

3. **DCC-GARCH conditional correlation persistence is high** — typical empirical values of α ≈ 0.02 and β ≈ 0.95 (so α + β ≈ 0.97) mean that the daily conditional correlation decays toward its unconditional mean very slowly, with a half-life on the order of 20–40 days [P003].

4. **Correlation regimes identified by Markov-switching tend to show bear regimes with both higher vol and higher cross-asset correlation** — the "diversification fails when you need it" stylised fact [P008].

## Gold–equity correlation

5. **Gold's unconditional correlation with US equities over ~30 years is slightly negative to near zero**, typically in the range [−0.1, +0.05] depending on sample and frequency [P004, P005].

6. **Gold is a short-horizon safe haven (~15 trading days) but not a long-horizon one** — the safe-haven role reverses at long horizons during recessions, so buy-and-hold gold is not downside-protective over multi-year stretches [P004, P007].

7. **Gold's safe-haven role is strong for developed European and US equities but absent for BRICs, Japan, Australia, Canada** — the finding is not universal across international equities [P005].

8. **Gold's inflation-hedging coefficient is regime-dependent** — gold hedges US inflation during average and bearish gold regimes but not during bullish ones; similar regime dependence in UK/JP/EU [P030, P031].

9. **Gold's safe-haven role weakened during COVID-19** in high-frequency DCC-GARCH analysis — not every crisis generates the classic gold-as-safe-haven pattern [P016].

10. **Gold hedges USD depreciation on average and is a safe haven against extreme dollar moves** — the gold-DXY relationship is reliably negative and symmetric in the tails [P006].

## Bitcoin–equity correlation

11. **BTC's rolling 90-day correlation with the S&P 500 rose from near zero (pre-2020) to ~0.3–0.5 (post-2020) and reached sustained positive levels after January 2024** (spot BTC ETF approval). The Nasdaq correlation is even higher [P044, P045].

12. **BTC failed as a safe haven during the March 2020 COVID crash** — BTC fell with the S&P 500 and any portfolio allocation to BTC INCREASED downside risk. The "digital gold" claim did not survive its first real stress test [P015].

13. **BTC's 90-day rolling correlation with gold has averaged ~0.1 since 2015** — weak on average, with episodes of alignment (e.g., late 2024) and of divergence (e.g., 2025 gold rally while BTC corrected) [P044, P045].

14. **BTC is not an effective inflation hedge** in post-2020 data despite the narrative; returns are dominated by risk-on/off flows, not inflation surprises [P037, P038].

## Commodities–equity correlation

15. **Pre-financialisation (1959–2004) commodity-equity correlation was negative**, roughly in the range [−0.2, 0.0] [P019].

16. **Post-2004 and especially post-Lehman (Sep 2008), commodity-equity correlation jumped from near zero to ~+0.5 and has stayed elevated** — a regime break attributed to index investment and financialisation [P022, P023].

17. **Index-member commodities have higher correlations with equities than non-index-member commodities** — confirming the financialisation channel operates via the fund-flow mechanism, not via fundamentals [P022].

18. **Oil-equity relationship is predictive, not just contemporaneous** — oil price changes Granger-cause global equity returns in 12 of 18 developed-country indices [P021].

## Macro-regime conditioning

19. **The sign of the inflation–output-gap correlation drives bond-stock correlation** — it flipped from positive (pre-2001) to negative (2001–2020) to positive again (2022–2023), which mechanically flips the bond-stock covariance [P026, P027].

20. **Tighter Fed policy reduces stocks and raises the yield curve** under heteroskedasticity-based identification; a typical 25 bp surprise hike moves the S&P 500 down ~1% [P024].

21. **Global capital-flow waves are driven primarily by global risk factors** — the common component (sometimes called the global financial cycle) drives synchronised cross-asset correlation shifts [P025].

22. **The historical inverse commodity-USD correlation broke down in 2021–2023** — both moved up together and then down together, a regime shift attributed to shifts in US terms-of-trade and global supply shocks [P041, P042].

23. **Intermediary leverage is procyclical** — rising asset prices → higher leverage; falling prices → forced deleveraging → cross-asset sell-offs → synchronous drawdowns [P032].

24. **Geopolitical risk (GPR) shocks raise inflation and depress output** in importing countries — a stagflationary shock that plausibly pushes gold and equities (as real claims) upward together for different mechanistic reasons [P029, P040].

25. **The post-ETF BTC regime (Jan 2024 onward) shifted BTC's mean correlation with SPY up by roughly 0.2–0.3 units** based on rolling windows in industry reports — a structural break of the kind a Markov-switching or Chow-test style test should detect [P044, P045].

## Methodological facts

26. **Rolling 90-day Pearson correlation is the industry-standard eyeball metric** but is high-variance; a 250-day window is more stable but lags regime changes. The typical robustness check is to report 30/90/250-day together [P007].

27. **Pre-break data can still improve out-of-sample forecasts in the presence of structural breaks** — the Pesaran-Timmermann window-selection result. Implication: we should NOT throw out pre-2020 data, even if we believe the post-COVID regime is different [P010].
