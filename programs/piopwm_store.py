from simple_json_store import Store

DEFAULT_PATH = "data/piopwm_store.json"

DUTY_NS = "ns"
DUTY_CYCLES = "cycles"
DUTY_PERCENT = "%"
DUTY_MODES = [DUTY_NS, DUTY_CYCLES, DUTY_PERCENT]

FREQ_CYCLES = "cycles"
FREQ_COUNT_HIGHER = "count"

SYSTEN_STRUCTURE = {
  "f1": {
    "period": 31,
    "duty": 15,
    "duty_percent": 50,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  },
  "f2": {
    "period": 31,
    "duty": 15,
    "low": 20,
    "duty_percent": 50,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  },
  "package": {
    "period": 300,
    "duty": 3,
    "duty_percent": 50,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  },
  "bigpack": {
    "period": 1,
    "duty": 1,
    "duty_percent": 50,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  }
}

INIT_STRUCTURE = {
  "version": 9,
  "system": SYSTEN_STRUCTURE,
  "saved": {}
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)

def set_low(pwm, value):
  store.set(f"system.{pwm}.low", value)
def get_low(pwm):
  return store.get(f"system.{pwm}.low")

def set_high(pwm, value):
  store.set(f"system.{pwm}.high", value)
def get_high(pwm):
  return store.get(f"system.{pwm}.high")

def set_period(pwm, value):
  store.set(f"system.{pwm}.period", value)
def get_period(pwm):
  return int(store.get(f"system.{pwm}.period"))

def set_duty(pwm, value):
  store.set(f"system.{pwm}.duty", value)
def get_duty(pwm):
  return int(store.get(f"system.{pwm}.duty"))

def set_duty_percent(pwm, value):
  store.set(f"system.{pwm}.duty_percent", value)
def get_duty_percent(pwm):
  return int(store.get(f"system.{pwm}.duty_percent"))

def set_duty_mode(pwm, mode):
  store.set(f"system.{pwm}.duty_mode", mode)
def get_duty_mode(pwm):
  return store.get(f"system.{pwm}.duty_mode")

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
