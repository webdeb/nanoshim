from simple_json_store import Store

DEFAULT_PATH = "data/main_store.json"

CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"

PULSE_FREQ            = "system.pulse.freq"
PULSE_DUTY            = "system.pulse.duty"

PACKAGE_LEN           = "system.package.length"
PACKAGE_COUNT         = "system.package.count"
PACKAGE_SHIFT         = "system.package.shift"

BIGPACK_LEN           = "system.bigpack.length"
BIGPACK_COUNT         = "system.bigpack.count"
BIGPACK_SHIFT         = "system.bigpack.top"

PUSHPULL_MODE         = "system.pushpull.mode"
PUSHPULL_FREQ         = "system.pushpull.freq"
PUSHPULL_SHIFT        = "system.pushpull.shift"
PUSHPULL_DUTY_A       = "system.pushpull.duty_a"
PUSHPULL_DUTY_B       = "system.pushpull.duty_b"
# PUSHPULL_OFFSET_B     = "system.pushpull.offset_b"

PUSHPULL_MODE_SYNC   = "SYN"
PUSHPULL_MODE_ADJUST = "ADJ"

SYSTEN_STRUCTURE = {
  "pulse": {
    "freq": 31,
    "duty": 15
  },
  "package": {
    "length": 30,
    "count": 3,
    # "shift": 0,
  },
  "bigpack": {
    "length": 1,
    "count": 1,
    # "shift": 0
  },
  "pushpull": {
    "shift": 0,
    "mode": PUSHPULL_MODE_SYNC,
    "freq": 20000,
    "duty_a": 200, # ns
    "duty_b": 200, # ns
    # "offset_b": 0 # promille
  }
}

INIT_STRUCTURE = {
  "version": 3,
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
  "system": SYSTEN_STRUCTURE
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
