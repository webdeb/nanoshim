from machine import Pin
from utils import BUTTON_WAIT_MS
import time

def _nop(): pass

class Button:
  _switch_dead_time = 0

  def __init__(self, pin, handler=_nop) -> None:
    self.sw_pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    self.sw_pin.irq(handler=self._on_switch, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)
    self.set_handler(handler)

  def set_handler(self, handler):
    self._handler = handler

  _press_time = 0
  def _on_switch(self, pin):
    now = time.ticks_ms()
    pin_value = pin.value()
    if (self._press_time == 0 or pin_value == 0):
      self._press_time = now
      return
    elif((now - self._press_time) < BUTTON_WAIT_MS):
      self._press_time = 0
      return

    self._press_time = 0
    self._handler()
