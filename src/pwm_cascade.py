from rp2 import PIO, asm_pio, StateMachine
from machine import Pin
import machine
import storecopy as store

pin_bigpack = 9
pin_pulse = 14
pin_package = 10

PULSE = "pulse"
PACKAGE = "package"
BIGPACK = "bigpack"

HIGH = 0; LOW = 1; PERIOD = 2
PROGRAM_PERIODS = {
  PULSE: [2, 3, 4], # 2 high, 2 low
  PACKAGE: [4, 3, 7], # 4 high, 3 low
  BIGPACK: [3, 3, 6] # 4 high, 3 low
}

DUTY_MODES = [
  store.DUTY_CYCLES,
  store.DUTY_PERCENT
]

@asm_pio(sideset_init=PIO.OUT_LOW)
def pulse_program():
  wrap_target()
  wait(0, irq, 4)                  # l
  mov(x, osr)                      # l
  mov(y, isr)         .side(1)     # h
  label("high")
  jmp(y_dec, "high")               # h + y
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x
  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW)
def package_program():
  wrap_target()
  mov(x, osr)                     # l
  wait(0, irq, 5)                 # l
  mov(y, isr)         .side(1)    # h
  irq(clear, 4)                   # h
  label("high")
  jmp(y_dec, "high")              # h + y
  irq(4) # Disable pulse          # h
  label("low")
  jmp(x_dec, "low")   .side(0)    # l + x
  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW)
def bigpack_program():
  wrap_target()
  mov(x, osr)                      # l
  mov(y, isr)         .side(1)     # h
  irq(clear, 5)                    # h
  label("high")
  jmp(y_dec, "high")               # h + y
  irq(5)              .side(0)     # l
  label("low")
  jmp(x_dec, "low")                # l + x
  wrap()                           

class PIOPWM:
  pwm = {}
  def __init__(self):
    # Cleanup memory
    PIO(0).remove_program()

    self.pwm[BIGPACK] = StateMachine(2, bigpack_program, sideset_base=Pin(pin_bigpack), freq=125_000_000)
    self.set_period(BIGPACK, store.get_period(BIGPACK))
    self.set_duty(BIGPACK, store.get_duty(BIGPACK))

    self.pwm[PACKAGE] = StateMachine(1, package_program, sideset_base=Pin(pin_package), freq=125_000_000)
    self.set_period(PACKAGE, store.get_period(PACKAGE))
    self.set_duty(PACKAGE, store.get_duty(PACKAGE))

    self.pwm[PULSE] = StateMachine(0, pulse_program, sideset_base=Pin(pin_pulse), freq=125_000_000)
    self.set_period(PULSE, store.get_period(PULSE))
    self.set_duty(PULSE, store.get_duty(PULSE))

  def get_duty_str(self, pwm):
    pwm_duty_mode = store.get_duty_mode(pwm)
    if (pwm_duty_mode == store.DUTY_PERCENT):
      return str(self.get_duty_percent(pwm)) + "%"
    return str(store.get_duty(pwm) + PROGRAM_PERIODS[pwm][HIGH])

  def get_duty(self, pwm):
    return store.get_duty(pwm) + PROGRAM_PERIODS[pwm][HIGH]

  def set_duty_mode(self, pwm, mode):
    store.set_duty_mode(pwm, mode)

  def switch_duty_mode(self, pwm):
    idx = DUTY_MODES.index(store.get_duty_mode(pwm) or store.DUTY_CYCLES)
    new_duty_mode = DUTY_MODES[(idx + 1) % len(DUTY_MODES)]
    self.set_duty_mode(pwm, new_duty_mode)

  def get_duty_ns(self, pwm):
    duty = store.get_duty(pwm) + PROGRAM_PERIODS[pwm][HIGH]
    return round(1/machine.freq() * duty * 1e9)

  def get_duty_percent(self, pwm):
    duty = store.get_duty(pwm) + PROGRAM_PERIODS[pwm][HIGH]
    return round(duty / (store.get_period(pwm) + PROGRAM_PERIODS[pwm][PERIOD]) * 100, 2)

  def get_freq(self, pwm):
    period = store.get_period(pwm) + PROGRAM_PERIODS[pwm][PERIOD]
    return round(machine.freq()/period)

  def set_period(self, pwm, period):
    # If duty_mode Percent.. recalculate
    if (store.get_duty_mode(pwm) is store.DUTY_PERCENT):
      duty = round(store.get_duty(pwm) / store.get_period(pwm) * period)
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
    sm.active(0)
    sm.put(duty)
    sm.exec("pull()")
    sm.exec("mov(isr, osr)")
    sm.put(x)
    sm.exec("pull()")
    sm.active(1)

  def update_period(self, pwm, inc, factor):
    period = store.get_period(pwm)
    new_period = period + (10**factor) * inc
    if (pwm == PULSE):
      package_period = store.get_period(PACKAGE)
      new_period = min(package_period, new_period)
    if (pwm == PACKAGE):
      bigpack_period = store.get_period(BIGPACK)
      new_period = min(bigpack_period, new_period)

    new_period = max(1, new_period)
    self.set_period(pwm, new_period)

  def update_duty(self, pwm, inc, factor):
    duty = store.get_duty(pwm)
    new_duty = duty + (10**factor) * inc
    if (pwm == PULSE):
      package_duty = store.get_duty(PACKAGE)
      new_duty = min(package_duty, new_duty)
    if (pwm == PACKAGE):
      bigpack_duty = store.get_duty(BIGPACK)
      new_duty = min(bigpack_duty, new_duty)

    new_duty = max(1, new_duty)
    self.set_duty(pwm, new_duty)
