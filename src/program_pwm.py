import machine
from machine import PWM, Pin
from store import (
  store,
  PULSE_FREQ,
  PULSE_DUTY,
  PACKAGE_FREQ,
  PACKAGE_DUTY,
  PUSHPULL_MODE,
  PUSHPULL_FREQ,
  PUSHPULL_DUTY_ONE,
  PUSHPULL_DUTY_TWO,
  PUSHPULL_DUTY_OFFSET,
  PUSHPULL_MODE_SYNC,
  PUSHPULL_MODE_ADJUST,
)
from ui_program import UIListProgram
from rotary import Rotary
from pwm_register import (
  set_pwm_channels,
  set_channel_inverted
)

class Pwm(UIListProgram):
  # Pulse & Package
  pin_pulse = 10
  pin_package = 14

  # Push & Pull
  pin_push_pull_one = 9
  pin_push_pull_two = 7
  pin_push_pull_offset = 6

  max_freq_exp = 7 # 1Mhz.
  max_duty_exp = 3 # 10000ns = 10ms
  
  title = "HACK PWM v0.0.1"
  pwm_exp = {
    "pulse_freq": 3,
    "pulse_duty": 2,
    "package_freq": 3,
    "package_duty": 2,
    "pushpull_freq": 3,
    "pushpull_duty_one": 2,
    "pushpull_duty_two": 2,
    "pushpull_duty_offset": 2,
  }
  pwms = {}

  def __init__(self, on_exit):
    self.handle_button = on_exit
    self.default_items = [
      # Pulse Package
      {
        "text": ["PulsF:", lambda: str(round(store.get(PULSE_FREQ)))],
        "handle_change": lambda event: self.change_freq("pulse", event),
        "exp": "pulse_freq", 
      },
      {
        "text": ["PulsD:", lambda: str(round(store.get(PULSE_DUTY)))+ "/pm"],
        "handle_change": lambda event: self.change_duty("pulse", event),
        "exp": "pulse_duty", 
      },
      {
        "text": ["PackF:", lambda: str(round(store.get(PACKAGE_FREQ)))],
        "handle_change": lambda event: self.change_freq("package", event),
        "exp": "package_freq",
      },
      {
        "text": ["PackD:", lambda: str(round(store.get(PACKAGE_DUTY)))+ "/oo"],
        "handle_change": lambda event: self.change_duty("package", event),
        "exp": "package_duty",
      },
      # Push - Pull
      # 
      {
        "text": ["PP Mode:", lambda: str(store.get(PUSHPULL_MODE))],
        "handle_change": lambda event: self.change_push_pull_mode(event),
      },
      {
        "text": ["Freq:", lambda: str(round(store.get(PUSHPULL_FREQ)))],
        "handle_change": lambda event: self.change_push_pull_freq(event),
        "exp": "pushpull_freq",
      },
      {
        "text": ["Duty 1:", lambda: str(round(store.get(PUSHPULL_DUTY_ONE)))+ "/oo"],
        "handle_change": lambda event: self.change_push_pull_duty("one", event),
        "exp": "pushpull_duty_one",
      },
      {
        "text": ["Duty 2:", lambda: str(round(store.get(PUSHPULL_DUTY_TWO)))+ "/oo"],
        "handle_change": lambda event: self.change_push_pull_duty("two", event),
        "exp": "pushpull_duty_two",
      },
      {
        "text": ["Offset:", lambda: str(round(store.get(PUSHPULL_DUTY_OFFSET)))+ "/oo"],
        "handle_change": lambda event: self.change_push_pull_duty("offset", event),
        "exp": "pushpull_duty_offset",
      },
    ]

    self._set_items_based_on_mode()
    self._create_push_pull_pwm_group()
    self._create_pulse_package_pwm_group()

    super().__init__()

  def _set_items_based_on_mode(self):
    if (store.get(PUSHPULL_MODE) == PUSHPULL_MODE_SYNC):
      self.items = self.default_items[0:-2]
    else:
      self.items = self.default_items
    
    super().__init__()

  def render(self):
    items_text = list(map(lambda i: i["text"], self.items))
    exp = None

    if ("exp" in self.default_items[self.selected_item]):
      exp = self.pwm_exp[self.default_items[self.selected_item]["exp"]]

    self.display.render_menu(self.title, items_text, self.selected_item, exp)

  def change_push_pull_mode(self, event):
    if (store.get(PUSHPULL_MODE) == PUSHPULL_MODE_SYNC):
      store.set(PUSHPULL_MODE, PUSHPULL_MODE_ADJUST)
    else:
      store.set(PUSHPULL_MODE, PUSHPULL_MODE_SYNC)

    self.set_push_pull_duty_by_mode()
    self._set_items_based_on_mode()

  def change_push_pull_freq(self, event):
    new_freq = store.get(f"system.push_pull.freq")
    exp = self.pwm_exp["pushpull_freq"]

    if (event == Rotary.TAP):
      self.pwm_exp["pushpull_freq"] = (exp + 1) % self.max_freq_exp
      return self.render()
    elif (event == Rotary.INC):
      new_freq += (10 ** exp)
    elif (event == Rotary.DEC):
      new_freq -= (10 ** exp)

    self._set_pwms_freq([
      self.pwms["push_pull_one"],
      self.pwms["push_pull_two"],
      self.pwms["push_pull_offset"],
    ], new_freq)

    store.set("system.push_pull.freq", new_freq)
    self.restart_push_pull()
    self.render()

  def change_push_pull_duty(self, pwm, event):
    duty_path = f"system.push_pull.duty_{pwm}"
    new_duty = store.get(duty_path)
    exp_key = f"pushpull_duty_{pwm}"
    exp = self.pwm_exp[exp_key]

    if (event == Rotary.TAP):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
      return self.render()
    elif (event == Rotary.INC):
      new_duty += (10 ** exp)
    elif (event == Rotary.DEC):
      new_duty -= (10 ** exp)

    new_duty = max(0, min(1000, new_duty))
    store.set(duty_path, new_duty)
    self.set_push_pull_duty_by_mode()
    self.render()

  def change_freq(self, pwm, event):
    new_freq = store.get(f"system.{pwm}.freq")
    exp = self.pwm_exp[f"{pwm}_freq"]

    if (event == Rotary.TAP):
      self.pwm_exp[f"{pwm}_freq"] = (exp + 1) % self.max_freq_exp
      return self.render()
    elif (event == Rotary.INC):
      new_freq += (10 ** exp)
    elif (event == Rotary.DEC):
      new_freq -= (10 ** exp)

    # change the setting, the pwm will cannot handle every adjustment..
    # but the setting will increase, and eventually the pwm too.
    new_freq = max(2_000, min(5_000_000, new_freq))
    store.set(f"system.{pwm}.freq", new_freq)

    old_freq = self.pwms[pwm].freq()
    self.pwms[pwm].freq(new_freq)
    new_freq = self.pwms[pwm].freq()

    # If freq did not changed, but can be changed, repeat.
    if (old_freq == new_freq and 2_000 < new_freq < 5_000_000):
      return self.change_freq(pwm, event)

    store.set(f"system.{pwm}.freq", new_freq)

    set_pwm_channels([
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package),
    ], 1)

    self.render()

  def change_duty(self, pwm, event):
    new_duty = store.get(f"system.{pwm}.duty")
    exp = self.pwm_exp[f"{pwm}_duty"]

    if (event == Rotary.TAP):
      self.pwm_exp[f"{pwm}_duty"] = (exp + 1) % self.max_duty_exp
      return self.render()
    elif (event == Rotary.INC):
      new_duty += 10 ** exp
    elif (event == Rotary.DEC):
      new_duty -= 10 ** exp

    # change the setting, the pwm will cannot handle every adjustment..
    # but the setting will increase, and eventually the pwm too.
    new_duty = round(max(0, min(1000, new_duty)))
    store.set(f"system.{pwm}.duty", new_duty)
    self.pwms[pwm].duty_u16(round(65535 * new_duty / 1000))

    set_pwm_channels([
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package),
    ], 1)

    self.render()

  def _create_pulse_package_pwm_group(self):
    self.pwms["pulse"] = self._create_pwm(self.pin_pulse, store.get(PULSE_FREQ))
    self.pwms["pulse"].duty_u16(round(65535 * store.get(PULSE_DUTY) / 1000))
    self.pwms["package"] = self._create_pwm(self.pin_package, store.get(PACKAGE_FREQ))
    self.pwms["package"].duty_u16(round(65535 * store.get(PACKAGE_DUTY) / 1000))

    set_pwm_channels([
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package),
    ], 1)

  def _create_push_pull_pwm_group(self):
    freq = store.get(PUSHPULL_FREQ)

    self.pwms["push_pull_one"] = self._create_pwm(self.pin_push_pull_one, freq)
    self.pwms["push_pull_two"] = self._create_pwm(self.pin_push_pull_two, freq)
    self.pwms["push_pull_offset"] = self._create_pwm(self.pin_push_pull_offset, freq)

    set_channel_inverted(
      get_pins_slice(self.pin_push_pull_two),
      get_pins_channel(self.pin_push_pull_two)
    )

    # Start pwms..
    self.restart_push_pull()
    
    # Set duty
    self.set_push_pull_duty_by_mode()

  def restart_push_pull(self):
    slices = [
      get_pins_slice(self.pin_push_pull_one),
      get_pins_slice(self.pin_push_pull_two),
      get_pins_slice(self.pin_push_pull_offset)
    ]

    set_pwm_channels(slices, 1)

  def rotary_one_handler(self, event):
    if (event == Rotary.TAP):
      super().rotary_two_handler(event)
    else:
      super().rotary_one_handler(event)

  def set_push_pull_duty_by_mode(self):
    mode = store.get(PUSHPULL_MODE) # ADJUST / SYNC
    duty_push_pull_one = store.get(PUSHPULL_DUTY_ONE)

    if (mode == PUSHPULL_MODE_SYNC):
      duty_push_pull_two = 500 # 50% 
      duty_push_pull_offset = duty_push_pull_two + duty_push_pull_one
    elif (mode == PUSHPULL_MODE_ADJUST):
      duty_push_pull_two = store.get(PUSHPULL_DUTY_OFFSET)
      duty_push_pull_offset = store.get(PUSHPULL_DUTY_TWO) + duty_push_pull_two

    self.pwms["push_pull_one"].duty_u16(round(65535 * duty_push_pull_one / 1000))
    self.pwms["push_pull_two"].duty_u16(round(65535 * duty_push_pull_two / 1000))
    self.pwms["push_pull_offset"].duty_u16(round(65535 * duty_push_pull_offset / 1000))

  def _create_pwm(self, pin, freq=False):
    pwm = PWM(Pin(pin))
    if (freq):
      pwm.freq(freq)

    return pwm

  def _set_pwms_freq(self, pwms, freq):
    if (isinstance(pwms, PWM)):
      pwms = [pwms]

    for pwm in pwms:
      pwm.freq(freq)

  def _fill_pwm_settings(self):    
    self.pwm_exp["push_pull_freq"] = 4
    self.pwm_exp["push_pull_duty_one"] = 2
    self.pwm_exp["push_pull_duty_two"] = 4
    self.pwm_exp["push_pull_duty_offset"] = 4

def get_pins_slice(pin):
  return pin // 2 % 8
    
def get_pins_channel(pin):
  return "A" if pin % 2 == 0 else "B"
