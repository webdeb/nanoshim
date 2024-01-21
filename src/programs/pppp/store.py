from lib.simple_json_store import Store

DEFAULT_PATH = "/store/pppp.json"

DUTY_NS = "ns"
DUTY_CYCLES = "cycles"
DUTY_PERCENT = "%"
DUTY_MODES = [DUTY_NS, DUTY_CYCLES, DUTY_PERCENT]

SYSTEN_STRUCTURE = {
    "symmetry": {
        "high": 1000,
        "low": 1000,
        "duty_mode": DUTY_PERCENT,
        "duty_percent": 0.5,
    },
    "pushpull": {
        "high": 400,
        "low": 400,
        "high_percent": 0.5,
        "low_percent": 0.5,
    },
    "pulse": {
        "high": 380,
        "low": 380,
        "count": 10,
        "phase": 10,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
    },
    "phase": {
        "high": 15,
        "low": 20,
        "duty_mode": DUTY_CYCLES,
        "duty_percent": 0,
        "half": 0,
    }
}

INIT_STRUCTURE = {
    "version": 2,
    "system": SYSTEN_STRUCTURE,
    "saved": {}
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)


def get_param(pwm, param):
    return store.get(f"system.{pwm}.{param}")


def set_param(pwm, param, value):
    store.set(f"system.{pwm}.{param}", value)


def set_low(pwm, value):
    store.set(f"system.{pwm}.low", max(1, value))


def get_low(pwm):
    return int(store.get(f"system.{pwm}.low"))


def get_duty_percent(pwm):
    return float(store.get(f"system.{pwm}.duty_percent"))


def set_half(half):
    return store.set("system.phase.half", int(half))


def get_half():
    return int(store.get("system.phase.half"))


def set_high(pwm, value):
    store.set(f"system.{pwm}.high", max(1, value))


def get_phase(pwm):
    return int(store.get(f"system.{pwm}.phase"))


def set_phase(pwm, value):
    store.set(f"system.{pwm}.phase", value)


def get_count(pwm):
    return int(store.get(f"system.{pwm}.count"))


def set_count(pwm, value):
    store.set(f"system.{pwm}.count", value)


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
