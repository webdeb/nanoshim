from machine import Pin
from neopixel import NeoPixel
from lib.constants import PIN_RGB_LED
import misc.colors as colors


class LED(NeoPixel):
    intensity = 0.05
    COLORS = colors

    def __init__(self, pin: Pin, n: int, *, bpp: int = 3, timing=1):
        super().__init__(pin, n, bpp=bpp, timing=timing)
        self.off()

    def __call__(self, color):
        print("Led ..", color)
        color = (
            round(color[0] * self.intensity),
            round(color[1] * self.intensity),
            round(color[2] * self.intensity)
        )

        self[0] = color
        self.write()

    def off(self):
        self(LED.COLORS.off)


Led = LED(Pin(PIN_RGB_LED), 1)
