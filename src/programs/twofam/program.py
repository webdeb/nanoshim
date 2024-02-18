from rp2 import PIO

from lib.ui_program import (UIListProgram)
from lib.utils import (
    freq_to_str
)

from piopwm.piopwm import (
    PioPWM,
    WITH_PIN,
    WITH_PIN_INVERTED,
    clear_programs
)
from hackpwm.pwm_system import PWMSystem
from lib.constants import (OUT1, OUT2, OUT3, OUT4)

from . import store

F1 = "f1"
F2 = "f2"
F2_PHASE = "f2_phase"
PACKAGE = "package"

PWMS = {
    PACKAGE:  {"pin": OUT4, "sm": 3},
    F1:       {"pin": OUT1, "sm": 0, "with": PACKAGE},
    F2_PHASE: {"pin": OUT3, "sm": 2, "with": PACKAGE, "inverted": True},
    F2:       {"pin": OUT2, "sm": 1, "with": F2_PHASE},
}


class Program(PWMSystem):
    title = "2F AM"
    pwms = {}

    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.items = [
            # """
            # F1
            # """
            {
                "text": [["F1:", self.exp_renderer("f1_freq")], self.freq_str(F1)],
                "handle_plusminus": self.exp_updater("f1_freq"),
                "handle_change": lambda event: self.change_freq(F1, event),
            },
            {
                "text": [["Duty:", self.exp_renderer("f1_duty")], self.duty_str(F1)],
                "handle_plusminus": self.exp_updater("f1_duty"),
                "handle_change": lambda event: self.change_duty(F1, event),
            },
            # """
            # Package
            # """
            {
                "text": [["P:", self.exp_renderer("package_freq")], self.freq_str(PACKAGE)],
                "handle_plusminus": self.exp_updater("package_freq"),
                "handle_change": lambda event: self.change_freq(PACKAGE, event),
            },
            {
                "text": [["Duty:", self.exp_renderer("package_duty")], self.duty_str(PACKAGE)],
                "handle_plusminus": self.exp_updater("package_duty"),
                "handle_change": lambda event: self.change_duty(PACKAGE, event),
            },

            # """
            # F2
            # """
            {
                "text": [["F2:", self.exp_renderer("f2_freq")], self.freq_str(F2)],
                "handle_plusminus": self.exp_updater("f2_freq"),
                "handle_change": lambda event: self.change_freq(F2, event),
            },
            {
                "text": [["Duty:", self.exp_renderer("f2_duty")], self.duty_str(F2)],
                "handle_plusminus": self.exp_updater("f2_duty"),
                "handle_change": lambda event: self.change_duty(F2, event),
            },
            {
                "text": [["Phase:", self.exp_renderer("f2_phase_duty")], self.duty_str(F2_PHASE)],
                "handle_plusminus": self.exp_updater("f2_phase_duty"),
                "handle_change": lambda event: self.change_duty(F2_PHASE, event),
            },
        ]

        super().__init__()

    def start(self):
        clear_programs()

        self.pwms[PACKAGE] = PioPWM(
            PWMS[PACKAGE]["sm"],
            pin=PWMS[PACKAGE]["pin"]
        )
        self.pwms[F2_PHASE] = PioPWM(
            PWMS[F2_PHASE]["sm"],
            pin=PWMS[F2_PHASE]["pin"],
            mode=WITH_PIN_INVERTED,
            in_pin=PWMS[PACKAGE]["pin"]
        )
        self.pwms[F1] = PioPWM(
            PWMS[F1]["sm"],
            pin=PWMS[F1]["pin"],
            in_pin=PWMS[PACKAGE]["pin"],
            mode=WITH_PIN,
        )
        self.pwms[F2] = PioPWM(
            PWMS[F2]["sm"],
            pin=PWMS[F2]["pin"],
            mode=WITH_PIN,
            in_pin=PWMS[F2_PHASE]["pin"]
        )

        self.load_params(PACKAGE)
        # self.load_params(F2_PHASE)
        self.load_params(F1)
        self.load_params(F2)

        super().start()

    # def get_exp(self, exp_name):
    #     return lambda: "x" + str(self.pwm_exp[exp_name] + 1)

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
        if (event in [UIListProgram.INC, UIListProgram.DEC]):
            period = store.get_period(pwm)
            self.set_period(pwm, self.get_value_by_exp(
                period, self.dir_to_inc(event, invert=True), exp_key))

    def change_duty(self, pwm, event):
        exp_key = pwm + "_duty"
        if (event == UIListProgram.TAP):
            self.switch_duty_mode(pwm)
        else:
            self.update_duty(pwm, self.dir_to_inc(
                event), self.get_exp(exp_key))

    def switch_duty_mode(self, pwm):
        prev_mode = str(store.get_duty_mode(pwm))
        idx = store.DUTY_MODES.index(prev_mode)
        new_duty_mode = store.DUTY_MODES[(idx + 1) % len(store.DUTY_MODES)]
        store.set_duty_mode(pwm, new_duty_mode)

    def set_period(self, pwm, period):
        high = store.get_high(pwm)
        if (store.get_duty_mode(pwm) == store.DUTY_PERCENT):
            high = round(store.get_duty_percent(pwm) * period)

        low = period - high
        store.set_params(pwm, (high, low))

        self.load_params(pwm)

    def update_duty(self, pwm, inc, factor):
        high = store.get_high(pwm)
        new_duty = self.get_value_by_exp(high, inc, factor)
        self.set_duty(pwm, new_duty)

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
