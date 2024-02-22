import machine
from lib.ui_program import UIListProgram
from lib.store import Store
from lib.autostart import autostartables, get_autostart_title, set_autostart_title

VERSION = "v1.1.1"

"""
Store
"""
store = Store(path="/store/settings_store.json", inital_data={
    "version": 3,
    "settings": {
        "contrast": 200,
        "machine_freq": 125_000_000,
    },
})
def set_freq(freq): store.set("settings.machine_freq", freq)
def get_freq(): return store.get("settings.machine_freq")


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
                "text": ["Start:", self.render_autostart],
                "handle_encoder": self.change_autostart
            },
            {
                "text": ["Vers:", lambda: VERSION]
            }
        ]

        self.handle_button = on_exit
        super().__init__()

    def get_freq(self):
        return str(int(machine.freq()/1_000_000)) + "MHz"

    """
    
    """

    def render_autostart(self):
        return get_autostart_title()[0:8]

    def change_autostart(self, event):
        if (event not in [UIListProgram.INC, UIListProgram.DEC]):
            return

        list_autostartables = list(autostartables)

        idx = list_autostartables.index(get_autostart_title())
        count = len(list_autostartables)

        print(idx)
        if (event == UIListProgram.INC):
            idx = (idx + 1) % count
            print("inc", idx)
        elif (event == UIListProgram.DEC):
            idx = (idx - 1) % count
            print("dec", idx)

        print(idx)
        set_autostart_title(list_autostartables[idx])

    def get_contrast(self):
        return str(self.display.get_contrast())

    def handle_freq_change(self, event):
        freq = int(machine.freq())
        if (event == UIListProgram.INC):
            freq += 1000000
        elif (event == UIListProgram.DEC):
            freq -= 1000000

        machine.freq(max(100_000_000, min(136_000_000, freq)))

    def handle_contrast_change(self, event):
        contrast = int(self.display.get_contrast())
        if (event == UIListProgram.INC):
            contrast += 10
        elif (event == UIListProgram.DEC):
            contrast -= 10
        self.display.set_contrast(contrast)