from machine import PWM, Pin
from store import store, PACKAGE_FREQ, PACKAGE_DUTY, PULSE_FREQ, PULSE_DUTY
from ui_program import UIListProgram
from pwm_register import set_divmode_in_channel
from rotary import Rotary

class Pwm(UIListProgram):
  package_pin = 10
  pulse_input_pin = 9
  pulse_output_pin = 8
  
  title = "PuPa / PuPu"
  pwm_exp = {}
  pwms = {}

  def __init__(self, on_exit):
    self.handle_button = on_exit
    self.items = [
      {
        "text": ["PulsF:", lambda: str(store.get("system.pulse.freq"))],
        "handle_change": lambda event: self.change_freq("pulse", event)
      },
      {
        "text": ["PulsD:", lambda: str(store.get("system.pulse.duty"))],
        "handle_change": lambda event: self.change_duty("pulse", event)
      },
      {
        "text": ["PackF:", lambda: str(store.get("system.package.freq"))],
        "handle_change": lambda event: self.change_freq("package", event)
      },
      {
        "text": ["PackD:", lambda: str(store.get("system.package.duty"))],
        "handle_change": lambda event: self.change_duty("package", event)
      }
    ]
    self._create_pulse_package_pwm_group()
    self._fill_pwm_settings()
    super().__init__()

  def change_freq(self, pwm, event):
    new_freq = store.get(f"system.{pwm}.freq")
    exp = self.pwm_exp[pwm]["freq_exp"]

    if (event == Rotary.TAP):
      self.pwm_exp[pwm]["freq_exp"] = (self.pwm_exp[pwm]["freq_exp"] + 1) % 4
      return self.render()
    elif (event == Rotary.INC):
      new_freq += 100 * (10 ** exp)
    elif (event == Rotary.DEC):
      new_freq -= 100 * (10 ** exp)

    # change the setting, the pwm will cannot handle every adjustment..
    # but the setting will increase, and eventually the pwm too.
    new_freq = max(2_000, min(5_000_000, new_freq))
    store.set(f"system.{pwm}.freq", new_freq)
    self.pwms[pwm].freq(new_freq)

    self.render()

  def change_duty(self, pwm, event):
    new_duty = store.get(f"system.{pwm}.duty")
    exp = self.pwm_exp[pwm]["duty_exp"]

    if (event == Rotary.TAP):
      self.pwm_exp[pwm]["duty_exp"] = (self.pwm_exp[pwm]["duty_exp"] + 1) % 5
      return self.render()
    elif (event == Rotary.INC):
      new_duty += 10 ** exp
    elif (event == Rotary.DEC):
      new_duty -= 10 ** exp

    # change the setting, the pwm will cannot handle every adjustment..
    # but the setting will increase, and eventually the pwm too.
    new_duty = round(max(0, min(65535, new_duty)))
    store.set(f"system.{pwm}.duty", new_duty)
    self.pwms[pwm].duty_u16(new_duty)

    self.render()

  def _create_pulse_package_pwm_group(self):
    pulse = PWM(Pin(self.pulse_output_pin))
    pulse.freq(store.get(PULSE_FREQ))
    pulse.duty_u16(round(store.get(PULSE_DUTY)))
    self.pwms["pulse"] = pulse
    # just assigns PIN to the PWM slice
    # self.pwms["pulse_input"] = PWM(
    #   Pin(self.pulse_input_pin, Pin.IN)
    # )

    set_divmode_in_channel(self.pulse_input_pin // 2 % 8)

    package = PWM(Pin(self.package_pin, Pin.PULL_DOWN))
    package.freq(store.get(PACKAGE_FREQ))
    package.duty_u16(round(store.get(PACKAGE_DUTY)))
    self.pwms["package"] = package

  def _fill_pwm_settings(self):
    for key, pwm in self.pwms.items():
      setting = {
        "freq_exp": 2,
        "duty_exp": 0,
      }

      self.pwm_exp[key] = setting

