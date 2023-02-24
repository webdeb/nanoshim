from simple_json_store import Store
import machine

DEFAULT_PATH = "data/steps.json"

CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"
PULSE_FREQ            = "system.pulse.freq"
PULSE_DUTY            = "system.pulse.duty"
PACKAGE_FREQ          = "system.package.freq"
PACKAGE_DUTY          = "system.package.duty"

def freq_to_steps(freq):
  return int(65535 / (freq / machine.freq() * 65535))

def ns_to_steps(ns):
  return int(ns/ (1/machine.freq()/1e-9))

def wrap_to_freq(period):
  return round(machine.freq() / (period + 1))

def cc_to_ns(period):
  return round((1/machine.freq() * period) / 1e-9)

SYSTEN_STRUCTURE = {
  "pulse": {
    "freq": freq_to_steps(5_000_000),
    "duty": ns_to_steps(200),
    "length": freq_to_steps(5_000_000),
    "pause": ns_to_steps(200),
  },
  "package": {
    "freq": freq_to_steps(20_000),
    "duty": ns_to_steps(10000),
    "length": 4,
    "pause": 12,
  },
}

print("SYSTEN_STRUCTURE", SYSTEN_STRUCTURE)

INIT_STRUCTURE = {
  "system": SYSTEN_STRUCTURE
}

store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)
