from machine import Pin
import time

def noop(_v):
  print("call handler..", _v)
  pass

class Rotary:
  INC = 1
  DEC = 2
  TAP = 4
  transition = 0

  def __init__(self, dt, clk, sw, handler=noop):
    self.dt_pin = Pin(dt, Pin.IN, Pin.PULL_UP)
    self.clk_pin = Pin(clk, Pin.IN, Pin.PULL_UP)
    self.sw_pin = Pin(sw, Pin.IN, Pin.PULL_UP)
    self.clk_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
    self.dt_pin.irq(handler=self.rotary_change, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
    self.last_status = (self.dt_pin.value() << 1) | self.clk_pin.value()

    # Switch
    self.sw_pin.irq(handler=self.switch_detect, trigger=Pin.IRQ_RISING)
    self.last_button_val = self.sw_pin.value()

    # One handler for every encoder
    self.set_handler(handler)

  def set_handler(self, handler):
    self.handler = handler

  def rotary_change(self, pin):
    new_status = (self.dt_pin.value() << 1) | self.clk_pin.value()
    if new_status == self.last_status:
      return

    self.transition = 0b11111111 & self.transition << 4 | self.last_status << 2 | new_status

    if self.transition == 23:
      self.handler(Rotary.INC)
    elif self.transition == 43:
      self.handler(Rotary.DEC)
    self.last_status = new_status

  def switch_detect(self, pin):
    if (self.switch_dead_time()):
      return

    self.handler(Rotary.TAP)

  _switch_dead_time = 0
  def switch_dead_time(self):

    now = time.ticks_ms()
    if (self._switch_dead_time < now):
      self._switch_dead_time = now + 200
      return False

    return True

if __name__ == "__main__":
  print("running rotary __main__")
  import user_inputs
