from simple_json_store import Store

DEFAULT_PATH = "data/storecopy.json"

CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"

DUTY_NS = "ns"
DUTY_CYCLES = "cycles"
DUTY_PERCENT = "%"

FREQ_CYCLES = "cycles"
FREQ_COUNT_HIGHER = "count"

SYSTEN_STRUCTURE = {
  "pulse": {
    "period": 31,
    "duty": 15,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  },
  "package": {
    "period": 300,
    "duty": 3,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  },
  "bigpack": {
    "period": 1,
    "duty": 1,
    "duty_mode": DUTY_CYCLES,
    "period_mode": FREQ_CYCLES,
  }
}

INIT_STRUCTURE = {
  "version": 6,
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
  "system": SYSTEN_STRUCTURE
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)

def set_period(pwm, value):
  store.set(f"system.{pwm}.period", value)
def get_period(pwm):
  return int(store.get(f"system.{pwm}.period"))

def set_duty(pwm, value):
  store.set(f"system.{pwm}.duty", value)
def get_duty(pwm):
  return int(store.get(f"system.{pwm}.duty"))

def set_duty_mode(pwm, mode):
  store.set(f"system.{pwm}.duty_mode", mode)
def get_duty_mode(pwm):
  return store.get(f"system.{pwm}.duty_mode")
