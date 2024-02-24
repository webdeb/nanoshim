from hackpwm.programs import PWM, PUSH_PULL, PHASE_PULSE
from lib.constants import (OUT1, OUT2, OUT3, OUT4, OUT5, OUT6,
                           PIN_GP00, PIN_GP01, PIN_GP02, PIN_GP03, PIN_GP04, PIN_GP27, PIN_GP28)

from lib.store import Store
store = Store("/store/systems.json", {
    "version": 4,
    "systems": [{
        "title": "6xPWM",
        "programs": [
            {"label": "F1", "pid": PWM.pid, "pin": OUT1},
            {"label": "F2", "pid": PWM.pid, "pin": OUT2},
            {"label": "F3", "pid": PWM.pid, "pin": OUT3},
            {"label": "F4", "pid": PWM.pid, "pin": OUT4},
            {"label": "F5", "pid": PWM.pid, "pin": OUT5},
            {"label": "F6", "pid": PWM.pid, "pin": OUT6}]
    }, {
        "title": "4P",
        "programs": [
            {"label": "PushPull", "pid": PUSH_PULL.pid, "pin": OUT1},
            {"label": "Tesla", "pid": PWM.pid, "pin": OUT3, "wait_pin": OUT4},
            {"pid": PHASE_PULSE.pid, "pin": OUT4, "wait_pin": OUT1, "count_pin": OUT3}]
    }, {
        "title": "2F AM",
        "programs": [
            {"label": "Mod", "pid": PWM.pid, "pin": OUT1},
            {"label": "F1", "pid": PWM.pid, "pin": OUT2, "wait_pin": OUT1},
            {"label": "F2", "pid": PWM.pid, "pin": OUT3, "wait_pin": OUT4},
            {"pid": PHASE_PULSE.pid, "wait_pin": OUT1, "pin": OUT4, "count_pin": OUT3}]
    }, {
        "title": "4P+",
        "programs": [
            {"label": "Mod", "pid": PWM.pid, "pin": OUT6},
            {"label": "Push Pull", "pid": PUSH_PULL.pid, "pin": OUT1, "wait_pin": OUT6},
            {"label": "Tesla", "pid": PWM.pid, "pin": OUT3, "wait_pin": OUT4},
            {"label": "Pack 1", "pid": PHASE_PULSE.pid, "wait_pin": OUT1, "pin": OUT4, "count_pin": OUT3},
            {"label": "Pack 2", "pid": PHASE_PULSE.pid, "wait_pin": OUT2, "pin": OUT4, "count_pin": OUT3}]
    }]
})
