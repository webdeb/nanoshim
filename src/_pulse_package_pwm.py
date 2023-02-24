import machine
from machine import PWM, Pin
from store_steps import (
  store,
  PULSE_FREQ,
  PULSE_DUTY,
  PACKAGE_FREQ,
  PACKAGE_DUTY,
  # PACKAGE_FREQ,
  # PACKAGE_DUTY,
)
from ui_program import UIListProgram
from rotary import Rotary
from pwm_register import (
  set_pwm_channels,
  PWM_REGISTERS,
)

MIN_FREQ = 2
MAX_FREQ = 65534

def wrap_to_freq(period):
  print("wrap to freq", period)
  return int(machine.freq() / (period + 1))

def cc_to_ns(period):
  print("cc to ns", period)
  return int(1/machine.freq() * period)

class Pwm(UIListProgram):
  # Pulse & Package
  pin_pulse = 10
  pin_package = 14

  max_freq_exp = 4
  max_duty_exp = 3
  
  title = "HACK PWM v0.0.2"
  pwm_exp = {
    "pulse_freq": 1,
    "pulse_duty": 1,
    "package_freq": 1,
    "package_duty": 1,
  }
  pwms = {}

  def __init__(self, on_exit):
    self.handle_button = on_exit
    self.items = [
      {
        "text": [["PuFreq:", lambda: f"{self.pwm_exp['pulse_freq']+1}x"], lambda: self.get_pulse_freq_str()],
        "handle_change": lambda event: self.change_pulse_period(event),
        "exp": "pulse_freq",
      },
      {
        "text": ["PuDuty:", lambda: self.get_pulse_duty_str()],
        "handle_change": lambda event: self.change_pulse_duty(event),
        "exp": "pulse_duty", 
      }
      # {
      #   "text": ["Pack Len:", lambda: self.get_pack_freq_str()],
      #   "handle_change": lambda event: self.change_pack_period(event),
      #   "exp": "package_freq",
      # },
      # {
      #   "text": ["Pack Pause:", lambda: self.get_pack_duty_str()],
      #   "handle_change": lambda event: self.change_pack_duty(event),
      #   "exp": "package_duty",
      # },
    ]

    self.pins_channels = {
      "pulse": (get_pins_slice(self.pin_pulse), get_pins_channel(self.pin_pulse)),
      "package": (get_pins_slice(self.pin_package), get_pins_channel(self.pin_package)),
    }

    # self._create_pulse_package_pwm_group()
    super().__init__()


  def get_pulse_freq_str(self):
    freq = machine.freq()/store.get(PULSE_FREQ)
    print(freq, machine.freq(), store.get(PULSE_FREQ))
    return str(int(freq))

  def get_pulse_duty_str(self):
    return "0000"

  def get_pack_freq_str(self):
    return "0000"

  def get_pack_duty_str(self):
    return "0000"

  def render(self):
    items_text = list(map(lambda i: i["text"], self.items))
    exp = None

    if ("exp" in self.items[self.selected_item]):
      exp = self.pwm_exp[self.items[self.selected_item]["exp"]]

    self.display.render_menu(self.title, items_text, self.selected_item, exp)

  def change_pulse_period(self, event):
    """
    A default PWM procedure to change
    """
    (pulse_slice, _) = self.pins_channels["pulse"]
    pulse_reg = PWM_REGISTERS[pulse_slice]
    pulse_wrap = pulse_reg.TOP.WRAP
    exp = 10**self.pwm_exp["pulse_freq"]

    if (event == Rotary.TAP):
      self.pwm_exp["pulse_freq"] = (1 + self.pwm_exp["pulse_freq"]) % 7
      self.render()
      return
    elif (event == Rotary.INC):
      pulse_wrap -= 1 * exp
    elif (event == Rotary.DEC):
      pulse_wrap += 1 * exp

    pulse_wrap = max(2, min(pulse_wrap, 65535))
    pulse_reg.TOP.WRAP = pulse_wrap
    store.set(PULSE_FREQ, pulse_wrap)

    self.render()

  def change_pulse_duty(event):
    pass

  def change_freq(self, pwm, event):
    (pulse_slice, _) = self.pins_channels["pulse"]
    pulse_reg = PWM_REGISTERS[pulse_slice]
    pulse_wrap = pulse_reg.TOP.WRAP

    (package_slice, package_channel) = self.pins_channels["package"]
    package_reg = PWM_REGISTERS[package_slice]
    package_wrap = package_reg.TOP.WRAP
    package_len = int(store.get(PACKAGE_LENGTH))
    package_pause = int(store.get(PACKAGE_PAUSE))

    # new_freq = int(store.get(f"system.{pwm}.freq"))
    # exp = self.pwm_exp[f"{pwm}_freq"]

    # if (event == Rotary.TAP):
    #   self.pwm_exp[f"{pwm}_freq"] = (exp + 1) % self.max_freq_exp
    #   return self.render()

    """
      If pulse is changing, change the package freq to a multiple of pulse.
      If package is changing, change it to the next multiple of pulse.
    """
    if (pwm == "pulse"):
      if (event == Rotary.INC):
        pulse_wrap -= 1
      elif (event == Rotary.DEC):
        pulse_wrap += 1

      pulse_wrap = max(2, min(65535, pulse_wrap))
      pulse_reg.TOP.WRAP = pulse_wrap
      package_reg.TOP.WRAP = (package_len + package_pause) * pulse_wrap

    elif (pwm == "package"):
      current_multiple = round(
        PWM_REGISTERS[self.pins_channels["package"][0]].TOP.WRAP /
        PWM_REGISTERS[self.pins_channels["pulse"][0]].TOP.WRAP
      )

      if (event == Rotary.INC):
        multiple_change = -1
      else:
        multiple_change = 1
      
      PWM_REGISTERS[self.pins_channels["package"][0]].TOP.WRAP = (current_multiple + multiple_change) * new_freq

    store.set(PULSE_FREQ, pulse_reg.TOP.WRAP)
    store.set(PACKAGE_LENGTH, package_reg.TOP.WRAP - package_reg.COMPARE[package_channel])
    store.set(PACKAGE_PAUSE, package_reg.COMPARE[package_channel])

    (pulse_slice, package_slice) = self.get_pulse_package_slices()
    set_pwm_channels([pulse_slice, package_slice], 1)
    self.render()


  def get_pulse_package_slices(self):
    return (
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package)
    )

  def change_duty(self, pwm, event):
    new_duty = int(store.get(f"system.{pwm}.duty"))
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
    new_duty = round(max(0, min(MAX_FREQ, new_duty)))
    store.set(f"system.{pwm}.duty", new_duty)
    self.pwms[pwm].duty_u16(round(65535 * new_duty / 1000))

    set_pwm_channels([
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package),
    ], 1)

    self.render()

  def _create_pulse_package_pwm_group(self):
    print("Creating.. pwms", store.get(PULSE_FREQ))

    self.pwms["pulse"] = self._create_pwm(self.pin_pulse, store.get(PULSE_FREQ))
    self.pwms["pulse"].duty_u16(store.get(PULSE_DUTY))

    self.pwms["package"] = self._create_pwm(self.pin_package, store.get(PACKAGE_FREQ))
    self.pwms["package"].duty_u16(store.get(PACKAGE_LENGTH))

    set_pwm_channels([
      get_pins_slice(self.pin_pulse),
      get_pins_slice(self.pin_package),
    ], 1)

  def _create_pwm(self, pin, freq=False):
    pwm = PWM(Pin(pin))

    if (freq):
      PWM_REGISTERS[get_pins_slice(pin)].TOP.WARP = freq

    return pwm

  def _set_pwms_freq(self, pwms, freq):
    if (isinstance(pwms, PWM)):
      pwms = [pwms]

    for pwm in pwms:
      pwm.freq(freq)

def get_pins_slice(pin):
  return pin // 2 % 8
    
def get_pins_channel(pin):
  return "A" if pin % 2 == 0 else "B"
