"""
Traffic signal controller: phase selection policy.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES.
"""

import numpy as np


class Controller:
    """E12: Simplified — waiting_threshold=2 always.

    Tests whether the surge-rate branch from E11 is actually doing work or
    is essentially a constant lower threshold for all tested scenarios.
    """

    name = "E12_unified_wait2"

    CLEAR_THRESHOLD = 0
    WAITING_THRESHOLD = 2

    def reset(self, sim):
        pass

    def act(self, obs) -> int:
        queues = obs["queues"]
        ns_q = queues[0] + queues[2]
        ew_q = queues[1] + queues[3]
        cur = obs["current_phase"]
        if cur == 0:
            green_q, red_q = ns_q, ew_q
        else:
            green_q, red_q = ew_q, ns_q
        if green_q <= self.CLEAR_THRESHOLD and red_q >= self.WAITING_THRESHOLD:
            return 1 - cur
        return cur
