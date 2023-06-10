import micropython
from misc.rgbled import RGBLED
import time


def simboot():
    # just for fun let it boot 3 seconds..
    led = RGBLED(16)

    # # 1 sec led it blink red 10 times
    # for _ in range(3):
    #   led.on(led.red)
    #   time.sleep_ms(300)
    #   led.off()
    #   time.sleep_ms(300)

    # # 2. sec let it blink 5 times yellow, 5 blue and 10 times green
    # for _ in range(5):
    #   led.on(led.orange)
    #   time.sleep_ms(100)
    #   led.off()
    #   time.sleep_ms(100)

    for _ in range(3):
        led.on(led.blue)
        time.sleep_ms(50)
        led.off()
        time.sleep_ms(50)

    # led.on(led.green)
    led.stop()
