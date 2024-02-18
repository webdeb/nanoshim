from rp2 import PIO, StateMachine
from machine import Pin, freq as machine_freq
from misc.rgbled import Led
import uasyncio as asyncio

from .pio_programs import (
    pwm_program,
    trigger_low_high,
    triggered_push_pull,
    pwm_with_pin_program,
    pwm_with_pin_program_inverted,
    pwm_with_pin_program_inverted_once,
    inverted_pin,
    pushpull_program,
    HIGH,
    LOW,
)

# Modes
NORMAL = 0
WITH_PIN = 1
WITH_PIN_INVERTED = 2
DOUBLE_PIN = 3
TRIGGER = 4
TRIGGERED_PUSH_PULL = 5
WITH_PIN_INVERTED_ONCE = 6
INVERTED_PIN = 7
PROGRAM = 8

MAX_VALUE = (1 << 31) - 1

PIO_PROGRAMS = []


class PioPWM:
    def set_params(self, params):
        high, low = params
        self.high = min(MAX_VALUE, max(1, high - HIGH))
        self.low = min(MAX_VALUE, max(1, low - LOW))
        if (self.sm.active()):
            self.apply_params()

    def active(self, on=1):
        if (on):
            self.apply_params()

        self.sm.active(on)

    def apply_params(self):
        self.sm.put(self.high)
        self.sm.put(self.low)

        # clear isr which forces a jump to "load"
        self.sm.exec("in_(null, 32)")

    def get_params(self):
        return self.get_high(), self.get_low()

    def get_period(self):
        return sum(self.get_params())

    def get_high(self):
        return self.high + HIGH

    def get_low(self):
        return self.low + LOW

    def high_percent(self):
        period = self.get_period()
        return round(self.get_high() / period, 4)

    def high_ns(self):
        return round(1/machine_freq() * self.get_high() / 1e-9)

    def get_freq(self):
        return round(machine_freq()/self.get_period(), 3)

    def __init__(self, id, pin=None, mode=NORMAL, in_pin=None, program=None, **kwargs):
        freq = machine_freq()
        if (mode == PROGRAM):
            self.sm = StateMachine(
                id, prog=program, freq=freq, **kwargs)
            PIO_PROGRAMS.append((id, program))
        elif (mode == NORMAL):
            self.sm = StateMachine(id, prog=pwm_program,
                                   freq=freq, sideset_base=Pin(pin))
            PIO_PROGRAMS.append((id, pwm_program))
        elif (mode == TRIGGER):
            self.sm = StateMachine(id, prog=trigger_low_high, freq=freq)
            PIO_PROGRAMS.append((id, trigger_low_high))
        elif (mode == TRIGGERED_PUSH_PULL):
            self.sm = StateMachine(
                id, prog=triggered_push_pull, sideset_base=Pin(pin), freq=freq)
            PIO_PROGRAMS.append((id, triggered_push_pull))
        elif (mode == WITH_PIN):
            if (in_pin == None):
                raise Exception("Define in_pin")
            self.sm = StateMachine(id, prog=pwm_with_pin_program, sideset_base=Pin(
                pin), in_base=Pin(in_pin), freq=freq)
            PIO_PROGRAMS.append((id, pwm_with_pin_program))
        elif (mode == INVERTED_PIN):
            if (in_pin == None):
                raise Exception("Define in_pin")
            self.sm = StateMachine(id, prog=inverted_pin, sideset_base=Pin(
                pin), in_base=Pin(in_pin), freq=freq)
            PIO_PROGRAMS.append((id, inverted_pin))
        elif (mode == WITH_PIN_INVERTED):
            if (in_pin == None):
                raise Exception("Define in_pin")
            self.sm = StateMachine(id, prog=pwm_with_pin_program_inverted, sideset_base=Pin(
                pin), in_base=Pin(in_pin), freq=freq)
            PIO_PROGRAMS.append((id, pwm_with_pin_program_inverted))
        elif (mode == WITH_PIN_INVERTED_ONCE):
            if (in_pin == None):
                raise Exception("Define in_pin")
            self.sm = StateMachine(id, prog=pwm_with_pin_program_inverted_once, sideset_base=Pin(
                pin), in_base=Pin(in_pin), freq=freq)
            PIO_PROGRAMS.append((id, pwm_with_pin_program_inverted_once))
        elif (mode == DOUBLE_PIN):
            pin_1 = pin
            self.sm = StateMachine(
                id, prog=pushpull_program, sideset_base=Pin(pin_1), freq=freq)
            PIO_PROGRAMS.append((id, pushpull_program))
        else:
            raise Exception("Define Mode")


def clear_programs():
    while PIO_PROGRAMS:
        pio = 0
        (sid, program) = PIO_PROGRAMS.pop()
        if (sid > 3):
            pio = 1

        PIO(pio).state_machine(sid % 4).active(0)
        PIO(pio).remove_program(program)

# async def start_pwm_status_led():
#     while (True):
#         if (len(PIO_PROGRAMS) > 0):
#             Led(Led.COLORS.red)
#         else:
#             Led.normal()

#         await asyncio.sleep_ms(100)
