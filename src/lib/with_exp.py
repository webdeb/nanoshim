from lib.ui_program import UIListProgram
import machine


class WithExp():
    exp = {}
    max_exp = 4

    def exp_renderer(self, exp):
        def render():
            return f"x{self.get_exp(exp)}"

        return render

    def exp_updater(self, exp_key):
        return lambda e: self.update_exp(exp_key, e)

    def update_exp(self, exp_key, event):
        exp = self.get_exp(exp_key)
        if (event == UIListProgram.MINUS):
            self.exp[exp_key] = (exp - 1) % self.max_exp
        if (event == UIListProgram.PLUS):
            self.exp[exp_key] = (exp + 1) % self.max_exp

        return self.exp[exp_key]

    def get_exp(self, exp_key):
        if (exp_key not in self.exp):
            self.exp[exp_key] = 0

        return self.exp[exp_key] + 1

    def get_value_by_exp(self, value, inc, exp_key, use_freq=False):
        if (inc not in [-1, 1]):
            inc = self.dir_to_inc(inc)

        exp = self.get_exp(exp_key)
        if (use_freq and exp in [1, 2, 3]):
            mf = machine.freq()
            return mf/self.get_value_by_exp(mf/value, inc * -1, exp_key)
        if (exp == 3):
            return value + inc * max(3, value * 0.5)
        if (exp == 2):
            return value + inc * max(2, value * 0.1)
        if (exp == 1):
            return value + inc * max(1, value * 0.01)

        return value + inc * 1

    def dir_to_inc(self, event, invert=False):
        inc = 0
        if (event == UIListProgram.INC):
            inc = 1
        elif (event == UIListProgram.DEC):
            inc = -1

        if (invert):
            return inc * -1

        return inc
