from math import sqrt
from lib.ui_program import UIListProgram
from lib.with_exp import WithExp
from lib.units import LRenderer, FRenderer, CRenderer

C = "C"
L = "L"
F = "F"
MODES = [C, L, F]
PI = 3.14159265359


class Program(UIListProgram, WithExp):
    title = "LC Calculator"
    mode = C

    def get_mode_field(self):
        return {
            "text": [["Mode:", self.get_mode], self.get_mode_result],
            "handle_change": self.handle_mode_change
        }

    def get_inductance_field(self):
        return {
            "text": [["L:", self.exp_renderer("inductance")], self.get_inductance],
            "handle_plusminus": lambda e: self.update_exp("inductance", e),
            "handle_change": self.handle_inductance_change
        }

    def get_capacitance_field(self):
        return {
            "text": [["C:", self.exp_renderer("capacitance")], self.get_capacitance],
            "handle_plusminus": lambda e: self.update_exp("capacitance", e),
            "handle_change": self.handle_capacitance_change
        }

    def get_frequency_field(self):
        return {
            "text": [["F:", self.exp_renderer("frequency")], self.get_frequency],
            "handle_plusminus": lambda e: self.update_exp("frequency", e),
            "handle_change": self.handle_frequency_change
        }

    def get_items(self):
        inputs = []
        if (self.mode == "C"):
            inputs = [self.get_inductance_field(), self.get_frequency_field()]
        elif (self.mode == "F"):
            inputs = [self.get_capacitance_field(), self.get_inductance_field()]
        elif (self.mode == "L"):
            inputs = [self.get_capacitance_field(), self.get_frequency_field()]

        return [self.get_mode_field()] + inputs

    def get_mode(self):
        return self.mode

    def handle_mode_change(self, event):
        if (event == UIListProgram.DEC):
            self.mode = MODES[(MODES.index(self.mode) - 1) % len(MODES)]
        if (event == UIListProgram.INC):
            self.mode = MODES[(MODES.index(self.mode) + 1) % len(MODES)]
        self.calculate()

    def get_mode_result(self):
        if (self.mode == "C"):
            return self.get_capacitance()
        if (self.mode == "L"):
            return self.get_inductance()
        if (self.mode == "F"):
            return self.get_frequency()

    inductance = 0

    def get_inductance(self):
        return LRenderer.render(self.inductance)

    def handle_inductance_change(self, event):
        if (event in [UIListProgram.DEC, UIListProgram.INC]):
            self.inductance = round(self.get_value_by_exp(
                self.inductance * 1_000_000, event, "inductance")) / 1_000_000
            self.calculate()

    """
    Capacitance field
    """
    capacitance = 0

    def get_capacitance(self):
        return CRenderer.render(self.capacitance)

    def handle_capacitance_change(self, event):
        if (event in [UIListProgram.DEC, UIListProgram.INC]):
            self.capacitance = round(self.get_value_by_exp(
                self.capacitance * 1_000_000_000_000, event, "capacitance")) / 1_000_000_000_000
            self.calculate()

    frequency = 0

    def get_frequency(self):
        return FRenderer.render(self.frequency)

    def handle_frequency_change(self, event):
        if (event in [UIListProgram.DEC, UIListProgram.INC]):
            self.frequency = self.get_value_by_exp(
                self.frequency, event, "frequency")
            self.calculate()

    def __init__(self, on_exit):
        self.handle_button = on_exit
        self.items = self.get_items()
        super().__init__()

    def calculate(self):
        if (self.mode == "C" and self.frequency > 0 and self.inductance > 0):
            self.capacitance = (
                1/(4*pow(PI, 2)*pow(self.frequency, 2) * self.inductance)
            )

        elif (self.mode == "L" and self.frequency > 0 and self.capacitance > 0):
            self.inductance = (
                1/(4*pow(PI, 2)*pow(self.frequency, 2) * self.capacitance)
            )

        elif (self.mode == "F" and self.frequency > 0 and self.inductance > 0):
            self.frequency = (
                1/(2*PI*sqrt(self.capacitance * self.inductance))
            )
