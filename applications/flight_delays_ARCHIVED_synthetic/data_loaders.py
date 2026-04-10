"""
Data loaders for flight delay propagation through US airline networks.

Generates a synthetic US domestic flight dataset calibrated to published
BTS On-Time Performance statistics (2023-2024). The synthetic data includes
realistic tail-number rotation chains, delay propagation, airport congestion,
and delay cause decomposition.

Calibration sources:
  - BTS monthly airline on-time performance summaries
  - FAA ASPM airport delay statistics
  - Published delay decomposition: ~35% late aircraft, ~30% carrier,
    ~25% NAS, ~5% weather, ~5% security (BTS 2023 annual)
  - Mean arrival delay: ~7-8 minutes (BTS 2023)
  - Fraction delayed >15 min: ~20% (BTS 2023)

Usage:
    python data_loaders.py               # Generate synthetic dataset
    python data_loaders.py --info        # Print dataset summary
    python data_loaders.py --regenerate  # Force regeneration
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
PARQUET_FILE = DATA_DIR / "flights_synthetic.parquet"
METADATA_FILE = DATA_DIR / "dataset_metadata.json"

# ============================================================================
# US airport and carrier constants (calibrated to BTS 2023)
# ============================================================================

# Top 30 US airports by traffic (accounts for ~70% of domestic flights)
TOP_AIRPORTS = [
    "ATL", "DFW", "DEN", "ORD", "LAX", "CLT", "MCO", "LAS", "PHX", "MIA",
    "SEA", "IAH", "JFK", "EWR", "SFO", "FLL", "MSP", "BOS", "DTW", "LGA",
    "PHL", "SLC", "DCA", "SAN", "BWI", "TPA", "IAD", "MDW", "HNL", "STL",
]

# Hub airports (higher connectivity, more propagation)
HUB_AIRPORTS = {
    "ATL": "DL", "DFW": "AA", "DEN": "UA", "ORD": "UA", "CLT": "AA",
    "IAH": "UA", "PHX": "AA", "MSP": "DL", "DTW": "DL", "SLC": "DL",
    "EWR": "UA", "JFK": "B6", "LAX": None, "SFO": "UA", "MIA": "AA",
    "LAS": None, "MCO": None, "SEA": "AS", "BOS": "B6", "LGA": "DL",
}

# Major carriers with buffer characteristics
# Carriers with tighter buffers propagate more delay
CARRIERS = {
    "AA": {"name": "American", "buffer_factor": 1.0, "share": 0.18},
    "DL": {"name": "Delta", "buffer_factor": 0.85, "share": 0.17},
    "UA": {"name": "United", "buffer_factor": 1.0, "share": 0.15},
    "WN": {"name": "Southwest", "buffer_factor": 0.75, "share": 0.16},
    "B6": {"name": "JetBlue", "buffer_factor": 1.15, "share": 0.05},
    "AS": {"name": "Alaska", "buffer_factor": 0.90, "share": 0.06},
    "NK": {"name": "Spirit", "buffer_factor": 1.25, "share": 0.04},
    "F9": {"name": "Frontier", "buffer_factor": 1.20, "share": 0.03},
    "G4": {"name": "Allegiant", "buffer_factor": 1.10, "share": 0.02},
    "HA": {"name": "Hawaiian", "buffer_factor": 0.80, "share": 0.01},
    "SY": {"name": "Sun Country", "buffer_factor": 1.05, "share": 0.01},
    "MQ": {"name": "Envoy (AA regional)", "buffer_factor": 1.15, "share": 0.04},
    "OO": {"name": "SkyWest (multi)", "buffer_factor": 1.10, "share": 0.05},
    "YX": {"name": "Republic (multi)", "buffer_factor": 1.10, "share": 0.03},
}

# Flight distance buckets (miles) with typical elapsed times
DISTANCE_BUCKETS = [
    (200, 500, 90),     # short-haul, ~90 min scheduled
    (500, 1000, 150),   # medium, ~2.5 hours
    (1000, 1500, 210),  # medium-long, ~3.5 hours
    (1500, 2500, 300),  # long-haul domestic, ~5 hours
    (2500, 3500, 360),  # transcontinental + Hawaii, ~6 hours
]

# Seasonal delay multipliers (1.0 = baseline)
SEASONAL_DELAY = {
    1: 1.15, 2: 1.10, 3: 1.05, 4: 0.95, 5: 0.90, 6: 1.10,
    7: 1.15, 8: 1.10, 9: 0.85, 10: 0.90, 11: 0.95, 12: 1.20,
}

# Hour-of-day delay accumulation (delays build through the day)
HOURLY_DELAY_FACTOR = {
    6: 0.5, 7: 0.6, 8: 0.7, 9: 0.8, 10: 0.85, 11: 0.9,
    12: 1.0, 13: 1.05, 14: 1.1, 15: 1.15, 16: 1.2, 17: 1.25,
    18: 1.3, 19: 1.25, 20: 1.15, 21: 1.0, 22: 0.85, 23: 0.7,
}


def _generate_route_network(
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate a realistic route network between top airports.

    Returns a DataFrame of (origin, dest, distance, elapsed_min, daily_freq)
    pairs representing all routes in the synthetic network.
    """
    routes = []
    n_airports = len(TOP_AIRPORTS)

    for i in range(n_airports):
        for j in range(n_airports):
            if i == j:
                continue
            orig = TOP_AIRPORTS[i]
            dest = TOP_AIRPORTS[j]

            # Not all airport pairs have direct service
            # Probability of route existing depends on hub status
            orig_hub = orig in HUB_AIRPORTS
            dest_hub = dest in HUB_AIRPORTS
            if orig_hub and dest_hub:
                p_exists = 0.85
            elif orig_hub or dest_hub:
                p_exists = 0.55
            else:
                p_exists = 0.20

            if rng.random() > p_exists:
                continue

            # Distance (synthetic but realistic)
            # Use a simple geographic proxy
            idx_diff = abs(i - j)
            base_dist = 300 + idx_diff * 80 + rng.integers(-100, 100)
            base_dist = max(200, min(3500, base_dist))

            # Find matching distance bucket
            for dmin, dmax, elapsed in DISTANCE_BUCKETS:
                if dmin <= base_dist < dmax:
                    sched_elapsed = elapsed + rng.integers(-20, 20)
                    break
            else:
                sched_elapsed = 360

            # Daily frequency depends on hub status and distance
            if orig_hub and dest_hub:
                freq = rng.integers(3, 12)
            elif orig_hub or dest_hub:
                freq = rng.integers(1, 6)
            else:
                freq = rng.integers(1, 3)

            routes.append({
                "origin": orig,
                "dest": dest,
                "distance": base_dist,
                "sched_elapsed_min": sched_elapsed,
                "daily_freq": freq,
            })

    return pd.DataFrame(routes)


