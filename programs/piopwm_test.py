from rp2 import PIO, asm_pio, StateMachine
import pwm.piopwm_store as store
from machine import Pin
import machine

from time import sleep

pin_f1 = Pin(14)
pin_f2 = Pin(11)
pin_package = Pin(10)
pin_bigpack = Pin(13)

F1 = "f1"
F2 = "f2"
PACKAGE = "package"
BIGPACK = "bigpack"

DUTY_MODES = [
  store.DUTY_CYCLES,
  store.DUTY_PERCENT
]

# ALL PWM Programms have the same default min LOW/HIGH/PERIOD
LOW = 4;
HIGH = 1;
PERIOD = LOW + HIGH

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program_high_low():
  label("reload")
  pull()
  out(isr, 32)
  pull()

  wrap_target()
  mov(x, osr)                      # l
  mov(y, isr)                      # l
  wait(1, pin, 0)                  # l
  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x
  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program_low_high():
  label("reload")
  pull()
  out(isr, 32)
  pull()

  wrap_target()

  mov(x, osr)         .side(0)     # l
  mov(y, isr)                      # l
  wait(1, pin, 0)                  # l

  label("low")
  jmp(x_dec, "low")                # l + x
  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y

  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_program_high_low():
  label("reload")
  pull()
  out(isr, 32)
  pull()

  wrap_target()
  mov(x, osr)                      # l
  mov(y, isr)                  [1] # 2xl just to have the same low periods
  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x
  wrap()

class PIOPWM:
  pwm = {}
  def __init__(self):
    # Cleanup memory
    PIO(0).remove_program()

    self.pwm[F1] = StateMachine(0, pwm_with_pin_program_high_low, in_base=pin_package, sideset_base=pin_f1, freq=125_000_000)
    self.update(F1)

    self.pwm[F2] = StateMachine(1, pwm_with_pin_program_low_high, in_base=pin_f1, sideset_base=pin_f2, freq=125_000_000)
    sm_pwm_set_params(self.pwm[F2], store.get_high(self.pwm[F2]),  store.get_low(self.pwm[F2]))
    self.pwm[F2].active(1)

    self.pwm[PACKAGE] = StateMachine(2, pwm_with_pin_program_high_low, in_base=pin_bigpack, sideset_base=pin_package, freq=125_000_000)
    self.update(PACKAGE)

    self.pwm[BIGPACK] = StateMachine(3, pwm_program_high_low, sideset_base=pin_bigpack, freq=125_000_000)
    self.update(BIGPACK)

  def get_duty_str(self, pwm):
    pwm_duty_mode = store.get_duty_mode(pwm)
    if (pwm_duty_mode == store.DUTY_PERCENT):
      return str(self.get_duty_percent(pwm)) + "%"
    return str(store.get_duty(pwm) + HIGH)

  def get_duty(self, pwm):
    return store.get_duty(pwm) + HIGH

  def set_duty_mode(self, pwm, mode):
    store.set_duty_mode(pwm, mode)

  def switch_duty_mode(self, pwm):
    idx = DUTY_MODES.index(store.get_duty_mode(pwm) or store.DUTY_CYCLES)
    new_duty_mode = DUTY_MODES[(idx + 1) % len(DUTY_MODES)]
    self.set_duty_mode(pwm, new_duty_mode)

  def get_duty_ns(self, pwm):
    duty = store.get_duty(pwm) + HIGH
    return round(1/machine.freq() * duty * 1e9)

  def get_duty_percent(self, pwm):
    duty = store.get_duty(pwm) + HIGH
    return round(duty / (store.get_period(pwm) + PERIOD) * 100, 2)

  def get_freq(self, pwm):
    period = store.get_period(pwm) + PERIOD
    return round(machine.freq()/period)

  def set_period(self, pwm, period):
    # If duty_mode Percent.. recalculate
    current_period = store.get_period(pwm)
    if (store.get_duty_mode(pwm) is store.DUTY_PERCENT):
      duty = round(store.get_duty(pwm) / current_period * period)
      store.set_duty(pwm, duty)

    store.set_period(pwm, period)
    self.update(pwm)

  def set_duty(self, pwm, value = 0):
    value = value or store.get_duty(pwm)
    period = store.get_period(pwm)
    value = max(value, -1)
    value = min(value, period - 2)
    store.set_duty(pwm, value)

    self.update(pwm)

  def update(self, pwm):
    period = store.get_period(pwm)
    duty = store.get_duty(pwm)
    x = period - duty

    sm = self.pwm[pwm]
    sm_pwm_set_params(sm, x, duty)
    sm.active(1)

  def update_period(self, pwm, inc, factor):
    period = store.get_period(pwm)
    new_period = period + (10**factor) * inc
    new_period = max(1, new_period)
    self.set_period(pwm, new_period)

  def update_duty(self, pwm, inc, factor):
    duty = store.get_duty(pwm)
    new_duty = duty + (10**factor) * inc
    if (pwm == F1):
      new_duty = min(store.get_duty(PACKAGE), new_duty)
    if (pwm == PACKAGE):
      new_duty = min(store.get_duty(BIGPACK), new_duty)
      new_duty = max(store.get_period(F1), new_duty)

    new_duty = max(1, new_duty)
    self.set_duty(pwm, new_duty)

  def update_low(self, pwm, inc, factor):
    low = store.get_low(pwm) + inc * factor
    store.set_low(pwm, low)
    sm_pwm_set_params(self.pwm[pwm], store.get_high(pwm), low)

  def update_high(self, pwm, inc, factor):
    high = store.get_high(pwm) + inc * factor
    store.set_high(pwm, high)
    sm_pwm_set_params(self.pwm[pwm], high, store.get_low(pwm))

  def get_low(self, pwm):
    return store.get_low(pwm)

  def get_high(self, pwm):
    return store.get_high(pwm)

def sm_pwm_set_params(sm, low, high):
  sm.put(high)
  sm.put(low)
  sm.restart()
