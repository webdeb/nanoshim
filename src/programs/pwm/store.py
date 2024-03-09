from hackpwm.programs import PWM, PUSH_PULL, PHASE_PULSE, INVERT
from lib.constants import (OUT1, OUT2, OUT3, OUT4, OUT5, OUT6,
                           PIN_GP00, PIN_GP01, PIN_GP02, PIN_GP03, PIN_GP04, PIN_GP27, PIN_GP28)

from lib.store import Store
store = Store("/store/systems.json", {
    "version": 7,
    "systems": [
        {
            "title": "4P+",
            "programs": [
                {"label": "Mod", "pid": PWM.pid, "pin": "OUT6", "d": {"x": 100000, "y": 100000, "%": 0.5 }},
                {"label": "Push Pull", "pid": PUSH_PULL.pid, "pin": "OUT1", "wait_pin": OUT6, "d": {"x": 1000, "y": 1000, "%": 0.5 }},
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
        }

    ]
})