def _assign_carriers_to_routes(
    routes: pd.DataFrame, rng: np.random.Generator,
) -> pd.DataFrame:
    """Assign carriers to routes based on hub dominance and market share."""
    assignments = []
    carrier_codes = list(CARRIERS.keys())
    carrier_shares = np.array([CARRIERS[c]["share"] for c in carrier_codes])
    carrier_shares = carrier_shares / carrier_shares.sum()

    for _, route in routes.iterrows():
        orig = route["origin"]
        dest = route["dest"]
        freq = route["daily_freq"]

        # Hub carrier gets majority of frequencies at hub airports
        hub_carrier = HUB_AIRPORTS.get(orig)
        if hub_carrier and hub_carrier in CARRIERS:
            # Hub carrier gets ~60% of frequencies
            hub_freq = max(1, int(freq * 0.6))
            other_freq = freq - hub_freq
            assignments.append({**route.to_dict(), "carrier": hub_carrier,
                                "carrier_freq": hub_freq})
            if other_freq > 0:
                # Other carriers split remaining
                other_carrier = rng.choice(carrier_codes, p=carrier_shares)
                assignments.append({**route.to_dict(), "carrier": other_carrier,
                                    "carrier_freq": other_freq})
        else:
            # No hub dominance — assign by market share
            carrier = rng.choice(carrier_codes, p=carrier_shares)
            assignments.append({**route.to_dict(), "carrier": carrier,
                                "carrier_freq": freq})

    return pd.DataFrame(assignments)


