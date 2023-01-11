import os
import json
import micropython
from simple_json_store import Store 

DEFAULT_PATH = "data/store.json"
SYSTEN_STRUCTURE = {
  "sync_push_pull": True,
  "pulse": {
    "freq": 1_000_000,
    "duty": 0.5 * 65535
  },
  "package": {
    "freq": 50_000,
    "duty": 0.2 * 65535
  },
  "push_pull":{
    "freq": 50_000,
    "duty": 0.2 * 65535
  }
}

INIT_STRUCTURE = {
  "ver": "0.0.1",
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
  "system": SYSTEN_STRUCTURE
}

CONTRAST_PATH = "settings.contrast"
MACHINE_FREQ_PATH = "settings.machine_freq"

PULSE_FREQ = "system.pulse.freq"
PULSE_DUTY = "system.pulse.duty"
PACKAGE_FREQ = "system.package.freq"
PACKAGE_DUTY = "system.package.duty"
PUSHPULL_FREQ = "system.push_pull.freq"
PUSHPULL_DUTY = "system.push_pull.duty"

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
