from hackpwm import PWMSystem
from lib.constants import OUT1, OUT3, OUT4
from hackpwm.programs import PWM, PUSH_PULL, PHASE_PULSE

Program = PWMSystem("4P", [
    PUSH_PULL("PUSH PULL", pin=OUT1),
    PWM("TESLA", pin=OUT3, wait_pin=OUT4),
    PHASE_PULSE("TESLA PACK", pin=OUT4, wait_pin=OUT1, count_pin=OUT3),
])
