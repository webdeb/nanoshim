from hackpwm import PWMSystem
from lib.constants import OUT1, OUT2, OUT3, OUT4, PIN_GP02
from hackpwm.programs import PWM
from machine import Pin

Pin(PIN_GP02, Pin.OUT, Pin.PULL_DOWN)

PWMSystem("PULS Pack", [
    PWM("Pulse", pin=OUT1, wait_pin=OUT2),
    PWM("Mod 1", pin=OUT2, wait_pin=OUT3),
    PWM("Mod X", pin=OUT3, wait_pin=PIN_GP02),
])
