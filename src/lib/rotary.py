from machine import Pin
import time


def noop(_v):
    # print("call handler..", _v)
    pass


class Rotary:
    INC = 1
    DEC = 2
    TAP = 4
    transition = 0

    def __init__(self, clk, sw, dt, handler=noop):
        self.dt_pin = Pin(dt, Pin.IN, Pin.PULL_UP)
        self.clk_pin = Pin(clk, Pin.IN, Pin.PULL_UP)
        self.clk_pin.irq(handler=self.rotary_change,
                         trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.sw_pin = Pin(sw, Pin.IN, Pin.PULL_UP)
        self.dt_pin.irq(handler=self.rotary_change,
                        trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.last_status = (self.dt_pin.value() << 1) | self.clk_pin.value()

        # Switch
        self.sw_pin.irq(handler=self.on_switch,
                        trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

        # One handler for every encoder
        self.set_handler(handler)

    def set_handler(self, handler):
        self.handler = handler

    def rotary_change(self, pin):
        new_status = (self.dt_pin.value() << 1) | self.clk_pin.value()
        if new_status == self.last_status:
            return

        self.transition = 0b11111111 & self.transition << 4 | self.last_status << 2 | new_status

        if self.transition in [23, 232]:
            self.handler(Rotary.INC)
        elif self.transition in [43, 212]:
            self.handler(Rotary.DEC)
        self.last_status = new_status

    _press_time = 0

    def on_switch(self, pin):
        now = time.ticks_ms()
        pin_value = pin.value()
        if (self._press_time == 0 or pin_value == 0):
            self._press_time = now
            return
        elif ((now - self._press_time) < 10):
            self._press_time = 0
            return

        self._press_time = 0
        self.handler(Rotary.TAP)
