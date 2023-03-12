"""
New:
1. Change the freq and output the real freq. ✅
2. Use ns for duty to adjust the impuls as good as possible ✅
3. [Functional] Sync Package to pulse. ✅
  A: Make the package always a multiple of pulse ✅
  B: The Duty of the package must not cut the last pulse ✅
4. UX Rotary left should increment exp, and Rot right should decrement exp. ✅
"""

"""
1. Align Pulse, Package and Big Package
2. Shift Pulse
3. Align Push Pull to inverted Package and its duty (which is the Push Pull offset)
4. Align Push A and Pull B 
"""
from machine import PWM, Pin
from store import (
  store,
  PULSE_FREQ,
  PULSE_DUTY,
  # 
  PACKAGE_LEN,
  PACKAGE_COUNT,
  # PACKAGE_SHIFT,
  BIGPACK_LEN,
  BIGPACK_COUNT,
  # PUSHPULL_SHIFT,
  # PUSHPULL_MODE,
  # PUSHPULL_FREQ,
  # PUSHPULL_DUTY_A,
  # PUSHPULL_DUTY_B,
  # PUSHPULL_OFFSET_B,
  # PUSHPULL_MODE_SYNC,
  # PUSHPULL_MODE_ADJUST,
)
from ui_program import (
  UIListProgram,
  TAP_LEFT
)
from rotary import Rotary
from pwm_register import (
  set_pwm_channels,
  # set_channel_inverted,
  increase_top,
  decrease_top,
  PWM_REGISTERS,
)

PIN = 0
SLICE = 1
CHANNEL = 2
MAX = 65535
MIN = 1

