from simple_json_store import Store

DEFAULT_PATH = "data/settings_store.json"

CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"
INIT_STRUCTURE = {
  "version": 3,
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
