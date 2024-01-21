import machine
from lib.ui_program import UIListProgram
from lib.utils import freq_to_str, percent_str
from lib.constants import (OUT1, OUT3, OUT4, OUT5)
from piopwm.piopwm import (
    PioPWM,
    WITH_PIN,
    WITH_PIN_INVERTED_ONCE,
    INVERTED_PIN,
    TRIGGER,
    TRIGGERED_PUSH_PULL,
    clear_programs,
)

from . import store

PULSE = "pulse"
PULSE_INVERTED = "pulse_inverted"
PHASE = "phase"
PUSHPULL = "pushpull"
SYMMETRY = "symmetry"

PWMS = {
    SYMMETRY: {"sm": 0},
    PUSHPULL: {"pin": OUT1, "sm": 1},
    PULSE: {"pin": OUT3, "sm": 4},
    PULSE_INVERTED: {"pin": OUT4, "sm": 5},
    PHASE: {"pin": OUT5, "sm": 6},
}


class Program(UIListProgram):
    max_exp = 4  # 1 -> tick.. 2 -> 10%, 3 -> 50%
    title = "4P"
    autostartable = True
    pwm_exp = {
        "symmetry_freq": 0,
        "symmetry_duty": 0,

        "high_duty": 0,
        "low_duty": 0,

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
                "text": [["PP:", self.exp_str("symmetry_freq")], self.freq_str(SYMMETRY)],
                "handle_change": lambda event: self.change_pp_freq(event),
            },
            {
                "text": [["Sym:", self.exp_str("symmetry_duty")], self.duty_str(SYMMETRY)],
                "handle_change": lambda event: self.change_pp_symmetry(event),
            },
            {
                "text": [["D1:", self.exp_str("high_duty")], self.pp_duty_str("high")],
                "handle_change": lambda event: self.change_pp_duty(event, "high"),
            },
            {
                "text": [["D2:", self.exp_str("low_duty")], self.pp_duty_str("low")],
                "handle_change": lambda event: self.change_pp_duty(event, "low"),
            },

            # """
            # F2
            # """
            {
                "text": [["Puls:", self.exp_str("pulse_freq")], self.freq_str(PULSE)],
                "handle_change": lambda event: self.change_pulse_freq(event),
            },
            {
                "text": [["Duty:", self.exp_str("pulse_duty")], self.duty_str(PULSE)],
                "handle_change": lambda event: self.change_pulse_duty(event),
            },
            {
                "text": [["Count:"], self.pulse_count],
                "handle_change": lambda event: self.change_pulse_count(event),
            },
            {
                "text": [["Phase:", self.exp_str("pulse_phase")], self.phase_str],
                "handle_change": lambda event: self.change_pulse_phase(event),
            },
            {
                "text": ["Period:", self.get_half()],
                "handle_change": lambda event: self.change_half(event)
            },
        ]

        super().__init__()

    def start(self):
        clear_programs()
        print("starting...")
        self.pwms[SYMMETRY] = PioPWM(
            PWMS[SYMMETRY]["sm"],
            mode=TRIGGER,
            pin=None,
        )
        self.pwms[PUSHPULL] = PioPWM(
            PWMS[PUSHPULL]["sm"],
            pin=PWMS[PUSHPULL]["pin"],
            mode=TRIGGERED_PUSH_PULL,
        )
        self.pwms[PULSE] = PioPWM(
            PWMS[PULSE]["sm"],
            pin=PWMS[PULSE]["pin"],
            in_pin=PWMS[PHASE]["pin"],
            mode=WITH_PIN,
        )
        self.pwms[PULSE_INVERTED] = PioPWM(
            PWMS[PULSE_INVERTED]["sm"],
            pin=PWMS[PULSE_INVERTED]["pin"],
            in_pin=PWMS[PULSE]["pin"],
            mode=INVERTED_PIN,
        ).sm.active(1)

        self.set_phase()
        self.load_params(SYMMETRY)
        self.load_params(PUSHPULL)
        self.load_params(PULSE)
        super().start()

    """
    PushPull
    """

    def change_pp_freq(self, event):
        exp_key = "symmetry_freq"
        if (event in [UIListProgram.MINUS, UIListProgram.PLUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            new_period = round(self.get_value_by_exp(
                store.get_period(SYMMETRY),
                self.dir_to_inc(event, True),
                exp_key,
                use_freq=True
            ))

            percent = store.get_duty_percent(SYMMETRY)
            h = round(new_period * percent)
            l = new_period - h
            store.set_params(SYMMETRY, (h, l))

            self.load_params(SYMMETRY)
            self.align_pushpull()

    def change_pp_symmetry(self, event):
        exp_key = "symmetry_duty"
        if (event in [UIListProgram.MINUS, UIListProgram.PLUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            self.update_duty(SYMMETRY, self.dir_to_inc(event), exp_key)

            self.load_params(SYMMETRY)
            self.align_pushpull()

    def align_pushpull(self):
        h, l = store.get_params(SYMMETRY)
        hi_1 = float(store.get_param(PUSHPULL, "high_percent"))
        hi_2 = float(store.get_param(PUSHPULL, "low_percent"))
        store.set_params(PUSHPULL, (round(h * hi_1), round(l * hi_2)))
        self.load_params(PUSHPULL)

    def change_pp_duty(self, event, half):
        exp_key = half + "_duty"

        if (event in [UIListProgram.PLUS, UIListProgram.MINUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            symmetry = int(store.get_param(SYMMETRY, half))
            duty = round(self.get_value_by_exp(store.get_param(
                PUSHPULL, half), self.dir_to_inc(event), exp_key))
            store.set_param(PUSHPULL, half + "_percent", duty / symmetry)
            store.set_param(PUSHPULL, half, duty)
            self.load_params(PUSHPULL)

    def pp_duty_str(self, half):
        return lambda: percent_str(store.get_param(PUSHPULL, half + "_percent"))

    """
    .Push Pull
    """

    def set_phase(self):
        half = min(store.get_half(), 1)
        self.pwms[PHASE] = PioPWM(
            PWMS[PHASE]["sm"],
            pin=PWMS[PHASE]["pin"],
            mode=WITH_PIN_INVERTED_ONCE,
            in_pin=PWMS[PUSHPULL]["pin"] + half
        )
        self.align_phase()

    def change_half(self, event):
        if (event in [UIListProgram.PLUS, UIListProgram.MINUS]):
            store.set_half((store.get_half() + 1) % 2)

        self.set_phase()

    """
    Functions for display strings.
    """

    def exp_str(self, exp_name):
        return lambda: "x" + str(self.get_exp(exp_name) + 1)

    def freq_str(self, pwm):
        return lambda: freq_to_str(self.pwms[pwm].get_freq())

    def duty_str(self, pwm):
        return lambda: self.get_duty_str(pwm)

    def get_duty_str(self, pwm):
        pwm_duty_mode = store.get_duty_mode(pwm)
        pwm = self.pwms[pwm]
        if (pwm_duty_mode == store.DUTY_PERCENT):
            return percent_str(pwm.high_percent())
        return str(pwm.get_high())

    def get_half(self):
        return lambda: str(store.get_half() + 1)

    """
    .
    """

    def phase_str(self):
        return str(store.get_phase(PULSE))

    def pulse_count(self):
        return str(store.get_count(PULSE))

    def change_pulse_phase(self, event):
        exp_key = "pulse_phase"

        if (event in [UIListProgram.MINUS, UIListProgram.PLUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            store.set_phase(
                PULSE,
                max(1, round(self.get_value_by_exp(
                    store.get_phase(PULSE),
                    self.dir_to_inc(event),
                    exp_key
                )))
            )
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

    def change_pulse_freq(self, event):
        self.change_freq(event, PULSE)
        self.align_phase()
        self.load_params(PULSE)

    def change_pulse_duty(self, event):
        self.change_duty(PULSE, event)
        self.load_params(PULSE)

    def change_freq(self, event, pwm):
        exp_key = pwm + "_freq"
        if (event in [UIListProgram.MINUS, UIListProgram.PLUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            self.update_period(pwm, self.dir_to_inc(
                event, invert=True), exp_key)

    def change_duty(self, pwm, event):
        exp_key = pwm + "_duty"

        if (event == UIListProgram.TAP):
            self.switch_duty_mode(pwm)
        elif (event in [UIListProgram.PLUS, UIListProgram.MINUS]):
            self.update_exp(exp_key, event)
        elif (event in [UIListProgram.INC, UIListProgram.DEC]):
            self.update_duty(pwm, self.dir_to_inc(event), exp_key)

    def update_period(self, pwm, inc, exp_key):
        period = store.get_period(pwm)
        new_period = round(self.get_value_by_exp(
            period, inc, exp_key, use_freq=True))
        self.set_period(pwm, new_period)

    def set_period(self, pwm, period):
        high = store.get_high(pwm)
        if (store.get_duty_mode(pwm) == store.DUTY_PERCENT):
            high = round(store.get_duty_percent(pwm) * period)

        low = period - high
        store.set_params(pwm, (high, low))

        # self.load_params(pwm)

    def update_duty(self, pwm, inc, exp_key):
        high = store.get_high(pwm)
        period = store.get_period(pwm)
        new_duty = min(
            period - 5, round(self.get_value_by_exp(high, inc, exp_key)))
        self.set_duty(pwm, new_duty)

    def set_duty(self, pwm, high):
        period = store.get_period(pwm)
        low = period - high
        store.set_low(pwm, low)
        store.set_high(pwm, high)
        store.reset_percent(pwm)

        # self.load_params(pwm)

    def switch_duty_mode(self, pwm):
        prev_mode = str(store.get_duty_mode(pwm))
        idx = store.DUTY_MODES.index(prev_mode)
        new_duty_mode = store.DUTY_MODES[(idx + 1) % len(store.DUTY_MODES)]
        store.set_duty_mode(pwm, new_duty_mode)

    def load_params(self, pwm):
        self.pwms[pwm].set_params(store.get_params(pwm))

    def align_phase(self):
        pulse_period = store.get_period(PULSE)
        pulse_count = store.get_count(PULSE)
        phase = store.get_phase(PULSE)

        phase_high_period = pulse_period * pulse_count
        phase_low_period = phase

        # is inverted
        store.set_high(PHASE, phase_low_period)
        store.set_low(PHASE, phase_high_period)

        self.load_params(PHASE)

    def get_value_by_exp(self, value, inc, exp_key, use_freq=False):
        exp = self.get_exp(exp_key)
        if (use_freq and exp in [1, 2, 3]):
            mf = machine.freq()
            return mf/self.get_value_by_exp(mf/value, inc * -1, exp_key)
        if (exp == 3):
            return value + inc * value * 0.5
        if (exp == 2):
            return value + inc * value * 0.1
        if (exp == 1):
            return value + inc * value * 0.01

        return value + inc * 1

    def update_exp(self, exp_key, event):
        exp = self.get_exp(exp_key)
        if (event == UIListProgram.MINUS):
            self.pwm_exp[exp_key] = (exp - 1) % self.max_exp
        if (event == UIListProgram.PLUS):
            self.pwm_exp[exp_key] = (exp + 1) % self.max_exp

        return self.pwm_exp[exp_key]

    def get_exp(self, exp_key):
        if (exp_key not in self.pwm_exp):
            self.pwm_exp[exp_key] = 0

        return self.pwm_exp[exp_key]

    def dir_to_inc(self, event, invert=False):
        inc = 1
        if (event == UIListProgram.DEC):
            inc = -1

        if (invert):
            return inc * -1

        return inc
