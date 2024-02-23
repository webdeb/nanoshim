import uasyncio as asyncio
from machine import ADC
import time
import gc


class Levels:
    _last_level = None
    debounce_ms = 30
    none_level = 65000
    callbacks = {}
    long_callbacks = {}
    long_press = 1000

    def __init__(self, pin, levels, cb):
        self.cb = cb
        self.levels = sorted(levels)
        self.adc = ADC(pin)
        self._run = asyncio.create_task(self.watch())

    def on(self, level, cb):
        self.callbacks[level] = cb

    def on_long(self, level, cb):
        self.long_callbacks[level] = cb

    async def watch(self):
        while True:
            for level in self.levels:
                if self.is_level(self.adc.read_u16(), level):
                    start = time.ticks_ms()
                    long_press = False
                    press_duration = 0

                    # wait hold
                    while (True):
                        is_level = self.is_level(
                            self.adc.read_u16(), level)

                        if (not is_level):
                            break

                        press_duration = time.ticks_ms() - start
                        if (press_duration > 1000):
                            long_press = True
                            break

                        await asyncio.sleep_ms(1)

                    if (long_press):
                        asyncio.create_task(self._long_cb(level))
                    elif (press_duration > 10):
                        asyncio.create_task(self._cb(level))

                    await self.wait_release(level)
                    gc.collect()
                    break

            await asyncio.sleep_ms(self.debounce_ms)

    async def wait_release(self, level):
        while (True):
            adc_level = self.adc.read_u16()
            is_level = self.is_level(adc_level, level)
            if (not is_level):
                break
            await asyncio.sleep_ms(1)

        return True

    async def _long_cb(self, level):
        if (level in self.long_callbacks and callable(self.long_callbacks[level])):
            self.long_callbacks[level]()

    async def _cb(self, level):
        if (level in self.callbacks and callable(self.callbacks[level])):
            self.callbacks[level]()
        else:
            self.cb(level)

    def is_level(self, state, level):
        # Determine the correct level by providing a narrow window for the level
        return min(level - 3000, level * 0.2) < state < max(level * 1.2, level + 3000)


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
