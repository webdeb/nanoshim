from machine import Pin
from rp2 import asm_pio, PIO
from lib.ui_program import UIListProgram
from lib.store import Store
from hackpwm.pwm_system import PWMSystem
from lib.constants import OUT1, OUT6
from piopwm import PioPWM, TRIGGER, PROGRAM

from piopwm.pio_programs import HIGH, LOW

from lib.utils import ns_to_str, ticks_to, percent_str

store = Store("/store/sixmix.json", {
    "version": 2,
    "period": 1000,
    "overlap": 220,
    "percent": None
})


def get_period():
    return int(store.get('period'))


def get_overlap():
    return int(store.get('overlap'))


class Program(PWMSystem):
    title = "6 Mix"
    autostartable = True

    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.items = [
            {
                "text": [["P:", self.exp_renderer("period")], self.render_period],
                "handle_plusminus": self.exp_updater("period"),
                "handle_encoder": self.update_period
            },
            {
                "text": [["O:", self.exp_renderer("overlap")], self.render_overlap],
                "handle_plusminus": self.exp_updater("overlap"),
                "handle_encoder": self.update_overlap
            },
        ]

        super().__init__()

    def run(self):
        self.pwm = PioPWM(0, mode=TRIGGER)
        self.program = PioPWM(1, mode=PROGRAM, program=sixmix,
                              sideset_base=Pin(OUT1), set_base=Pin(OUT6))
        self.program.sm.active(1)
        self.load_params()

    def get_get_total_period(self):
        return self.pwm.get_low() + self.pwm.get_high() * 2

    def render_period(self):
        return ns_to_str(ticks_to(self.get_get_total_period()))

    def render_overlap(self):
        percent_duty = store.get("percent")
        if (percent_duty is not None):
            return percent_str(get_overlap() / get_period())

        return ns_to_str(ticks_to(self.pwm.get_high()))

    def update_period(self, event):
        new_value = self.get_value_by_exp(
            get_period(), self.dir_to_inc(event), "period")
        store.set("period", max(HIGH, new_value))
        percent_duty = store.get("percent")

        if (percent_duty is not None):
            store.set("overlap", round(percent_duty * new_value))

        self.load_params()

    def update_overlap(self, event):
        if (event == UIListProgram.TAP):
            if (store.get("percent") is None):
                store.set("percent", self.pwm.get_high() /
                          self.get_get_total_period())
            else:
                store.set("percent", None)
            return

        new_value = self.get_value_by_exp(
            get_overlap(), self.dir_to_inc(event), "overlap")
        store.set("overlap", max(
            LOW, min(int(self.get_get_total_period()/2), new_value)))

        self.load_params()

    def load_params(self):
        self.pwm.set_params((get_overlap(), get_period() - get_overlap()*2))


@asm_pio(set_init=PIO.OUT_LOW, sideset_init=[PIO.OUT_LOW]*5)
def sixmix():
    wait(1, irq, 4)     .side(0b00000)  # <- dis 5
    wait(1, irq, 5)     .side(0b00001)  # <- en 1
    set(pins, 0)        .side(0b00001)  # <- dis 6
    wait(1, irq, 4)     .side(0b00001)  # <- just keep to not use opt
    wait(1, irq, 5)     .side(0b00011)  # <- en 2
    wait(1, irq, 4)     .side(0b00010)  # <- dis 1
    wait(1, irq, 5)     .side(0b00110)  # <- en 3
    wait(1, irq, 4)     .side(0b00100)  # <- dis 2
    wait(1, irq, 5)     .side(0b01100)  # <- en 4
    wait(1, irq, 4)     .side(0b01000)  # <- dis 3
    wait(1, irq, 5)     .side(0b11000)  # <- en 5
    wait(1, irq, 4)     .side(0b10000)  # <- dis 4
    set(pins, 1)        .side(0b10000)  # <- en 6
    wait(1, irq, 5)     .side(0b10000)  # <- just keep to not use opt
