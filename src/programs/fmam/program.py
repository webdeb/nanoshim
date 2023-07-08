from rp2 import PIO
from constants import (
    OUT1,
    OUT2,
    OUT3,
    OUT4
)
from lib.ui_program import (
    UIListProgram,
)

from utils import (
    freq_to_str
)

from piopwm.piopwm import (
    PIOPWM,
    WITH_PIN,
    WITH_PIN_INVERTED,
    clear_programs,
)

import fmam.store as store

F1 = "f1"
F2 = "f2"
F2_PHASE = "f2_phase"
PACKAGE = "package"

PWMS = {
    F1:       {"pin": OUT1, "sm": 0, "with": PACKAGE},
    F2:       {"pin": OUT2, "sm": 1, "with": F2_PHASE},
    F2_PHASE: {"pin": OUT3, "sm": 2, "with": PACKAGE, "inverted": True},
    PACKAGE:  {"pin": OUT4, "sm": 3},
}

class MultiPWMProgram(UIListProgram):
    max_freq_exp = 3  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    max_duty_exp = 3  # 1 -> tick.. 2 -> 10%, 3 -> 50%

    title = "2F AM"
    pwm_exp = {
        "f1_freq": 0,
        "f1_duty": 0,
        "f2_freq": 0,
        "f2_duty": 0,
        "package_freq": 0,
        "package_duty": 0,
    }

    pwms = {}

    def __init__(self, on_exit):
        self.handle_button = on_exit
        self.items = [
            # """
            # F1
            # """
            {
                "text": [["F1:", self.get_exp("f1_freq")], self.freq_str(F1)],
                "handle_change": lambda event: self.change_freq(F1, event),
            },
            {
                "text": [["Duty:", self.get_exp("f1_duty")], self.duty_str(F1)],
                "handle_change": lambda event: self.change_duty(F1, event),
            },

            # """
            # F2
            # """
            {
                "text": [["F2:", self.get_exp("f2_freq")], self.freq_str(F2)],
                "handle_change": lambda event: self.change_freq(F2, event),
            },
            {
                "text": [["Duty:", self.get_exp("f2_duty")], self.duty_str(F2)],
                "handle_change": lambda event: self.change_duty(F2, event),
            },
            {
                "text": [["Phase:"], self.duty_str(F2_PHASE)],
                "handle_change": lambda event: self.change_duty(F2_PHASE, event),
            },

            # """
            # Package
            # """
            {
                "text": [["P:", self.get_exp("package_freq")], self.freq_str(PACKAGE)],
                "handle_change": lambda event: self.change_freq(PACKAGE, event),
            },
            {
                "text": [["Duty:", self.get_exp("package_duty")], self.duty_str(PACKAGE)],
                "handle_change": lambda event: self.change_duty(PACKAGE, event),
            },
        ]

        super().__init__()

    def start(self):
        clear_programs()

        self.pwms[PACKAGE] = PIOPWM(
            PWMS[PACKAGE]["sm"],
            pin=PWMS[PACKAGE]["pin"]
        )
        self.pwms[F2_PHASE] = PIOPWM(
            PWMS[F2_PHASE]["sm"],
            pin=PWMS[F2_PHASE]["pin"],
            mode=WITH_PIN_INVERTED,
            in_pin=PWMS[PACKAGE]["pin"]
        )
        self.pwms[F1] = PIOPWM(
            PWMS[F1]["sm"],
            pin=PWMS[F1]["pin"],
            in_pin=PWMS[PACKAGE]["pin"],
            mode=WITH_PIN,
        )
        self.pwms[F2] = PIOPWM(
            PWMS[F2]["sm"],
            pin=PWMS[F2]["pin"],
            mode=WITH_PIN,
            in_pin=PWMS[F2_PHASE]["pin"]
        )

        self.load_params(PACKAGE)
        # self.load_params(F2_PHASE)
        self.load_params(F1)
        self.load_params(F2)

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

        """
        Special case. Update F2_PHASE
        """
        if (pwm == PACKAGE):
            self.align_phase_to_package()

    def align_phase_to_package(self):
        package_high = store.get_high(PACKAGE)
        # if phase high > package_high
        store.set_high(F2_PHASE, min(
            store.get_high(F2_PHASE), package_high - 10))
        self.set_period(F2_PHASE, package_high)

    def update_duty(self, pwm, inc, factor):
        high = store.get_high(pwm)
        new_duty = self.get_value_by_factor(high, inc, factor)
        self.set_duty(pwm, new_duty)

    def get_value_by_factor(self, value, inc, factor):
        if (factor == 2):
            return round(value + inc * value * 0.5)
        if (factor == 1):
            return round(value + inc * value * 0.1)
        return value + inc * 1
