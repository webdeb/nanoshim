from machine import Pin

def noop(_v):
  pass

class Rotary:
  INC = 1
  DEC = 2
  TAP = 4
  transition = 0

  def __init__(self, dt, clk, sw, handler=noop):
    self.clk_pin = Pin(clk, Pin.IN, Pin.PULL_UP)
    self.dt_pin = Pin(dt, Pin.IN, Pin.PULL_UP)
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
    self.handler(Rotary.TAP)
