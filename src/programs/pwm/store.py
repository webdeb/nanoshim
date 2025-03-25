from hackpwm.programs import PWM, PUSH_PULL, PHASE_PULSE, INVERT, MIX, OVERLAP_MODE

from lib.store import Stores
store = Stores.get_store("/store/systems.json", {
    "version": 12,
    "systems": [
        {
            "title": "DOUBLE TAP",
            "programs": [
                {"label": "PWM", "pid": PWM.pid, "pin": "OUT1" },
                {"label": "FOLLOW", "pid": PHASE_PULSE.pid, "pin": "OUT2", "wait_pin": "OUT1", "wait_level": 0 },
            ]
        },
        {
            "title": "4P+",
            "programs": [
                {"label": "Mod", "pid": PWM.pid, "pin": "OUT6", "d": {"x": 100000, "y": 100000, "%": 0.5 }},
                {"label": "Push Pull", "pid": PUSH_PULL.pid, "pin": "OUT1", "wait_pin": "OUT6", "d": {"x": 1000, "y": 1000, "%": 0.5 }},
                {"label": "Tesla", "pid": PWM.pid, "pin": "OUT3", "wait_pin": "OUT4", "d": {"x": 100, "y": 100, "%": 0.5 }},
                {"label": "Pack 1", "pid": PHASE_PULSE.pid, "wait_pin": "OUT1", "count_pin": "OUT3", "pin": "OUT4", "d": {"x": 100, "y": 10}},
                {"label": "Pack 2", "pid": PHASE_PULSE.pid, "wait_pin": "OUT2", "count_pin": "OUT3", "pin": "OUT4", "d": {"x": 100, "y": 3}},
                {"pid": INVERT.pid, "pin": "OUT5", "wait_pin": "OUT6"}
            ]
        },

        {
            "title": "2F AM",
            "programs": [
                {"label": "Mod", "pid": PWM.pid, "pin": "OUT1"},
                {"label": "F1", "pid": PWM.pid, "pin": "OUT2", "wait_pin": "OUT1"},
                {"label": "F2", "pid": PWM.pid, "pin": "OUT3", "wait_pin": "OUT4"},
                {"pid": PHASE_PULSE.pid, "pin": "OUT4", "wait_pin": "OUT1", "count_pin": "OUT3"}
            ]
        },
        {
            "title": "PWM",
            "programs": [
                {"label": "F1", "pid": PWM.pid, "pin": "OUT1"}
            ]
        },
        {
            "title": "SIXMIX INV OVERLAP",
            "programs": [
                {"pid": MIX.pid, "inverted": True, "pin": "OUT1", "pins": 6, "mode": OVERLAP_MODE}
            ]
        },
        {
            "title": "3 MIX",
            "programs": [
                { "pid": MIX.pid, "pin": "OUT1", "pins": 3}
            ]
        },
        {
            "title": "2 MIX OVERLAP",
            "programs": [
                { "pid": MIX.pid, "pin": "OUT1", "pins": 2, "mode": OVERLAP_MODE }
            ]
        },
        {
            "title": "2 MIX+",
            "programs": [
                { "pid": MIX.pid, "pin": "OUT1", "pins": 2, "mode": OVERLAP_MODE },
                { "pid": PHASE_PULSE.pid, "pin": "OUT4", "wait_pin": "OUT1" },
                { "pid": PHASE_PULSE.pid, "pin": "OUT5", "wait_pin": "OUT2" },
                { "pid": PHASE_PULSE.pid, "pin": "OUT6", "wait_pin": "OUT3" }
            ]
        },
        {
            "title": "2 MIX INV OVERLAP",
            "programs": [
                { "pid": MIX.pid, "inverted": True, "pin": "OUT1", "pins": 2, "mode": OVERLAP_MODE }
            ]
        }
    ]
})
