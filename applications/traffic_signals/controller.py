"""
Traffic signal controller: phase selection policy (SUMO + sumo-rl).

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES.

Contract:
    class Controller:
        name: str                 # optional log tag
        def reset(self, env):     # env is a sumo_rl.SumoEnvironment instance
            ...
        def act(self, obs) -> int:
            ...

The `obs` dict is built by evaluate.py's build_rich_obs(), containing:
    phase_one_hot:      np.ndarray (num_green_phases,)
    current_phase:      int
    num_green_phases:   int
    min_green_flag:     0/1
    time_since_last_phase_change: int (seconds)
    lane_density:       np.ndarray (n_lanes,)  [0,1]
    lane_queue:         np.ndarray (n_lanes,)  [0,1]
    lane_queue_count:   np.ndarray (n_lanes,)  raw halting count
    lane_veh_count:     np.ndarray (n_lanes,)  raw vehicle count
    lane_ids:           list[str]
    phase_lane_mask:    np.ndarray (num_green_phases, n_lanes) in {0,1}
    t:                  float (simulation seconds)

The controller should return the *index* of the desired next green phase.
sumo-rl enforces min_green + yellow_time; if `current_phase` is returned the
signal holds. Returning a different phase while min_green not satisfied is
automatically coerced to a hold.
"""

import numpy as np


class Controller:
    """SOTL — self-organising traffic light (E12 ported to SUMO).

    The winning rule from the lightweight-simulator HDR run:
        yield current green iff
            queue_served_by_current_phase == 0
            AND  max(queue_served_by_any_other_phase) >= WAITING_THRESHOLD

    Ported to SUMO:
      - "queue served" = sum of `lane_queue_count` over lanes whose
        phase-lane-mask entry is 1 for that phase
      - Raw halting vehicle counts (not normalised density) so the
        thresholds transfer directly from the toy simulator
      - Multi-phase generalisation: pick the other phase with the largest
        waiting queue as the switch target
    """

    name = "S16_preempt2x"

    CLEAR_THRESHOLD = 0
    WAITING_THRESHOLD = 1
    PREEMPT_RATIO = 2.0
    PREEMPT_FLOOR = 4

    def reset(self, env):
        pass

    def act(self, obs) -> int:
        cur = int(obs["current_phase"])
        queue = np.asarray(obs["lane_queue_count"], dtype=np.float32)
        mask = np.asarray(obs["phase_lane_mask"], dtype=np.float32)
        n_phases = int(obs["num_green_phases"])

        phase_queue = mask @ queue

        green_q = float(phase_queue[cur])
        other_qs = [(p, float(phase_queue[p])) for p in range(n_phases) if p != cur]
        if not other_qs:
            return cur
        best_other_phase, best_other_q = max(other_qs, key=lambda t: t[1])

        # Preemption: if the best other phase has much more queue than the
        # current green, switch early (before current drains). Reduces
        # starvation under heavy asymmetric demand.
        if best_other_q >= self.PREEMPT_RATIO * max(green_q, 1.0) and best_other_q >= self.PREEMPT_FLOOR:
            return best_other_phase

        if green_q <= self.CLEAR_THRESHOLD and best_other_q >= self.WAITING_THRESHOLD:
            return best_other_phase
        return cur
