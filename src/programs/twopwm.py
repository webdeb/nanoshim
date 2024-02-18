from hackpwm import PWMSystem
from hackpwm.pins import OUT1, OUT3, OUT5, OUT4
from hackpwm.programs import (
    PWM,
    TRIGGER_45_WITH_PIN,
    PUSH_PULL_45,
    PWM_WITH_PIN,
    COUNT_AFTER_4,
    COUNT_AFTER_5,
)


Program = PWMSystem("FULL", [
    PWM("Main", pin=OUT5),
    TRIGGER_45_WITH_PIN("PUSH PULL", in_pin=OUT5),
    PUSH_PULL_45(pin=OUT1),  # + OUT2
    PWM_WITH_PIN("PULSE", pin=OUT3, in_pin=OUT4),
    COUNT_AFTER_4("Phase 1 & Count", pin=OUT4, in_pin=OUT3),
    COUNT_AFTER_5("Phase 2 & Count", pin=OUT4, in_pin=OUT3)
])
