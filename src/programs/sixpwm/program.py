from lib.constants import OUT1, OUT2, OUT3, OUT4, OUT5, OUT6
from lib.utils import freq_to_str
from piopwm.piopwm import PioPWM
from hackpwm.pwm_system import PWMSystem

from . import store

PWMS = {
    "f1":       {"pin": OUT1, "sm": 0},
    "f2":       {"pin": OUT2, "sm": 1},
    "f3":       {"pin": OUT3, "sm": 2},
    "f4":       {"pin": OUT4, "sm": 4},
    "f5":       {"pin": OUT5, "sm": 5},
    "f6":       {"pin": OUT6, "sm": 6},
}


class Program(PWMSystem):
    max_freq_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    max_duty_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    title = "6 x PWM"
    pwm_exp = {}
    pwms = {}

    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.items = []

        for name in sorted(PWMS.keys()):
            self.items.extend([
                {
                    "text": [[f"{name}:", self.exp_renderer(f"{name}_freq")], lambda event: self.update_period(name, event)],
                    "handle_plusminus": self.exp_updater(f"{name}_freq"),
                    "handle_encoder": lambda event: self.update_period(pwm=name, event=event),
                },
                {
                    "text": [["Duty:", self.exp_renderer(f"{name}_duty")], self.duty_str(name)],
                    "handle_plusminus": self.exp_updater(f"{name}_duty"),
                    "handle_change": lambda event: self.change_duty(pwm=name, event=event),
                }
            ])

        super().__init__()

    def run(self):
        for pwm, settings in PWMS.items():
            self.pwms[pwm] = PioPWM(settings["sm"], pin=settings["pin"])
            self.load_params(pwm)

    def freq_str(self, pwm):
        return lambda: freq_to_str(self.pwms[pwm].get_freq())

    def duty_str(self, pwm):
        return lambda: self.get_duty_str(pwm)

    def get_duty_str(self, pwm):
        pwm_duty_mode = store.get_duty_mode(pwm)
        pwm = self.pwms[pwm]

        if (pwm_duty_mode == store.DUTY_PERCENT):
            return str(pwm.high_percent()) + "%"
        if (pwm_duty_mode == store.DUTY_NS):
            return str(pwm.high_ns()) + "ns"

        return str(pwm.get_high())

    def change_duty(self, pwm, event):
        exp_key = pwm + "_duty"
        if (event == PWMSystem.TAP):
            self.switch_duty_mode(pwm)
        else:
            high = store.get_high(pwm)
            new_duty = self.get_value_by_exp(
                high, self.dir_to_inc(event), self.get_exp(exp_key))
            self.set_duty(pwm, new_duty)

    def switch_duty_mode(self, pwm):
        prev_mode = str(store.get_duty_mode(pwm))
        idx = store.DUTY_MODES.index(prev_mode)
        new_duty_mode = store.DUTY_MODES[(idx + 1) % len(store.DUTY_MODES)]
        store.set_duty_mode(pwm, new_duty_mode)

    def update_period(self, pwm, event):
        exp_key = f"{pwm}_freq"
        self.set_period(pwm, self.get_value_by_exp(
            store.get_period(pwm), self.dir_to_inc(event), exp_key))

    def set_period(self, pwm, period):
        high = store.get_high(pwm)
        if (store.get_duty_mode(pwm) == store.DUTY_PERCENT):
            high = round(store.get_duty_percent(pwm) * period)

        low = period - high
        store.set_params(pwm, (high, low))

        self.load_params(pwm)

    def set_duty(self, pwm, high):
        period = store.get_period(pwm)
        low = period - high
        store.set_low(pwm, low)
        store.set_high(pwm, high)
        store.reset_percent(pwm)

        self.load_params(pwm)

    def load_params(self, pwm):
        params = store.get_params(pwm)
        self.pwms[pwm].set_params(params)
