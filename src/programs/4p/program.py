from rp2 import PIO
from lib.ui_program import UIListProgram
from utils import freq_to_str
from constants import (OUT1, OUT2, OUT3, OUT4)
from piopwm.piopwm import (
    PIOPWM,
    WITH_PIN,
    WITH_PIN_INVERTED,
    DOUBLE_PIN,
    clear_programs,
)

from . import store

PULSE = "pulse"
PHASE = "phase"
PUSHPULL_ONE = "pushpull_1"
PUSHPULL_TWO = "pushpull_2"
PWMS = {
    PUSHPULL_ONE: {"pin": OUT1, "sm": 0},
    PUSHPULL_TWO: {"pin": OUT2, "sm": 0},
    PULSE: {"pin": OUT3, "sm": 1},
    PHASE: {"pin": OUT4, "sm": 4},
}


class Program(UIListProgram):
    max_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    title = "4P Program"
    pwm_exp = {
        "pushpull_freq": 0,
        "pushpull_duty": 0,

        "pulse_freq": 0,
        "pulse_duty": 0,
        "pulse_phase": 0,

        "phase_freq": 0,
        "phase_duty": 0,
    }

    pwms = {}

    def __init__(self, on_exit):
        self.handle_button = on_exit
        self.items = [
            # """
            # F1
            # """
            {
                "text": [["PP:", self.get_exp("pushpull_freq")], self.pp_freq_str(PUSHPULL)],
                "handle_change": lambda event: self.change_pp_freq(event),
            },
            {
                "text": [["Duty:", self.get_exp("pushpull_duty")], self.duty_str(PUSHPULL)],
                "handle_change": lambda event: self.change_pp_duty(event),
            },
            {
                "text": [["Duty 2:", self.get_exp("pushpull_duty_2")], self.duty_str(PUSHPULL)],
                "handle_change": lambda event: self.change_pp_duty_two(event),
            },

            # """
            # F2
            # """
            {
                "text": [["Puls:", self.get_exp("pulse_freq")], self.freq_str(PULSE)],
                "handle_change": lambda event: self.change_freq(PULSE, event),
            },
            {
                "text": [["Duty:", self.get_exp("pulse_duty")], self.duty_str(PULSE)],
                "handle_change": lambda event: self.change_duty(PULSE, event),
            },

            {
                "text": [["Count:"], self.pulse_count],
                "handle_change": lambda event: self.change_pulse_count(event),
            },
            {
                "text": [["Phase:", self.get_exp("pulse_phase")], self.pulse_phase],
                "handle_change": lambda event: self.change_pulse_phase(event),
            },
            {
                "text": ["Period:", self.get_half()],
                "handle_change": lambda event: self.change_half(event)
            },
        ]

        super().__init__()

    """
    Changes to PushPull
    """

    def change_pp_freq(self, event):
        pass

    def change_pp_duty(self, event):
        pass

    def change_pp_duty_two(self, event):
        pass

    def start(self):
        clear_programs()
        print("starting...")

        self.pwms[PUSHPULL_ONE] = PIOPWM(
            PWMS[PUSHPULL_ONE]["sm"],
            pin=PWMS[PUSHPULL_ONE]["pin"],
            mode=WITH_ZERO_PIN_INVERTED,
        )
        self.pwms[PUSHPULL_TWO] = PIOPWM(
            PWMS[PUSHPULL_TWO]["sm"],
            pin=PWMS[PUSHPULL_TWO]["pin"],
            mode=WITH_PIN_INVERTED,
        )

        self.set_phase()

        self.pwms[PULSE] = PIOPWM(
            PWMS[PULSE]["sm"],
            pin=PWMS[PULSE]["pin"],
            in_pin=PWMS[PHASE]["pin"],
            mode=WITH_PIN,
        )

        self.load_params(PUSHPULL)
        self.load_params(PULSE)
        super().start()

    def set_phase(self):
        half = min(store.get_half(), 1)
        self.pwms[PHASE] = PIOPWM(
            PWMS[PHASE]["sm"],
            pin=PWMS[PHASE]["pin"],
            mode=WITH_PIN_INVERTED,
            in_pin=PWMS[PUSHPULL]["pin"] + half
        )
        self.align_phase()

    def get_half(self):
        return lambda: str(store.get_half() + 1)

    def change_half(self, event):
        if (event == UIListProgram.PLUS):
            store.set_half((store.get_half() + 1) % 2)

        self.set_phase()

    def pp_freq_str(self, pwm):
        return lambda: freq_to_str(self.pwms[pwm].get_freq() / 2)

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

    def pulse_phase(self):
        return str(store.get_phase(PULSE))

    def pulse_count(self):
        return str(store.get_count(PULSE))

    def change_pulse_phase(self, event):
        exp_key = "pulse_phase"
        exp = self.pwm_exp[exp_key]
        phase = int(self.pulse_phase())

        if (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_exp
        if (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_exp
        if (event == UIListProgram.INC):
            store.set_phase(PULSE, self.get_value_by_factor(phase, 1, exp))
        elif (event == UIListProgram.DEC):
            store.set_phase(PULSE, max(
                self.get_value_by_factor(phase, -1, exp), 1))

        self.align_phase()

    def change_pulse_count(self, event):
        count = store.get_count(PULSE)
        if (event == UIListProgram.INC):
            store.set_count(PULSE, count + 1)
        elif (event == UIListProgram.DEC):
            store.set_count(PULSE, max(count - 1, 1))

        self.align_phase()

    def render(self):
        items_text = list(map(lambda i: i["text"], self.items))
        self.display.render_menu(self.title, items_text, self.selected_item)

    def change_freq(self, pwm, event):
        exp_key = pwm + "_freq"
        if (exp_key not in self.pwm_exp):
            self.pwm_exp[exp_key] = 0

        exp = self.pwm_exp[exp_key]

        if (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_exp
        if (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_exp
        elif (event == UIListProgram.INC):
            self.update_period(pwm, -1, exp)
        elif (event == UIListProgram.DEC):
            self.update_period(pwm, 1, exp)

    def change_duty(self, pwm, event):
        exp_key = pwm + "_duty"
        if (exp_key not in self.pwm_exp):
            self.pwm_exp[exp_key] = 0

        exp = self.pwm_exp[exp_key]

        if (event == UIListProgram.TAP):
            self.switch_duty_mode(pwm)
        elif (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_exp
        elif (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_exp
        elif (event == UIListProgram.INC):
            self.update_duty(pwm, 1, exp)
        elif (event == UIListProgram.DEC):
            self.update_duty(pwm, -1, exp)

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

    def update_duty(self, pwm, inc, factor):
        high = store.get_high(pwm)
        new_duty = self.get_value_by_factor(high, inc, factor)
        self.set_duty(pwm, new_duty)

    def set_duty(self, pwm, high):
        period = store.get_period(pwm)
        low = period - high
        store.set_low(pwm, low)
        store.set_high(pwm, high)
        store.reset_percent(pwm)

        self.load_params(pwm)

    def switch_duty_mode(self, pwm):
        prev_mode = str(store.get_duty_mode(pwm))
        idx = store.DUTY_MODES.index(prev_mode)
        new_duty_mode = store.DUTY_MODES[(idx + 1) % len(store.DUTY_MODES)]
        store.set_duty_mode(pwm, new_duty_mode)

    def load_params(self, pwm):
        params = store.get_params(pwm)
        self.pwms[pwm].set_params(params)
        if (pwm != PHASE):
            self.align_phase()

    def align_phase(self):
        pulse_period = store.get_period(PULSE)
        pulse_count = store.get_count(PULSE)
        pushpull_half_high = store.get_high(PUSHPULL)

        phase = store.get_phase(PULSE)

        phase_high_period = pulse_period * pulse_count
        phase_low_period = phase + pushpull_half_high

        # is inverted
        store.set_high(PHASE, phase_low_period)
        store.set_low(PHASE, phase_high_period)

        self.load_params(PHASE)

    def get_value_by_factor(self, value, inc, factor):
        if (factor == 3):
            return round(value + inc * value * 0.5)
        if (factor == 2):
            return round(value + inc * value * 0.1)
        if (factor == 1):
            return round(value + inc * value * 0.01)

        return value + inc * 1

    def on(self, events, cb, param):
        def handler(event):
            if (event in events):
                cb(event, param)
        return handler
