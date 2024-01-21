from rp2 import PIO
from lib.constants import OUT1, OUT2, OUT3, OUT4, OUT5, OUT6
from lib.ui_program import UIListProgram
from lib.utils import freq_to_str
from piopwm.piopwm import PioPWM, clear_programs

from . import store

F1 = "f1"
F2 = "f2"
F3 = "f3"
F4 = "f4"
F5 = "f5"
F6 = "f6"

PWMS = {
    F1:       {"pin": OUT1, "sm": 0},
    F2:       {"pin": OUT2, "sm": 1},
    F3:       {"pin": OUT3, "sm": 2},

    F4:       {"pin": OUT4, "sm": 4},
    F5:       {"pin": OUT5, "sm": 5},
    F6:       {"pin": OUT6, "sm": 6},
}


class Program(UIListProgram):
    max_freq_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    max_duty_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    title = "6 x PWM"
    pwm_exp = {}
    pwms = {}

    def __init__(self, on_exit):
        self.handle_button = on_exit
        self.items = []

        for name in sorted(PWMS.keys()):
            self.items.append({
                "text": [[f"{name}:", self.get_exp(f"{name}_freq")], self.freq_str(name)],
                "handle_change": lambda event, name=name: self.change_freq(pwm=name, event=event),
            })
            self.pwm_exp[f"{name}_freq"] = 0

            self.items.append({
                "text": [["Duty:", self.get_exp(f"{name}_duty")], self.duty_str(name)],
                "handle_change": lambda event, name=name: self.change_duty(pwm=name, event=event),
            })
            self.pwm_exp[f"{name}_duty"] = 0

        super().__init__()

    def start(self):
        clear_programs()

        for pwm, settings in PWMS.items():
            print("create PWM ", pwm, settings)
            self.pwms[pwm] = PioPWM(settings["sm"], pin=settings["pin"])
            self.load_params(pwm)

        print("started 6 pwms")
        super().start()

    def get_exp(self, exp_name):
        return lambda: "x" + str(self.pwm_exp[exp_name] + 1)

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

    def render(self):
        items_text = list(map(lambda i: i["text"], self.items))
        self.display.render_menu(self.title, items_text, self.selected_item)

    def change_freq(self, pwm, event):
        exp_key = pwm + "_freq"
        if (exp_key not in self.pwm_exp):
            self.pwm_exp[exp_key] = 0

        exp = self.pwm_exp[exp_key]

        if (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_freq_exp
        if (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_freq_exp
        elif (event == UIListProgram.INC):
            self.update_period(pwm, -1, exp)
        elif (event == UIListProgram.DEC):
            self.update_period(pwm, 1, exp)

        self.render()

    def change_duty(self, pwm, event):
        exp_key = pwm + "_duty"
        if (exp_key not in self.pwm_exp):
            self.pwm_exp[exp_key] = 0

        exp = self.pwm_exp[exp_key]

        if (event == UIListProgram.TAP):
            self.switch_duty_mode(pwm)
        elif (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_duty_exp
        elif (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_duty_exp
        elif (event == UIListProgram.INC):
            self.update_duty(pwm, 1, exp)
        elif (event == UIListProgram.DEC):
            self.update_duty(pwm, -1, exp)

        self.render()

    def switch_duty_mode(self, pwm):
        prev_mode = str(store.get_duty_mode(pwm))
        idx = store.DUTY_MODES.index(prev_mode)
        new_duty_mode = store.DUTY_MODES[(idx + 1) % len(store.DUTY_MODES)]
        store.set_duty_mode(pwm, new_duty_mode)

    def update_period(self, pwm, inc, factor):
        period = store.get_period(pwm)
        new_period = self.get_value_by_factor(period, inc, factor)
        self.set_period(pwm, new_period)

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

    def update_duty(self, pwm, inc, factor):
        high = store.get_high(pwm)
        new_duty = self.get_value_by_factor(high, inc, factor)
        self.set_duty(pwm, new_duty)

    def get_value_by_factor(self, value, inc, factor):
        if (factor == 3):
            return round(value + inc * value * 0.5)
        if (factor == 2):
            return round(value + inc * value * 0.1)
        if (factor == 1):
            return round(value + inc * value * 0.01)
        return value + inc * 1
