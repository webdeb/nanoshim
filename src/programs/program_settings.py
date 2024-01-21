from lib.ui_program import UIListProgram
from lib.simple_json_store import Store
import machine

"""
Store
"""
CONTRAST_PATH = "settings.contrast"
MACHINE_FREQ_PATH = "settings.machine_freq"
INIT_STRUCTURE = {
    "version": 3,
    "settings": {
        "contrast": 200,
        "machine_freq": 125_000_000
    },
}
store = Store(path="/store/settings_store.json", inital_data=INIT_STRUCTURE)
def set_freq(freq): store.set("settings.machine_freq", freq)
def get_freq(): store.get("settings.machine_freq")


class Settings(UIListProgram):
    title = "Settings"

    def __init__(self, on_exit):
        self.items = [
            {
                "text": ["Contrast:", self.get_contrast],
                "handle_change": self.handle_contrast_change
            },
            {
                "text": ["Freq:", self.get_freq],
                "handle_change": self.handle_freq_change
            },
            {
                "text": ["Start: ", self.render_autostart],
                "handle_encoder": self.change_autostart
            }
        ]

        self.handle_button = on_exit
        super().__init__()

    def get_freq(self):
        return str(int(machine.freq()/1000)) + "kHz"

    """
    
    """

    def get_contrast(self):
        return str(self.display.get_contrast())

    def render_autostart(self):
        return "..."

    def change_autostart(self):
        pass

    def handle_freq_change(self, event):
        freq = int(machine.freq())
        if (event == UIListProgram.INC):
            freq += 1000
        elif (event == UIListProgram.DEC):
            freq -= 1000

        machine.freq(max(100_000_000, min(136_000_000, freq)))

    def handle_contrast_change(self, event):
        contrast = int(self.display.get_contrast())
        if (event == UIListProgram.INC):
            contrast += 10
        elif (event == UIListProgram.DEC):
            contrast -= 10
        self.display.set_contrast(contrast)

    def load_settings():
        machine.freq(get_freq())
        display.set_contrast(get_contrast())
