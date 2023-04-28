from ui_program import UIListProgram
from simple_json_store import Store
from rotary import Rotary
import machine

"""
Store
"""
CONTRAST_PATH         = "settings.contrast"
MACHINE_FREQ_PATH     = "settings.machine_freq"
INIT_STRUCTURE = {
  "version": 3,
  "settings": {
    "contrast": 200,
    "machine_freq": 125_000_000
  },
}

store = Store(path="data/settings_store.json", inital_data=INIT_STRUCTURE)

class Settings(UIListProgram):
  title = "Settings"

  def __init__(self, on_exit):
    self.items = [
      {
        "text": ["Contrast:", self.get_contrast ],
        "handle_change": self.handle_contrast_change
      },
      {
        "text": ["Freq:", self.get_freq],
        "handle_change": self.handle_freq_change
      }
    ]

    self.handle_button = on_exit
    super().__init__()

  def get_freq(self):
    return str(int(machine.freq()/1_000_000)) + "MHz"

  def handle_freq_change(self, event):
    freq = int(machine.freq() / 1_000_000)
    if (event == Rotary.INC):
      freq += 1
    elif (event == Rotary.DEC):
      freq -= 1

    machine.freq(max(100, min(200, freq)) * 1_000_000)

  def get_contrast(self):
    return str(self.display.get_contrast())

  def handle_contrast_change(self, event):
    contrast = int(self.display.get_contrast())
    if (event == Rotary.INC):
      contrast += 10
    elif (event == Rotary.DEC):
      contrast -= 10
    self.display.set_contrast(contrast)
