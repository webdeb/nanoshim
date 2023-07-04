from lib.simple_json_store import Store
from machine import Pin, PWM as MPWM
import math
import multipwmstore as store
from pwm_register import (
    PWM_REGISTERS,
    get_pins_channel,
    get_pins_slice
)

# 6, 7, 8, 9, 10, 11, 13, 14, 15
pin_f1 = 9
pin_f2 = 14
pin_package = 13

F1 = "F1"
F2 = "F2"
PACKAGE = "PACKAGE"


class PWM(MPWM):
    def __init__(self, pin_number):
        self.slice = get_pins_slice(pin_number)
        self.channel = get_pins_channel(pin_number)
        self.register = PWM_REGISTERS[self.slice]
        self.compare = self.register.COMPARE.A if self.channel == "A" else self.register.COMPARE.B
        super().__init__(Pin(pin_number))

    def step_freq(self, inc, factor):
        wrap = int(self.register.TOP.WRAP)
        if (inc < 0):
            wrap = max(math.floor(wrap - wrap * 0.5), wrap * inc * factor)
        else:
            wrap = wrap * inc * factor

        self.register.TOP.WRAP = wrap

    def step_duty(self, inc, factor):
        compare = int(self.register.TOP.WRAP)
        if (inc < 0):
            wrap = max(math.floor(wrap - wrap * 0.5), wrap * inc * factor)
        else:
            wrap = wrap * inc * factor

        self.register.TOP.WRAP = wrap


class MULTIPWM:
    pwm = {}

    def __init__(self):
        self.pwm[F1] = PWM(pin_f1)
        self.pwm[F2] = PWM(pin_f2)
        self.pwm[PACKAGE] = PWM(pin_package)

    def get_duty_str(self, pwm):
        return str(round(self.pwm[pwm].duty_u16() / 65535, 3) * 100) + "%"

    def get_duty_ns(self, pwm):
        return str(self.pwm[pwm].duty_ns())

    def get_freq(self, pwm):
        return round(self.pwm[pwm].freq(), 2)

    # def set_period(self, pwm, period):
    #   # If duty_mode Percent.. recalculate
    #   current_period = store.get_period(pwm)
    #   if (store.get_duty_mode(pwm) is store.DUTY_PERCENT):
    #     duty = round(store.get_duty(pwm) / current_period * period)
    #     store.set_duty(pwm, duty)

    #   store.set_period(pwm, period)
    #   self.update(pwm)

    # def set_duty(self, pwm, value = 0):
    #   value = value or store.get_duty(pwm)
    #   period = store.get_period(pwm)
    #   value = max(value, -1)
    #   value = min(value, period - 2)
    #   store.set_duty(pwm, value)

    #   self.update(pwm)

    # def update(self, pwm):
    #   period = store.get_period(pwm)
    #   duty = store.get_duty(pwm)

    #   x = period - duty
    #   sm = self.pwm[pwm]
    #   # sm.active(0)
    #   sm.put(duty)
    #   sm.exec("pull()")
    #   sm.exec("mov(isr, osr)")
    #   sm.put(x)
    #   sm.exec("pull()")
    #   sm.active(1)

    def update_period(self, pwm, inc, factor):
        period = store.get_period(pwm)
        if (inc < 0 and factor > period):
            # perform update, but use the period as factor
            return self.update_period(pwm, inc, period)

        new_period = period + (10**factor) * inc
        if (pwm == PULSE):
            package_period = store.get_period(PACKAGE)
            new_period = min(package_period, new_period)
        if (pwm == PACKAGE):
            bigpack_period = store.get_period(BIGPACK)
            new_period = min(bigpack_period, new_period)

        new_period = max(1, new_period)
        self.set_period(pwm, new_period)

    def update_duty(self, pwm, inc, factor):
        duty = store.get_duty(pwm)
        new_duty = duty + (10**factor) * inc
        if (pwm == PULSE):
            package_duty = store.get_duty(PACKAGE)
            new_duty = min(package_duty, new_duty)
        if (pwm == PACKAGE):
            bigpack_duty = store.get_duty(BIGPACK)
            new_duty = min(bigpack_duty, new_duty)

        new_duty = max(1, new_duty)
        self.set_duty(pwm, new_duty)


INIT_STRUCTURE = {
    "version": 6,
    "settings": {
        "contrast": 200,
        "machine_freq": 125_000_000
    },
    "system": {
        "pulse": {
            "period": 31,
            "duty": 15,
            "duty_mode": DUTY_CYCLES,
            "period_mode": FREQ_CYCLES,
        },
        "package": {
            "period": 300,
            "duty": 3,
            "duty_mode": DUTY_CYCLES,
            "period_mode": FREQ_CYCLES,
        },
        "bigpack": {
            "period": 1,
            "duty": 1,
            "duty_mode": DUTY_CYCLES,
            "period_mode": FREQ_CYCLES,
        }
    }
}
DEFAULT_PATH = "data/main_store.json"
store = Store(path=DEFAULT_PATH, inital_data=INIT_STRUCTURE)


def set_period(pwm, value):
    store.set(f"system.{pwm}.period", value)


def get_period(pwm):
    return int(store.get(f"system.{pwm}.period"))


def set_duty(pwm, value):
    store.set(f"system.{pwm}.duty", value)


def get_duty(pwm):
    return int(store.get(f"system.{pwm}.duty"))


def set_duty_mode(pwm, mode):
    store.set(f"system.{pwm}.duty_mode", mode)


def get_duty_mode(pwm):
    return store.get(f"system.{pwm}.duty_mode")
