from lib.simple_json_store import Store

DEFAULT_PATH = "data/twofam.json"

DUTY_NS = "ns"
DUTY_CYCLES = "cycles"
DUTY_PERCENT = "%"
DUTY_MODES = [DUTY_NS, DUTY_CYCLES, DUTY_PERCENT]

SYSTEN_STRUCTURE = {
    "f1": {
        "high": 15,
        "low": 50,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
    },
    "f2": {
        "high": 15,
        "low": 20,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
    },
    "package": {
        "high": 15,
        "low": 20,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
    },
    "f2_phase": {
        "high": 15,
        "low": 20,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
    }
}

INIT_STRUCTURE = {
    "version": 10,
    "system": SYSTEN_STRUCTURE,
    "saved": {}
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)


def set_low(pwm, value):
    store.set(f"system.{pwm}.low", max(1, value))


def get_low(pwm):
    return int(store.get(f"system.{pwm}.low"))


def get_duty_percent(pwm):
    return store.get(f"system.{pwm}.duty_percent")


def set_high(pwm, value):
    store.set(f"system.{pwm}.high", max(1, value))


def reset_percent(pwm):
    high, low = get_params(pwm)
    store.set(f"system.{pwm}.duty_percent", high/(high+low))


def get_high(pwm):
    return int(store.get(f"system.{pwm}.high"))


def set_duty_mode(pwm, mode):
    store.set(f"system.{pwm}.duty_mode", mode)


def get_duty_mode(pwm):
    return store.get(f"system.{pwm}.duty_mode")


def set_params(pwm, params):
    high, low = params
    set_high(pwm, high)
    set_low(pwm, low)


def get_params(pwm):
    return get_high(pwm), get_low(pwm)


def get_period(pwm):
    return sum(get_params(pwm))


"""
TODO: Save Systems
"""


def save_system(name):
    system = store.get("system")
    saved = store.get("saved") or {}
    saved[name] = system
    store.set("saved", saved)


def get_saved_names():
    systems = list(store.get("saved") or {})
    return systems


def load_saved(name):
    system = store.get(f"saved.{name}")
    store.set("system", system)
