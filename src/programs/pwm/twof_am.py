from hackpwm import PWMSystem
from lib.constants import OUT1, OUT2, OUT3
from hackpwm.programs import PWM, PHASE_PULSE

Program = PWMSystem("2F AM", [
    PWM("PACK", pin=OUT2),
    PWM("TESLA 1", pin=OUT1, wait_pin=OUT2),
    PHASE_PULSE("TESLA 2.", pin=OUT3, wait_pin=OUT1)
])
