# revnet_landauer_imagenet — PAUSED (external hardware blocker)

**Date:** 2026-04-20
**Follow-on priority in the thermodynamics portfolio:** #7 of 8.

## What this project would do

Train both an i-RevNet (invertible residual network) and a matched conventional ResNet on ImageNet, with DCGM per-kernel power instrumentation. The theoretical prediction from `thermodynamic_ml_limits/paper.md` §5.3 is that RevNets, by virtue of logical reversibility of their linear operations, should dissipate roughly 10× less energy per bit of PAC-Bayes information (Lotfi et al. 2022) than conventional ResNets at matched accuracy.

This would be the first falsifiable measurement of the reversibility-driven energy-efficiency headroom in real ML training — a direct test of the "reversible computing" proposition.

## Why paused

Requires multi-GPU ImageNet training (typically 8× A100 for ~24 hours, or larger for i-RevNet's memory-optimised but compute-heavy training). DCGM power instrumentation requires administrative access to the GPU cluster. Neither is available in the current research environment.

Per program.md external-blocker rule: the project is paused, not killed.

## Resumption checklist

1. Confirm GPU cluster access (8× A100 or equivalent, with DCGM).
2. Reproduce the published i-RevNet ImageNet benchmark first (Jacobsen et al. 2018) to validate the training pipeline.
3. Use Lotfi et al. 2022 code to compute PAC-Bayes bits at matched accuracy.
4. Run the project's Phase −0.5 scope check (proposal will be drafted at resumption).
5. Continue through the full HDR sweep.

## Lower-resource fallback

A small-scale version on CIFAR-10 with a toy RealNVP (Dinh et al. 2016) vs ResNet-18 could be done on a single consumer GPU in ~4 hours. This would not be a full ImageNet result but could act as a pilot that either motivates or de-prioritises the full-scale experiment. Noted as a possible reframe path at resumption.

## Related open projects

- `h100_housekeeping_phi_hw_blocked` (priority #2) — also hardware-blocked; the two could be resumed together.
