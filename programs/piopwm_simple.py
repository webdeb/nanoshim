from rp2 import PIO, asm_pio, StateMachine
# import pwm.piopwm_store as store
from machine import Pin

# ALL PWM Programms have the same default min LOW/HIGH/PERIOD
LOW = 5
HIGH = 1;
PERIOD = LOW + HIGH

@asm_pio(sideset_init=PIO.OUT_LOW, autopull=True)
def pwm_with_pin_program():
  label("load")
  out(isr, 32)
  out(null, 32)

  wrap_target()

  mov(y, isr)                      # l
  mov(x, osr)                      # l
  jmp(not_y, "load")               # l

  wait(1, pin, 0)                  # l
  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x

  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW, autopull=True)
def pwm_with_pin_program_inverted():
  label("load")
  out(isr, 32)
  out(null, 32)

  wrap_target()

  mov(y, isr)         .side(0)     # l
  jmp(not_y, "load")               # l (dont care about "load" delay)
  mov(x, osr)                      # l

  wait(1, pin, 0)                  # l
  label("low")
  jmp(x_dec, "low")                # l + x
  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y
  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW, autopull=True)
def pwm_program():
  label("load")
  out(isr, 32)
  out(null, 32)

  wrap_target()
  mov(x, osr)                      # l
  mov(y, isr)                  [1] # 2xl just to have the same low periods
  jmp(not_y, "load")               # l (dont care about "load" delay)

  label("high")
  jmp(y_dec, "high")  .side(1)     # h + y
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x
  wrap()

NORMAL = 0
WITH_PIN = 1
WITH_PIN_INVERTED = 2

class PIOPWM:
  def __init__(self, id, pin, high, low, mode=NORMAL, in_pin=None):
    if (mode == NORMAL):
      sm = StateMachine(id, prog=pwm_program, sideset_base=Pin(pin))
    elif (mode == WITH_PIN):
      if (in_pin == None):
        raise Exception("Define in_pin")
      sm = StateMachine(id, prog=pwm_with_pin_program, sideset_base=Pin(pin), in_base=Pin(in_pin))

    elif (mode == WITH_PIN_INVERTED):
      if (in_pin == None):
        raise Exception("Define in_pin")
      sm = StateMachine(id, prog=pwm_with_pin_program_inverted, sideset_base=Pin(pin), in_base=Pin(in_pin))
    else:
      raise Exception("Define Mode")

    self.sm = sm
    self.set_params(high, low)

  

  def set_params(self, high, low):
    self.sm.put(min(1<<31, max(HIGH, high - HIGH)))
    self.sm.put(min(1<<31, max(LOW, low - LOW)))
    self.sm.exec("in_(null, 32)") # clear isr which forces a jump to "load"

