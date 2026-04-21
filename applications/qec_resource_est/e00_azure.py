"""
E00_azure: Microsoft Azure Resource Estimator baseline for RSA-2048 factoring.
Logical counts from Gidney-Ekera 2021 (arXiv:1905.09749) for 2048-bit RSA via Shor.
Run with default surface-code scheme across six qubit-technology presets.
"""

from __future__ import annotations
import datetime
import json
import time

from qsharp.estimator import LogicalCounts, EstimatorParams, QubitParams, QECScheme

# Gidney-Ekera 2021 2048-bit Shor logical counts (arXiv:1905.09749 Table 1 n=2048)
LOGICAL_COUNTS = {
    "numQubits": 6200,
    "tCount": 5_626_000_000,
    "rotationCount": 0,
    "rotationDepth": 0,
    "cczCount": 0,
    "ccixCount": 0,
    "measurementCount": 6_200_000_000,
}

QUBIT_PRESETS = [
    ("gate_ns_e3", QubitParams.GATE_NS_E3),
    ("gate_ns_e4", QubitParams.GATE_NS_E4),
    ("gate_us_e3", QubitParams.GATE_US_E3),
    ("gate_us_e4", QubitParams.GATE_US_E4),
    ("maj_ns_e4", QubitParams.MAJ_NS_E4),
    ("maj_ns_e6", QubitParams.MAJ_NS_E6),
]


def run_cell(qubit_name: str, qubit_preset, qec_scheme=QECScheme.SURFACE_CODE) -> dict:
    params = EstimatorParams()
    params.error_budget = 1e-3
    params.qubit_params.name = qubit_preset
    if qubit_name.startswith("maj_"):
        params.qec_scheme.name = QECScheme.FLOQUET_CODE
    else:
        params.qec_scheme.name = qec_scheme

    lc = LogicalCounts(LOGICAL_COUNTS)
    t0 = time.perf_counter()
    result = lc.estimate(params=params)
    elapsed = time.perf_counter() - t0

    # Parse result (it's a dict-like EstimatorResult)
    raw = dict(result) if hasattr(result, "keys") else json.loads(str(result))

    phys = raw.get("physicalCounts", {})
    logical = raw.get("logicalQubit", {})

    return {
        "qubit": qubit_name,
        "elapsed_s": elapsed,
        "physicalQubits": phys.get("physicalQubits"),
        "runtime_ns": phys.get("runtime"),
        "runtime_hours": (phys.get("runtime") or 0) / 3.6e12 if phys.get("runtime") else None,
        "logicalCycleTime_ns": logical.get("logicalCycleTime"),
        "codeDistance": logical.get("codeDistance"),
        "raw": raw,
    }


def main():
    print("[E00_azure] RSA-2048 Shor factoring, Gidney-Ekera 2021 logical counts", flush=True)
    print(f"[E00_azure] LogicalCounts: {LOGICAL_COUNTS}", flush=True)
    print()

    rows = []
    for name, preset in QUBIT_PRESETS:
        print(f"=== {name} ===", flush=True)
        try:
            r = run_cell(name, preset)
            for k, v in r.items():
                if k == "raw":
                    continue
                print(f"  {k}: {v}", flush=True)
            rows.append(r)
        except Exception as e:
            import traceback
            print(f"  FAILED: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()

    # Save the first raw result for inspection
    if rows and rows[0].get("raw"):
        path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/azure_raw_first.json"
        with open(path, "w") as f:
            json.dump(rows[0]["raw"], f, indent=2, default=str)
        print(f"\n[E00_azure] raw result of first row saved to {path}")

    # Append to results.tsv
    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    with open(tsv_path, "a") as f:
        for r in rows:
            ts = datetime.datetime.utcnow().isoformat()
            line = (
                f"E00_azure_{r['qubit']}\t{ts}\tshor_rsa_2048\t"
                f"{r.get('codeDistance') or 0}\tazure_{r['qubit']}\tNA\tNA\t42\t"
                f"{r.get('physicalQubits') or 0}\t{(r.get('runtime_hours') or 0):.3f}\t"
                f"{r.get('logicalCycleTime_ns') or 0}\t0\tNA\tKEEP\t"
                f"Phase0.5_E00_azure_RSA2048_Gidney-Ekera2021\n"
            )
            f.write(line)
    print(f"[E00_azure] wrote {len(rows)} rows to {tsv_path}")


if __name__ == "__main__":
    main()
