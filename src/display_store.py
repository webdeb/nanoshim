from simple_json_store import Store
DEFAULT_PATH = "store/display.json"
CONTRAST_PATH = "contrast"
INIT_STRUCTURE = {
  "version": 1,
  "contrast": 200,
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
