from simple_json_store import Store

DEFAULT_PATH = "data/store.json"

CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"

PULSE_FREQ            = "system.pulse.freq"
PULSE_DUTY            = "system.pulse.duty"
PACKAGE_FREQ          = "system.package.freq"
PACKAGE_DUTY          = "system.package.duty"
PACKAGE_TOP           = "system.package.top"
PACKAGE_COUNT         = "system.package.count"
PACKAGE_SHIFT         = "system.package.shift"

PUSHPULL_MODE         = "system.push_pull.mode"
PUSHPULL_FREQ         = "system.push_pull.freq"
PUSHPULL_DUTY_ONE     = "system.push_pull.duty_one"
PUSHPULL_DUTY_TWO     = "system.push_pull.duty_two"
PUSHPULL_DUTY_OFFSET  = "system.push_pull.duty_offset"

PUSHPULL_MODE_SYNC   = "SYN"
PUSHPULL_MODE_ADJUST = "ADJ"

SYSTEN_STRUCTURE = {
  "pulse": {
    "freq": 1_000_000,
    "duty": 200
  },
  "package": {
    "freq": 50_000,
    "duty": 200,
    "top": 20,
    "count": 4,
    "shift": 0,
  },
  "push_pull": {
    "mode": PUSHPULL_MODE_SYNC,
    "freq": 20000,
    "duty_one": 100, # promille

    # only relevant if mode is not sync (e.g. adjust)
    "duty_two": 100, # promille
    "duty_offset": 500 # promille
  }
}

INIT_STRUCTURE = {
  "version": 1,
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
  "system": SYSTEN_STRUCTURE
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
