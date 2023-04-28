from ui_program import (
  UIListProgram,
  TAP_LEFT,
  TAP_RIGHT,
  INC,
  DEC,
)

from old.multipwm import (
  MULTIPWM,
  F1,
  F2,
  PACKAGE,
)

class Pwm(UIListProgram):
  max_freq_exp = 7 # 1Mhz.
  max_duty_exp = 7 # 10000ns = 10ms
  
  title = "HACK PWM v0.0.3"
  pwm_exp = {
    "pulse_freq": 0,
    "pulse_duty": 0,
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
        "text": [["Duty:", self.get_exp("f2_duty")], self.get_duty_str(F2)],
        "handle_change": lambda event: self.change_duty(F2, event),
      },
      {
        "text": [["Phase:"], self.get_phase(F2)],
        "handle_change": lambda event: self.change_phase(F2, event),
      },

      # """
      # Package
      # """
      {
        "text": [["P: ", self.get_exp("package_freq")], self.get_freq_str(BIGPACK)],
        "handle_change": lambda event: self.change_freq(PACKAGE, event),
      },
      {
        "text": [["Duty:", self.get_exp("package_duty")], self.get_duty_str(BIGPACK)],
        "handle_change": lambda event: self.change_duty(PACKAGE, event),
      },
    ]

    self.pwmcontroller = MULTIPWM()
    super().__init__()

  def get_exp(self, exp_name):
    return lambda: "x" + str(self.pwm_exp[exp_name] + 1)
  def get_freq_str(self, pwm):
    return lambda: freq_to_str(self.pwmcontroller.get_freq(pwm))
  def get_duty_str(self, pwm):
    return lambda: self.pwmcontroller.get_duty_str(pwm)

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
      self.pwmcontroller.update_period(pwm, -1, exp)
    elif (event == DEC):
      self.pwmcontroller.update_period(pwm, 1, exp)

    self.render()

  def change_duty(self, pwm, event):
    exp_key = pwm + "_duty"
    if (exp_key not in self.pwm_exp):
      self.pwm_exp[exp_key] = 0

    exp = self.pwm_exp[exp_key]

    if (event == TAP_LEFT):
      return
    elif (event == TAP_RIGHT):
      self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
    elif (event == INC):
      self.pwmcontroller.update_duty(pwm, 1, exp)
    elif (event == DEC):
      self.pwmcontroller.update_duty(pwm, -1, exp)

    self.render()

def freq_to_str(freq):
  if (freq < 1000):
    return str(round(freq, 1)) + "Hz"
  if (freq < 1_000_000):
    return str(round(freq / 1_000, 2)) + "kHz"
  else:
    return str(round(freq / 1_000_000, 2)) + "MHz"
