from misc.rgbled import Led
import time


def simboot():
    for _ in range(3):
        Led(Led.COLORS.blue)
        time.sleep_ms(500)
        Led(Led.COLORS.cyan)
        Led.off()
        time.sleep_ms(500)
        Led(Led.COLORS.red)
        time.sleep_ms(500)

    # led.on(led.green)
    Led.off()
