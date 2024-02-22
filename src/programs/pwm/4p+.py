from hackpwm import PWMSystem
from hackpwm.pins import OUT1, OUT2, OUT3, OUT4, OUT5, OUT6
from hackpwm.programs import PWM

Program = PWMSystem("6xPWM", [
    PWM("F1", pin=OUT1),
    PWM("F2", pin=OUT2),
    PWM("F3", pin=OUT3),
    PWM("F4", pin=OUT4),
    PWM("F5", pin=OUT5),
    PWM("F6", pin=OUT6),
])
