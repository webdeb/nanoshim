import machine
from lib.utils import noop_0, noop_1
from lib.ui_program import UIListProgram


class WithExp():
    exp = 0
    max_exp = 3
    is_freq = False

    def exp_renderer(self):
        return f"x{self.exp + 1}"

    def update_exp(self, event):
        if (event == UIListProgram.MINUS):
            self.exp = max(0, self.exp - 1)
        if (event == UIListProgram.PLUS):
            self.exp = min(self.max_exp, self.exp + 1)

        return self.exp

    def get_value_by_exp(self, value, inc):
        exp = self.exp
        if (exp == 4):
            return value + inc * max(1, value * 0.2)
        if (exp == 3):
            return value + inc * max(1, value * 0.1)
        if (exp == 2):
            return value + inc * max(1, value * 0.01)
        if (exp == 1):
            return value + inc * max(1, value * 0.001)

        return value + inc * 1

    def dir_to_inc(self, event):
        inc = 0
        if (event == UIListProgram.INC):
            inc = 1
        elif (event == UIListProgram.DEC):
            inc = -1

        if (self.is_freq):
            inc = inc * -1

        return inc


def default_render(value):
    return str(value)


class Field(WithExp):
    label = "label"
    max_exp = 4
    with_exp = False
    exp_key = "_"
    is_freq = False

    def __init__(self, label, get_value, on_change, on_mode=noop_1, render_value=default_render, with_exp=False, is_freq=False):
        self.label = label
        self.on_mode = on_mode
        self.with_exp = with_exp
        self.get_value = get_value
        self.on_change = on_change
        self.render_value = render_value
        self.is_freq = is_freq

    def item(self):
        if (self.with_exp):
            text = [[f"{self.label}:", self.exp_renderer], self._render_value]
        else:
            text = [[f"{self.label}:"], self._render_value]

        return {
            "text": text,
            "handle_plusminus": self.handle_plusminus,
            "handle_encoder": self.handle_change,
        }

    def _render_value(self):
        return self.render_value(self.get_value())

    def handle_change(self, e):
        if (e == UIListProgram.TAP):
            return self.on_mode(e)

        value = self.get_value()
        inc = self.dir_to_inc(e)
        self.on_change(self.get_value_by_exp(value, inc))

    def handle_plusminus(self, e):
        if (self.with_exp):
            self.update_exp(e)

    def on_mode(self, e): pass

class LabelField():
    def __init__(self, label, on_mode=noop_0, get_addition=lambda: ""):
        self.label = label
        self.on_mode = on_mode
        self.get_addition = get_addition

    def item(self):
        return {
            "text": [self.label, self.get_addition],
            f"handle_{UIListProgram.TAP}": self.on_mode
        }