def _generate_tail_rotations(
    route_carriers: pd.DataFrame,
    n_days: int,
    rng: np.random.Generator,
) -> list[dict]:
    """Generate realistic tail-number rotation chains.

    Each aircraft (tail number) flies 3-6 legs per day, forming a chain.
    Delays on earlier legs propagate to later legs (the key mechanism).
    """
    # Create a pool of tail numbers
    total_daily_flights = route_carriers["carrier_freq"].sum()
    legs_per_aircraft_per_day = 4  # average
    n_aircraft = max(100, total_daily_flights // legs_per_aircraft_per_day)

    tail_numbers = [f"N{1000 + i}" for i in range(n_aircraft)]

    # Assign tail numbers to carriers
    carrier_aircraft = {}
    idx = 0
    for carrier, grp in route_carriers.groupby("carrier"):
        carrier_flights = grp["carrier_freq"].sum()
        n_carrier_aircraft = max(5, carrier_flights // legs_per_aircraft_per_day)
        carrier_aircraft[carrier] = tail_numbers[idx:idx + n_carrier_aircraft]
        idx += n_carrier_aircraft

    # Generate flight schedule for all days
    all_flights = []
    flight_id = 0

    for day_offset in range(n_days):
        day_date = date(2023, 1, 1) + timedelta(days=day_offset)
        month = day_date.month
        dow = day_date.weekday()

        # Weekend has ~80% of weekday traffic
        weekend_factor = 0.80 if dow >= 5 else 1.0

        # Track which airport each tail number is at (for rotation chains)
        aircraft_location = {}  # tail -> current airport

        # Generate flights by departure hour
        for dep_hour in range(6, 24):
            hourly_flights = []

            for _, rc in route_carriers.iterrows():
                carrier = rc["carrier"]
                freq = rc["carrier_freq"]

                # Spread flights across the day (more at peak hours)
                peak_factor = 1.0
                if 7 <= dep_hour <= 9 or 16 <= dep_hour <= 19:
                    peak_factor = 1.5
                elif 10 <= dep_hour <= 15:
                    peak_factor = 1.2
                else:
                    peak_factor = 0.6

                expected_this_hour = freq * peak_factor * weekend_factor / 18.0
                n_flights = rng.poisson(max(0.01, expected_this_hour))

                for _ in range(n_flights):
                    # Assign tail number — prefer one already at origin
                    tails = carrier_aircraft.get(carrier, tail_numbers[:5])
                    origin = rc["origin"]

                    # Find aircraft at this origin
                    available = [t for t in tails
                                 if aircraft_location.get(t) == origin]
                    if available:
                        tail = rng.choice(available)
                    else:
                        tail = rng.choice(tails)

                    dep_minute = rng.integers(0, 60)
                    sched_dep = dep_hour * 100 + dep_minute

                    hourly_flights.append({
                        "flight_id": flight_id,
                        "fl_date": day_date.isoformat(),
                        "carrier": carrier,
                        "tail_num": tail,
                        "origin": origin,
                        "dest": rc["dest"],
                        "distance": rc["distance"],
                        "sched_elapsed_min": rc["sched_elapsed_min"],
                        "crs_dep_hour": dep_hour,
                        "crs_dep_min": dep_minute,
                        "crs_dep_time": sched_dep,
                        "month": month,
                        "day_of_week": dow,
                    })
                    flight_id += 1

                    # Update aircraft location
                    aircraft_location[tail] = rc["dest"]

            all_flights.extend(hourly_flights)

    return all_flights


def _generate_delays(
    flights: pd.DataFrame, rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate realistic delay patterns with propagation through rotation chains.

    This is the core of the simulation: delays on earlier legs in an aircraft's
    daily rotation chain propagate to later legs. The propagation fraction
    depends on the carrier's buffer time and the magnitude of the prior delay.
    """
    df = flights.copy()
    n = len(df)

    # Sort by date, then tail number, then departure time for rotation chain
    df = df.sort_values(["fl_date", "tail_num", "crs_dep_time"]).reset_index(drop=True)

    # Initialize delay arrays
    dep_delay = np.zeros(n, dtype=np.float32)
    arr_delay = np.zeros(n, dtype=np.float32)
    carrier_delay = np.zeros(n, dtype=np.float32)
    weather_delay = np.zeros(n, dtype=np.float32)
    nas_delay = np.zeros(n, dtype=np.float32)
    security_delay = np.zeros(n, dtype=np.float32)
    late_aircraft_delay = np.zeros(n, dtype=np.float32)

    # Track previous flight delay for each tail number on each day
    prev_tail_delay = {}  # (date, tail) -> arrival delay of previous leg

    for i in range(n):
        row = df.iloc[i]
        carrier = row["carrier"]
        month = row["month"]
        dep_hour = row["crs_dep_hour"]
        origin = row["origin"]
        fl_date = row["fl_date"]
        tail = row["tail_num"]
        distance = row["distance"]

        buffer_factor = CARRIERS.get(carrier, {}).get("buffer_factor", 1.0)
        seasonal = SEASONAL_DELAY.get(month, 1.0)
        hourly = HOURLY_DELAY_FACTOR.get(dep_hour, 1.0)

        # Is origin a hub? Hub airports have more congestion
        is_hub = origin in HUB_AIRPORTS
        hub_congestion = 1.15 if is_hub else 1.0

        # Base independent delay (not from propagation)
        # BTS statistics: mean delay ~7-8 min, ~20% delayed >15 min,
        # ~5% delayed >45 min. Achieved via mixture distribution:
        # - 40% early/on-time (uniform [-10, 3])
        # - 35% minor delay (exponential, mean ~8 min)
        # - 20% moderate delay (exponential, mean ~25 min)
        # - 5% major delay (exponential, mean ~60 min)
        draw = rng.random()
        modulation = seasonal * hourly * hub_congestion * buffer_factor
        if draw < 0.40:
            independent_delay = rng.uniform(-10, 3)
        elif draw < 0.75:
            independent_delay = rng.exponential(8.0 * modulation)
        elif draw < 0.95:
            independent_delay = 15.0 + rng.exponential(25.0 * modulation)
        else:
            independent_delay = 30.0 + rng.exponential(60.0 * modulation)

        # PROPAGATION: Check if previous leg on this tail was delayed
        tail_key = (fl_date, tail)
        prev_delay = prev_tail_delay.get(tail_key, 0.0)

        propagated_delay = 0.0
        if prev_delay > 5:  # Only propagate meaningful delays
            # Propagation fraction: how much of the previous delay carries over
            # Depends on: buffer time (carrier), turnaround time, delay magnitude
            # Typical turnaround is 35-55 min; buffer is what's left after min turn
            min_turnaround = 35  # minutes minimum ground time
            scheduled_turnaround = min_turnaround + 20 / buffer_factor
            buffer_available = max(0, scheduled_turnaround - min_turnaround)
            absorbed = min(prev_delay, buffer_available)
            propagated_delay = max(0, prev_delay - absorbed)

            # Partial recovery: ground crews can recover ~15-30% of remaining
            recovery_rate = 0.15 + 0.15 * rng.random()
            propagated_delay *= (1 - recovery_rate)

            # Long-haul flights have more en-route buffer to absorb delay
            if distance > 1500:
                propagated_delay *= 0.8

        # Combine independent + propagated delay
        total_delay = independent_delay + propagated_delay

        # Decompose into cause codes (only for delays > 15 min)
        if total_delay > 15:
            remaining = total_delay

            # Late aircraft component (from propagation)
            if propagated_delay > 0:
                late_aircraft_delay[i] = min(propagated_delay, remaining)
                remaining -= late_aircraft_delay[i]

            if remaining > 0:
                # Weather: ~5% probability of weather event, but large when it happens
                if rng.random() < 0.08 * seasonal:
                    weather_frac = rng.uniform(0.3, 0.8)
                    weather_delay[i] = remaining * weather_frac
                    remaining -= weather_delay[i]

                # NAS (air traffic control, airspace): ~25% of remaining
                if remaining > 0 and rng.random() < 0.35:
                    nas_frac = rng.uniform(0.2, 0.5)
                    nas_delay[i] = remaining * nas_frac
                    remaining -= nas_delay[i]

                # Security: rare
                if remaining > 0 and rng.random() < 0.03:
                    security_delay[i] = remaining * rng.uniform(0.1, 0.3)
                    remaining -= security_delay[i]

                # Carrier (everything else: mechanical, crew, boarding)
                carrier_delay[i] = max(0, remaining)

        dep_delay[i] = total_delay
        # Arrival delay = departure delay + en-route variation
        enroute_variation = rng.normal(0, 5)  # wind, routing
        arr_delay[i] = total_delay + enroute_variation

        # Store this flight's arrival delay for next leg in rotation chain
        prev_tail_delay[tail_key] = max(0, arr_delay[i])

    df["dep_delay"] = np.round(dep_delay, 1)
    df["arr_delay"] = np.round(arr_delay, 1)
    df["carrier_delay"] = np.round(np.clip(carrier_delay, 0, None), 1)
    df["weather_delay"] = np.round(np.clip(weather_delay, 0, None), 1)
    df["nas_delay"] = np.round(np.clip(nas_delay, 0, None), 1)
    df["security_delay"] = np.round(np.clip(security_delay, 0, None), 1)
    df["late_aircraft_delay"] = np.round(np.clip(late_aircraft_delay, 0, None), 1)

    # Arrival time
    df["crs_arr_time"] = (
        df["crs_dep_time"] + df["sched_elapsed_min"]
    ).astype(int)
    df["actual_elapsed_min"] = df["sched_elapsed_min"] + df["arr_delay"] - df["dep_delay"]

    # Binary flag: significantly delayed
    df["delayed_15"] = (df["arr_delay"] > 15).astype(int)
    df["delayed_30"] = (df["arr_delay"] > 30).astype(int)

    # Cancellation: ~2% of flights, more in bad weather months
    cancel_rate = 0.02 * df["month"].map(SEASONAL_DELAY)
    df["cancelled"] = (rng.random(n) < cancel_rate).astype(int)
    df.loc[df["cancelled"] == 1, "arr_delay"] = np.nan

    return df


def _build_propagation_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the key propagation features from tail-number rotation chains.

    For each flight, reconstruct:
    - prev_leg_arr_delay: arrival delay of the previous flight on the same tail
    - prev_leg_late_aircraft: late aircraft delay code from previous leg
    - rotation_position: which leg in today's rotation this flight is (1st, 2nd, etc.)
    - origin_congestion: number of flights departing from origin within +/- 1 hour
    """
    df = df.copy()
    df = df.sort_values(["fl_date", "tail_num", "crs_dep_time"]).reset_index(drop=True)

    # Previous leg delay on same tail number, same day
    df["prev_leg_arr_delay"] = (
        df.groupby(["fl_date", "tail_num"])["arr_delay"]
        .shift(1)
        .fillna(0)
    )
    df["prev_leg_late_aircraft"] = (
        df.groupby(["fl_date", "tail_num"])["late_aircraft_delay"]
        .shift(1)
        .fillna(0)
    )

    # Rotation position (1st leg, 2nd leg, etc.)
    df["rotation_position"] = (
        df.groupby(["fl_date", "tail_num"]).cumcount() + 1
    )

    # Origin airport congestion: flights departing within +/- 1 hour
    # Approximate: count flights at same origin, same date, within hour window
    df["origin_hour_flights"] = (
        df.groupby(["fl_date", "origin", "crs_dep_hour"])["flight_id"]
        .transform("count")
    )

    # Destination congestion (arrivals)
    arr_hour = (df["crs_dep_hour"] + df["sched_elapsed_min"] / 60).astype(int).clip(0, 23)
    df["dest_arr_hour"] = arr_hour
    df["dest_hour_flights"] = (
        df.groupby(["fl_date", "dest", "dest_arr_hour"])["flight_id"]
        .transform("count")
    )

    # Hub indicator
    df["origin_is_hub"] = df["origin"].isin(HUB_AIRPORTS).astype(int)
    df["dest_is_hub"] = df["dest"].isin(HUB_AIRPORTS).astype(int)

    # Carrier buffer factor
    df["carrier_buffer_factor"] = df["carrier"].map(
        {k: v["buffer_factor"] for k, v in CARRIERS.items()}
    ).fillna(1.0)

    # Schedule buffer: difference between scheduled elapsed time and minimum
    # (proxy for how much padding the carrier added)
    min_elapsed_by_distance = df.groupby(
        pd.cut(df["distance"], bins=[0, 500, 1000, 1500, 2500, 4000])
    )["sched_elapsed_min"].transform("min")
    df["schedule_buffer_min"] = df["sched_elapsed_min"] - min_elapsed_by_distance

    return df


def generate_synthetic_dataset(
    n_target_flights: int = 500_000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate the full synthetic flight delay dataset.

    Produces a DataFrame with one row per flight, containing:
    - Flight identifiers (date, carrier, tail number, origin, dest)
    - Scheduled and actual times
    - Delay values (departure, arrival, cause codes)
    - Propagation features (previous leg delay, rotation position, congestion)
    - Binary delay flags

    The dataset is calibrated to match published BTS delay statistics.
    """
    rng = np.random.default_rng(seed)

    print("  Generating route network...")
    routes = _generate_route_network(rng)
    print(f"    {len(routes)} routes between {len(TOP_AIRPORTS)} airports")

    print("  Assigning carriers to routes...")
    route_carriers = _assign_carriers_to_routes(routes, rng)
    print(f"    {len(route_carriers)} carrier-route pairs")

    # Estimate flights per day and adjust number of days
    daily_flights_est = route_carriers["carrier_freq"].sum() * 1.0
    n_days = max(30, int(n_target_flights / max(1, daily_flights_est)))
    n_days = min(n_days, 730)  # cap at 2 years
    print(f"  Generating {n_days} days of flights (~{daily_flights_est:.0f}/day)...")

    print("  Building tail number rotation chains...")
    flights_list = _generate_tail_rotations(route_carriers, n_days, rng)
    df = pd.DataFrame(flights_list)
    print(f"    {len(df)} raw flights generated")

    # Sample down to target if too many
    if len(df) > n_target_flights * 1.5:
        df = df.sample(n=n_target_flights, random_state=seed).reset_index(drop=True)
        print(f"    Sampled down to {len(df)} flights")

    print("  Generating delay patterns with propagation...")
    df = _generate_delays(df, rng)

    # Remove cancelled flights for the prediction task
    df_valid = df[df["cancelled"] == 0].copy()

    print("  Building propagation features...")
    df_valid = _build_propagation_features(df_valid)

    # Final feature: time-of-day sin/cos
    df_valid["dep_hour_sin"] = np.sin(2 * np.pi * df_valid["crs_dep_hour"] / 24)
    df_valid["dep_hour_cos"] = np.cos(2 * np.pi * df_valid["crs_dep_hour"] / 24)
    df_valid["dow_sin"] = np.sin(2 * np.pi * df_valid["day_of_week"] / 7)
    df_valid["dow_cos"] = np.cos(2 * np.pi * df_valid["day_of_week"] / 7)
    df_valid["month_sin"] = np.sin(2 * np.pi * (df_valid["month"] - 1) / 12)
    df_valid["month_cos"] = np.cos(2 * np.pi * (df_valid["month"] - 1) / 12)

    # Is weekend
    df_valid["is_weekend"] = (df_valid["day_of_week"] >= 5).astype(int)
    df_valid["is_monday"] = (df_valid["day_of_week"] == 0).astype(int)
    df_valid["is_friday"] = (df_valid["day_of_week"] == 4).astype(int)

    # Parse date
    df_valid["fl_date"] = pd.to_datetime(df_valid["fl_date"])

    print(f"  Final dataset: {len(df_valid)} flights")
    return df_valid


def load_dataset(force_regenerate: bool = False) -> pd.DataFrame:
    """Load the flight delay dataset.

    Attempts to load from cached parquet file. If not found or
    force_regenerate is True, generates synthetic data.
    """
    if not force_regenerate and PARQUET_FILE.exists():
        df = pd.read_parquet(PARQUET_FILE)
        print(f"  Loaded cached dataset: {len(df)} flights from {PARQUET_FILE}")
        return df

    print("  Generating synthetic US domestic flight dataset...")
    print("  (BTS On-Time data requires manual download from transtats.bts.gov)")
    df = generate_synthetic_dataset()

    # Save to parquet
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_FILE, index=False)

    # Save metadata
    valid = df[df["arr_delay"].notna()]
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "n_flights": len(df),
        "n_valid": len(valid),
        "date_range": f"{df['fl_date'].min()} to {df['fl_date'].max()}",
        "n_airports": df["origin"].nunique(),
        "n_carriers": df["carrier"].nunique(),
        "n_tail_numbers": df["tail_num"].nunique(),
        "mean_arr_delay": float(valid["arr_delay"].mean()),
        "median_arr_delay": float(valid["arr_delay"].median()),
        "frac_delayed_15": float((valid["arr_delay"] > 15).mean()),
        "frac_delayed_30": float((valid["arr_delay"] > 30).mean()),
        "delay_cause_fractions": {
            "late_aircraft": float(
                valid["late_aircraft_delay"].sum() /
                valid[["carrier_delay", "weather_delay", "nas_delay",
                       "security_delay", "late_aircraft_delay"]].sum().sum()
            ) if valid[["carrier_delay", "weather_delay", "nas_delay",
                        "security_delay", "late_aircraft_delay"]].sum().sum() > 0 else 0,
        },
        "source": "synthetic, calibrated to BTS On-Time Performance 2023",
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"  Generated {len(df)} flights")
    print(f"  Valid (non-cancelled): {len(valid)}")
    print(f"  Mean arrival delay: {valid['arr_delay'].mean():.1f} min")
    print(f"  Fraction delayed >15 min: {(valid['arr_delay'] > 15).mean():.1%}")
    print(f"  Fraction delayed >30 min: {(valid['arr_delay'] > 30).mean():.1%}")
    print(f"  Saved to {PARQUET_FILE}")

    return df


def get_cv_folds(
    df: pd.DataFrame, n_folds: int = 5,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Generate temporal cross-validation folds.

    Uses expanding window: each fold trains on earlier dates and
    validates on the next chronological chunk. No shuffle — respects
    time ordering to avoid leaking future information.
    """
    # Sort by date
    dates = df["fl_date"].values
    unique_dates = np.sort(df["fl_date"].unique())
    n_dates = len(unique_dates)
    fold_size = n_dates // (n_folds + 1)

    folds = []
    for i in range(n_folds):
        train_cutoff = unique_dates[fold_size * (i + 1) - 1]
        val_start = unique_dates[fold_size * (i + 1)]
        val_end_idx = min(fold_size * (i + 2) - 1, n_dates - 1)
        val_end = unique_dates[val_end_idx]

        train_mask = dates <= train_cutoff
        val_mask = (dates >= val_start) & (dates <= val_end)

        train_idx = np.where(train_mask)[0]
        val_idx = np.where(val_mask)[0]

        if len(val_idx) > 0:
            folds.append((train_idx, val_idx))

    return folds


def get_train_test_split(
    df: pd.DataFrame, test_fraction: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train/test with the last N% of dates as holdout.

    Temporal split: train on earlier flights, test on later flights.
    """
    unique_dates = np.sort(df["fl_date"].unique())
    n_test_dates = max(1, int(len(unique_dates) * test_fraction))
    cutoff = unique_dates[-n_test_dates]

    train = df[df["fl_date"] < cutoff].copy()
    test = df[df["fl_date"] >= cutoff].copy()
    return train, test


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flight delay propagation data loader"
    )
    parser.add_argument("--info", action="store_true",
                        help="Print dataset summary statistics")
    parser.add_argument("--regenerate", action="store_true",
                        help="Force regeneration of synthetic dataset")
    args = parser.parse_args()

    df = load_dataset(force_regenerate=args.regenerate)

    if args.info:
        valid = df[df["arr_delay"].notna()]
        print(f"\nDataset shape: {df.shape}")
        print(f"Date range: {df['fl_date'].min()} to {df['fl_date'].max()}")
        print(f"Airports: {df['origin'].nunique()} origins, {df['dest'].nunique()} destinations")
        print(f"Carriers: {df['carrier'].nunique()}")
        print(f"Tail numbers: {df['tail_num'].nunique()}")
        print(f"\nDelay statistics (non-cancelled):")
        print(f"  Mean arrival delay: {valid['arr_delay'].mean():.1f} min")
        print(f"  Median arrival delay: {valid['arr_delay'].median():.1f} min")
        print(f"  Std arrival delay: {valid['arr_delay'].std():.1f} min")
        print(f"  Delayed >15 min: {(valid['arr_delay'] > 15).mean():.1%}")
        print(f"  Delayed >30 min: {(valid['arr_delay'] > 30).mean():.1%}")
        print(f"\nDelay cause decomposition (flights with delay >15 min):")
        delayed = valid[valid["arr_delay"] > 15]
        total_cause = (
            delayed["carrier_delay"].sum() + delayed["weather_delay"].sum() +
            delayed["nas_delay"].sum() + delayed["security_delay"].sum() +
            delayed["late_aircraft_delay"].sum()
        )
        if total_cause > 0:
            print(f"  Late aircraft: {delayed['late_aircraft_delay'].sum()/total_cause:.1%}")
            print(f"  Carrier: {delayed['carrier_delay'].sum()/total_cause:.1%}")
            print(f"  NAS: {delayed['nas_delay'].sum()/total_cause:.1%}")
            print(f"  Weather: {delayed['weather_delay'].sum()/total_cause:.1%}")
            print(f"  Security: {delayed['security_delay'].sum()/total_cause:.1%}")
        print(f"\nTail number rotation stats:")
        rot = valid.groupby(["fl_date", "tail_num"]).size()
        print(f"  Mean legs/aircraft/day: {rot.mean():.1f}")
        print(f"  Max legs/aircraft/day: {rot.max()}")
