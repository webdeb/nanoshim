import rp2
from machine import Pin
import time


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)[T3 - 1]
    jmp(not_x, "do_zero")   .side(1)[T1 - 1]
    jmp("bitloop")          .side(1)[T2 - 1]
    label("do_zero")
    nop()                   .side(0)[T2 - 1]
    wrap()


class RGBLED:
    red = (155, 0, 0)
    green = (0, 155, 0)
    orange = (155, 90, 20)
    blue = (0, 0, 155)

    def __init__(self, pin):
        self.pin = Pin(pin)
        self.sm = rp2.StateMachine(
            0, ws2812, freq=8_000_000, sideset_base=self.pin)

    def stop(self):
        self.off()
        self.sm.active(0)

    def on(self, color=(55, 55, 55)):
        (r, g, b) = color
        self.sm.active(1)
        self.sm.put(r << 24 | g << 16 | b << 8)

    def off(self):
        self.sm.put(0x000000)
        # self.sm.active(0)

    def multicolor(self, ms=3000):
        start_ms = time.ticks_ms()

        # self.is_multicolor = 1
        self.sm.active(1)
        max_lum = 100
        r, g, b = 0, 0, 0

        while start_ms + ms > time.ticks_ms():
            for i in range(0, max_lum):
                r = i
                b = max_lum - i
                rgb = (g << 24) | (r << 16) | (b << 8)
                self.sm.put(rgb)
                time.sleep_ms(10)
            time.sleep_ms(100)
            for i in range(0, max_lum):
                g = i
                r = max_lum - i
                rgb = (g << 24) | (r << 16) | (b << 8)
                self.sm.put(rgb)
                time.sleep_ms(10)
            time.sleep_ms(100)
            for i in range(0, max_lum):
                b = i
                g = max_lum - i
                rgb = (g << 24) | (r << 16) | (b << 8)
                self.sm.put(rgb)
                time.sleep_ms(10)
            time.sleep_ms(100)
