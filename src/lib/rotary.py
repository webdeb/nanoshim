from machine import Pin
import time
import uasyncio as asyncio


def noop(_v):
    # print("call handler..", _v)
    pass


INC = 1
DEC = 2
TAP = 4


class Rotary:
    event = None
    transition = 0
    _press_time = float('inf')

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
        self._tsf = asyncio.ThreadSafeFlag()
        self._waiter = asyncio.create_task(self._run())

    def set_handler(self, handler):
        self.handler = handler

    def rotary_change(self, pin):
        new_status = (self.dt_pin.value() << 1) | self.clk_pin.value()
        if new_status == self.last_status:
            return

        self.transition = 0b11111111 & self.transition << 4 | self.last_status << 2 | new_status

        if self.transition in [23, 232]:
            self.event = INC
            self._tsf.set()
        elif self.transition in [43, 212]:
            self.event = DEC
            self._tsf.set()

        self.last_status = new_status

    """
    " Start Counter on pin 1
    " If release, check if pin is 0 and duration >300ms
    """

    def on_switch(self, pin):
        now = time.ticks_ms()
        pin_value = pin.value()

        if (pin_value == 0):
            self._press_time = now

        elif (pin_value == 1 and (now - self._press_time) > 300):
            self._press_time = float("inf")
            self.event = TAP
            self._tsf.set()

    async def _run(self):
        while True:
            await self._tsf.wait()
            self.handler(self.event)
