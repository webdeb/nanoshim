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

from ui_program import (
  UIListProgram,
  TAP_LEFT,
  TAP_RIGHT,
  INC,
  DEC,
)

from pwm.piopwm import (
  PIOPWM,
  F1,
  F2,
  PACKAGE,
  BIGPACK
)

class Pwm(UIListProgram):
  max_freq_exp = 2 # 1Mhz. 1tick.. 2-10%, 3,50%
  max_duty_exp = 2 # 10000ns = 10ms
  
  title = "HACK PWM v0.0.3"
  pwm_exp = {
    "f1_freq": 0,
    "f1_duty": 0,
    "f2_low": 0,
    "f2_high": 0,
    "package_freq": 0,
    "package_duty": 0,
    "bigpack_freq": 0,
    "bigpack_duty": 0,
  }

  def __init__(self, on_exit):
    self.handle_button = on_exit
    self.items = [
      # """
      # F1
      # """
      {
        "text": [["F1:", self.get_exp("f1_freq")], self.get_freq_str(F1)],
        "handle_change": lambda event: self.change_freq(F1, event),
      },
      {
        "text": [["Duty:", self.get_exp("f1_duty")], self.get_duty_str(F1)],
        "handle_change": lambda event: self.change_duty(F1, event),
      },

      # """
      # F2
      # """
      {
        "text": [["F2:", self.get_exp("f2_freq")], self.get_freq_str(F2)],
        "handle_change": lambda event: self.change_freq(F2, event),
      },
      {
        "text": [["High:", self.get_exp("f2_high")], lambda: str(self.piopwm.get_high(F2))],
        "handle_change": lambda event: self.change_duty(F2, event),
      },

      # """
      # Package
      # """
      {
        "text": [["P:", self.get_exp("package_freq")], self.get_freq_str(PACKAGE)],
        "handle_change": lambda event: self.change_freq(PACKAGE, event),
      },
      {
        "text": [["Duty:", self.get_exp("package_duty")], self.get_duty_str(PACKAGE)],
        "handle_change": lambda event: self.change_duty(PACKAGE, event),
      },

      # """
      # BigPack
      # """
      {
        "text": [["BP: ", self.get_exp("bigpack_freq")], self.get_freq_str(BIGPACK)],
        "handle_change": lambda event: self.change_freq(BIGPACK, event),
      },
      {
        "text": [["Duty:", self.get_exp("bigpack_duty")], self.get_duty_str(BIGPACK)],
        "handle_change": lambda event: self.change_duty(BIGPACK, event),
      }
    ]

    self.piopwm = PIOPWM()
    super().__init__()

  def get_exp(self, exp_name):
    return lambda: "x" + str(self.pwm_exp[exp_name] + 1)
  def get_freq_str(self, pwm):
    return lambda: freq_to_str(self.piopwm.get_freq(pwm))
  def get_duty_str(self, pwm):
    return lambda: self.piopwm.get_duty_str(pwm)
  def get_low(self, pwm):
    return lambda: str(self.piopwm.get_low(pwm))
  def render(self):
    items_text = list(map(lambda i: i["text"], self.items))
    self.display.render_menu(self.title, items_text, self.selected_item)

  def change_freq(self, pwm, event):
    exp_key = pwm + "_freq"
    if (exp_key not in self.pwm_exp):
      self.pwm_exp[exp_key] = 0

    exp = self.pwm_exp[exp_key]

    if (event == TAP_LEFT):
      self.pwm_exp[exp_key] = (exp - 1) % self.max_freq_exp
    if (event == TAP_RIGHT):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_freq_exp
    elif (event == INC):
      self.piopwm.update_period(pwm, -1, exp)
    elif (event == DEC):
      self.piopwm.update_period(pwm, 1, exp)

    self.render()

  def change_duty(self, pwm, event):
    exp_key = pwm + "_duty"
    if (exp_key not in self.pwm_exp):
      self.pwm_exp[exp_key] = 0

    exp = self.pwm_exp[exp_key]

    if (event == TAP_LEFT):
      self.piopwm.switch_duty_mode(pwm)
    elif (event == TAP_RIGHT):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
    elif (event == INC):
      self.piopwm.update_duty(pwm, 1, exp)
    elif (event == DEC):
      self.piopwm.update_duty(pwm, -1, exp)

    self.render()

  def change_low(self, pwm, event):
    exp_key = pwm + "_low"
    if (exp_key not in self.pwm_exp):
      self.pwm_exp[exp_key] = 0

    exp = self.pwm_exp[exp_key]

    if (event == INC):
      self.piopwm.update_low(pwm, 1, exp)
    elif (event == DEC):
      self.piopwm.update_low(pwm, -1, exp)
    elif (event == TAP_RIGHT):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
    elif (event == TAP_LEFT):
      self.pwm_exp[exp_key] = (exp - 1) % self.max_duty_exp

    self.render()

  def change_high(self, pwm, event):
    exp_key = pwm + "_high"
    if (exp_key not in self.pwm_exp):
      self.pwm_exp[exp_key] = 0

    exp = self.pwm_exp[exp_key]

    if (event == INC):
      self.piopwm.update_high(pwm, 1, exp)
    elif (event == DEC):
      self.piopwm.update_high(pwm, -1, exp)
    elif (event == TAP_RIGHT):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
    elif (event == TAP_LEFT):
      self.pwm_exp[exp_key] = (exp - 1) % self.max_duty_exp

    self.render()

def freq_to_str(freq):
  if (freq < 1000):
    return str(round(freq, 1)) + "Hz"
  if (freq < 1_000_000):
    return str(round(freq / 1_000, 2)) + "kHz"
  else:
    return str(round(freq / 1_000_000, 2)) + "MHz"
