from machine import Pin
from rp2 import asm_pio, PIO
from lib.ui_program import UIListProgram
from lib.store import Stores
from lib.with_exp import WithExp
from lib.constants import OUT1, OUT6
from piopwm import PioPWM, TRIGGER, PROGRAM
from piopwm.pio_programs import HIGH, LOW
from lib.utils import ns_to_str, ticks_to
from lib.autostart import autostart

store = Stores.get_store("/store/sixmix.json", {
    "version": 1,
    "period": 1000,
    "overlap": 220,
})


def get_period():
    return int(store.get('period'))


def get_overlap():
    return int(store.get('overlap'))


class Program(UIListProgram, WithExp):
    title = "6 Mix"
    autostartable = True

    def __init__(self, on_exit):
        self.handle_button = on_exit
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
        self.program = PioPWM(1, mode=PROGRAM, program=sixmix_inverted,
                              sideset_base=Pin(OUT1), set_base=Pin(OUT6))
        self.program.sm.active(1)
        self.load_params()

    def render_period(self):
        return ns_to_str(ticks_to(self.pwm.get_low() + self.pwm.get_high() * 2))

    def render_overlap(self):
        return ns_to_str(ticks_to(self.pwm.get_high()))

    def update_period(self, event):
        new_value = self.get_value_by_exp(
            get_period(), self.dir_to_inc(event), "period")
        store.set("period", max(HIGH, new_value))
        self.load_params()

    def update_overlap(self, event):
        new_value = self.get_value_by_exp(
            get_overlap(), self.dir_to_inc(event), "overlap")
        store.set("overlap", max(
            LOW, min(int(self.pwm.get_period()/2), new_value)))
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

@asm_pio(set_init=PIO.OUT_HIGH, sideset_init=[PIO.OUT_HIGH]*5)
def sixmix_inverted():
    wait(1, irq, 4)     .side(0b11111)  # <- dis 5
    wait(1, irq, 5)     .side(0b11110)  # <- en 1
    set(pins, 1)        .side(0b11110)  # <- dis 6
    wait(1, irq, 4)     .side(0b11110)  # <- just keep to not use opt
    wait(1, irq, 5)     .side(0b11100)  # <- en 2
    wait(1, irq, 4)     .side(0b11101)  # <- dis 1
    wait(1, irq, 5)     .side(0b11001)  # <- en 3
    wait(1, irq, 4)     .side(0b11011)  # <- dis 2
    wait(1, irq, 5)     .side(0b10011)  # <- en 4
    wait(1, irq, 4)     .side(0b10111)  # <- dis 3
    wait(1, irq, 5)     .side(0b00111)  # <- en 5
    wait(1, irq, 4)     .side(0b01111)  # <- dis 4
    set(pins, 0)        .side(0b01111)  # <- en 6
    wait(1, irq, 5)     .side(0b01111)  # <- just keep to not use opt