class Pwm(UIListProgram):
  # Pulse & Package
  pulse = (10, 5, "A")
  package = (14, 7, "A")

  # Push & Pull
  bigpack = (9, 4, "B")
  bigpack_inv = (8, 4, "A")

  pushpull_a = (6, 3, "A")
  pushpull_b = (7, 3, "B")

  max_freq_exp = 7 # 1Mhz.
  max_duty_exp = 3 # 10000ns = 10ms
  
  title = "HACK PWM v0.0.3"

  pwm_exp = {
    "pulse_freq": 3,
    "pulse_duty": 2,
    # "pulse_shift": 1,
    # "package_freq": 3,
    # "package_duty": 2,
    # "pushpull_freq": 3,
    # "pushpull_duty_one": 2,
    # "pushpull_duty_two": 2,
    # "pushpull_duty_offset": 2,
  }
  pwms = {}

  def __init__(self, on_exit):
    self.handle_button = on_exit
    self.default_items = [
      # """
      # Pulse
      # """
      {
        "text": [["F:", self.get_exp("pulse_freq")], lambda: str(store.get(PULSE_FREQ))],
        "handle_change": lambda event: self.change_pulse_freq(event),
      },
      {
        "text": [["Duty:", self.get_exp("pulse_duty")], lambda: str(store.get(PULSE_DUTY))],
        "handle_change": lambda event: self.change_pulse_duty(event),
      },

      # """
      # Package
      # """
      {
        "text": ["Package:", lambda: str(store.get(PACKAGE_LEN))],
        "handle_change": lambda event: self.change_package_length(event),
      },
      {
        "text": ["Count:", lambda: str(store.get(PACKAGE_COUNT))],
        "handle_change": lambda event: self.change_package_count(event),
      },

      # """
      # BigPack
      # """
      {
        "text": ["BigPack:", lambda: str(store.get(BIGPACK_LEN))],
        "handle_change": lambda event: self.change_bigpack_length(event),
      },
      {
        "text": ["Count:", lambda: str(store.get(BIGPACK_COUNT))],
        "handle_change": lambda event: self.change_bigpack_count(event),
      },

      # """
      # PushPull
      # """
      # {
      #   "text": ["Push Pull Mode:", lambda: str(store.get(PUSHPULL_MODE))],
      #   "handle_change": lambda event: self.change_push_pull_mode(event),
      # },
      # {
      #   "text": ["Shift:", lambda: str(round(int(store.get(PUSHPULL_SHIFT))))],
      #   "handle_change": lambda event: self.change_push_pull_duty("offset", event),
      # },
      # {
      #   "text": ["PP:", lambda: str(round(int(store.get(PUSHPULL_FREQ))))],
      #   "handle_change": lambda event: self.change_push_pull_freq(event),
      # },
      # {
      #   "text": ["Duty:", lambda: str(round(int(store.get(PUSHPULL_DUTY_A)))) + "/ns"],
      #   "handle_change": lambda event: self.change_push_pull_duty("one", event),
      # },
      # {
      #   "text": ["B Duty:", lambda: str(round(int(store.get(PUSHPULL_DUTY_B)))) + "/ns"],
      #   "handle_change": lambda event: self.change_push_pull_duty("two", event),
      # },
    ]

    self._set_items_based_on_mode()
    self._init_pwms()

    super().__init__()

  def get_exp(self, exp_name):
    return lambda: "x" + str(self.pwm_exp[exp_name] + 1)

  def _set_items_based_on_mode(self):
    self.items = self.default_items

  def render(self):
    items_text = list(map(lambda i: i["text"], self.items))
    self.display.render_menu(self.title, items_text, self.selected_item)

  def change_pulse_freq(self, event):
    new_freq = store.get(PULSE_FREQ)
    exp = self.pwm_exp["pulse_freq"]

    if (event == Rotary.TAP):
      self.pwm_exp["pulse_freq"] = (exp - 1) % self.max_freq_exp
      return self.render()
    if (event == TAP_LEFT):
      self.pwm_exp["pulse_freq"] = (exp + 1) % self.max_freq_exp
      return self.render()
    elif (event == Rotary.INC):
      new_freq += (10 ** exp)
    elif (event == Rotary.DEC):
      new_freq -= (10 ** exp)
    else:
      return

    store.set(PULSE_FREQ, ensure_between(new_freq))

    self.restart_driver()
    self.render()

  def change_pulse_duty(self, event):
    new_duty = int(store.get(PULSE_DUTY))
    pulse_top = int(store.get(PULSE_FREQ))
    exp = self.pwm_exp["pulse_duty"]

    if (event == TAP_LEFT):
      self.pwm_exp["pulse_duty"] = (exp + 1) % self.max_duty_exp
      return self.render()
    elif (event == Rotary.TAP):
      self.pwm_exp["pulse_duty"] = (exp - 1) % self.max_duty_exp
      return self.render()
    elif (event == Rotary.INC):
      new_duty += (10 ** exp)
    elif (event == Rotary.DEC):
      new_duty -= (10 ** exp)
    else:
      return

    # change the setting, the pwm will cannot handle every adjustment..
    # but the setting will increase, and eventually the pwm too.
    store.set(PULSE_DUTY, ensure_between(new_duty, 0, pulse_top + 1))

    self.restart_driver()
    self.render()

  def change_package_length(self, event):
    top = int(store.get(PACKAGE_LEN))

    if (event == Rotary.INC):
      top = top + 1
    elif (event == Rotary.DEC):
      top = top - 1

    store.set(PACKAGE_LEN, top)
    self.restart_driver()
    self.render()

  def change_package_count(self, event):
    count = int(store.get(PACKAGE_COUNT))

    if (event == Rotary.INC):
      count = min(1000, count + 1)
    elif (event == Rotary.DEC):
      count = max(1, count - 1)

    store.set(PACKAGE_COUNT, count)
    self.restart_driver()
    self.render()

  def change_bigpack_length(self, event):
    length = int(store.get(BIGPACK_LEN))

    if (event == Rotary.INC):
      length = length + 1
    elif (event == Rotary.DEC):
      length = length - 1
    else:
      return

    store.set(BIGPACK_LEN, length)
    self.restart_driver()
    self.render()

  def change_bigpack_count(self, event):
    count = int(store.get(BIGPACK_COUNT))

    if (event == Rotary.INC):
      count += 1
    elif (event == Rotary.DEC):
      count -= 1

    store.set(BIGPACK_COUNT, count)
    self.restart_driver()
    self.render()

  """
  Main logic to hold everything together
  """
  def restart_driver(self):
    pulse_cycles     = int(store.get(PULSE_FREQ))
    pulse_count   = int(store.get(PULSE_DUTY))

    package_len     = int(store.get(PACKAGE_LEN))
    package_count   = int(store.get(PACKAGE_COUNT))

    bigpack_len     = int(store.get(BIGPACK_LEN))
    bigpack_count   = int(store.get(BIGPACK_COUNT))

    pulse = self.pulse
    package = self.package
    bigpack = self.bigpack

    package_cycles = ensure_between(pulse_cycles * package_len)
    package_compare = ensure_between(pulse_cycles * package_count)
    bigpack_cycles = ensure_between(package_cycles * bigpack_len)
    bigpack_compare = ensure_between(bigpack_count * package_cycles)

    set_pwm_channels([
      (pulse[SLICE], 0),
      (package[SLICE], 0),
      (bigpack[SLICE], 0),
    ], 0)

    """
    Package & Bigpack
    """
    bigpack_slice = bigpack[SLICE]
    PWM_REGISTERS[bigpack_slice].TOP.WRAP = bigpack_cycles - 1
    PWM_REGISTERS[bigpack_slice].COMPARE.B = bigpack_compare

    package_slice = package[SLICE]
    PWM_REGISTERS[package_slice].TOP.WRAP = package_cycles - 1
    PWM_REGISTERS[package_slice].COMPARE.A = package_compare

    pulse_slice = pulse[SLICE]
    PWM_REGISTERS[pulse_slice].TOP.WRAP = pulse_cycles - 1
    PWM_REGISTERS[pulse_slice].COMPARE.A = pulse_count

    set_pwm_channels([
      (pulse[SLICE], 0),
      (package[SLICE], 0),
      (bigpack[SLICE], 0),
    ], 1)

  def _init_pwms(self):
    self.pwms["pulse"] =  PWM(Pin(self.pulse[PIN]))
    self.pwms["package"] =  PWM(Pin(self.package[PIN]))
    self.pwms["bigpack"] =  PWM(Pin(self.bigpack[PIN]))

    self.restart_driver()

def ensure_between(value, min_v = MIN, max_v = MAX):
  return int(max(min_v, min(max_v, value)))
