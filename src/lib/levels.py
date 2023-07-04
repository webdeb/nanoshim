import uasyncio as asyncio
from machine import ADC
import time


class Levels:
    _last_level = None
    debounce_ms = 1
    none_level = 65000
    callbacks = {}

    def __init__(self, pin, levels, cb):
        self.cb = cb
        self.levels = sorted(levels)
        self.adc = ADC(pin)
        self._run = asyncio.create_task(self.watch())

    def on(self, level, cb):
        self.callbacks[level] = cb

    async def watch(self):
        while True:
            state = self.adc.read_u16()
            for level in self.levels:
                if self.is_level(state, level):
                    # The same level must be hold for some time to trigger,
                    # to avoid spontanous triggering due to static discharges etc.
                    # await asyncio.sleep_ms(5)

                    if self.is_level(self.adc.read_u16(), level) and await self.release():
                        asyncio.create_task(self._cb(level))
                        self._last_level = level
                        break
            await asyncio.sleep_ms(self.debounce_ms)

    async def release(self):
        now = time.ticks_ms()
        while (now + 1000) > time.ticks_ms():
            if self.is_level(self.adc.read_u16(), self.none_level):
                return True
            await asyncio.sleep_ms(1)

        return False

    async def _cb(self, level):
        if (level in self.callbacks and callable(self.callbacks[level])):
            self.callbacks[level]()
        else:
            self.cb(level)

    def is_level(self, state, level):
        # Determine the correct level by providing a narrow window for the level
        return min(level - 1000, level * 0.8) < state < max(level * 1.2, level + 1000)


"""
Usage (in an asyc context)

SW1 = 3000
SW2 = 10000
ADC_PIN = 0
Buttons = Levels(
    pin=ADC_PIN,
    levels=(SW1, SW2),
    cb=lambda level: print(level)
)

Buttons.on(SW1, lambda: print("SW1 pressed"))
Buttons.on(SW2, lambda: print("SW2 pressed"))
"""
