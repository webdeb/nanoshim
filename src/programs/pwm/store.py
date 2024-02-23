from hackpwm.programs import PWM, PUSH_PULL, PHASE_PULSE
from lib.constants import (OUT1, OUT2, OUT3, OUT4, OUT5, OUT6,
                           PIN_GP00, PIN_GP01, PIN_GP02, PIN_GP03, PIN_GP04, PIN_GP27, PIN_GP28)

from lib.store import Store
store = Store("/store/systems.json", {
    "version": 1,
    "systems": {
        "6_pwm": {
            "title": "6xPWM",
            "programs": [
              {"label": "F1", "pid": PWM.id, "pin": OUT1},
              {"label": "F2", "pid": PWM.id, "pin": OUT2},
              {"label": "F3", "pid": PWM.id, "pin": OUT3},
              {"label": "F4", "pid": PWM.id, "pin": OUT4},
              {"label": "F5", "pid": PWM.id, "pin": OUT5},
              {"label": "F6", "pid": PWM.id, "pin": OUT6}]
        },
        "pppp": {
            "title": "4P",
            "programs": [
                {"label": "PushPull", "pid": PUSH_PULL.id, "pin": OUT1},
                {"label": "Tesla", "pid": PWM.id, "pin": OUT3, "wait_pin": OUT4},
                {"pid": PHASE_PULSE.id, "pin": OUT4, "wait_pin": OUT1, "count_pin": OUT3}]
        },
        "twofam": {
            "title": "2F AM",
            "programs": [
                {"label": "Mod", "pid": PWM.id, "pin": OUT1},
                {"label": "F1", "pid": PWM.id, "pin": OUT2, "wait_pin": OUT1},
                {"label": "F2", "pid": PWM.id, "pin": OUT3, "wait_pin": OUT4},
                {"label": "Phase Count", "pid": PHASE_PULSE.id,
                    "wait_pin": OUT1, "pin": OUT4, "count_pin": OUT3},
            ]
        }
    }
})
