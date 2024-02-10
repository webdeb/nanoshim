# HackPWM

<img src="https://github.com/webdeb/nanoshim/assets/14992140/7e6a05b5-28bf-47a2-9062-699df4bb3fd5" width="600px" />


This is a full rp2040 (aka pico) micropython project which implements some cool stuff and controls multiple PWM outputs. It can be extended to use all of the 8 PWM slices, which are provided by the pico. Actually it can be extended much more than that and I had to force me to stop implementing more fancy stuff.

_I build this project with the aim to learn python, and the pico. To see what the rp2040 offers, and how to build things with it. So I played around._

## Implemented Features

- One main **Button** as input (mostly used as Exit-Button)
- Two **Rotary Encoder** inputs
- **ssd1306 128x64** to display all the cool stuff, and as an example an image of Nikolas Tesla eyes with a framebuffer
- A simple rendering engine to render a Menu with two-part text items (static: <-> dynamic) like (Contrast:&nbsp;&nbsp;&nbsp;&nbsp;128) and active menu items.
- Usage of pythons OO-Model to simplify the creation of similar UIs (like Menus, with items, which are boring to code..)
- **Storage** settings are stored on the built-in flash memory in a simple **json** file.
- Simplified version of **JSONPath** to save stuff in a deep data structure without typed getters and setters (what can go wrong..)
- Usage of `uctypes` to access rp2040 registers directly from micropython
- Usage of micropythons port of the **PWM** driver.
- Usage of the PWM-to-PWM feature, to control one signal by another.
- Thats it. you can read.

Use it, extend it and if you are not too lazy to click a button, star this repo.

### Detailed information

look into the main.py file, and follow the code into the rebbit whole.

### Run it

don't, but if you do, do it.

### Thanks

Thanks to all, who helped me during my first baby steps into python, micropython, pico and the world of microcontrollers. Maybe thats not my last project. Star this repo. (But don't double-click)

### UIListProgram

The `UIListProgram` class simplifies (ui_program.py)

The simples usage of the `UIListProgram` is the **MainMenu** (`program_menu.py`)

```py
from ui_program import UIListProgram

class MainMenu(UIListProgram):
  def __init__(self, open_pwm, open_settings):
    # Title for the display
    self.title = "Menu"
    # Items to render and which can be selected with the left encoder
    self.items = [
      # Text of the item and handler for the main button.
      { "text": "PWM", "handle_button": open_pwm },
      { "text": "Board Settings", "handle_button": open_settings }
    ]

    super().__init__()

```

The following is a an extended example of how to use the `UIListProgram` class. In this example the `Settings` class is created. `program_settings.py`
This is using dynamic list items, for left<->right text.
It also uses the second encoder to change the actual setting.

```py
from ui_program import UIListProgram
from rotary import Rotary
import machine

class Settings(UIListProgram):
  title = "Settings"

  def __init__(self, on_exit):
    self.items = [
      {
        # Will render to "Contrast:     255" (see display.py#render_menu)
        "text": ["Contrast:", self.get_contrast ],
        # This handler will be called when the user has selected this item
        # with left encoder and is rotating the right encoder
        "handle_change": self.handle_contrast_change
      },
      {
        "text": ["Freq:", self.get_freq],
        "handle_change": self.handle_freq_change
      }
    ]

    # Also implemented in the UIListProgram, here we just assign the handler.
    self.handle_button = on_exit

    # Also implemented in the UIListProgram, here we just assign the handler.
    super().__init__()

  # This is the actual class specific logic
  def get_freq(self):
    return str(int(machine.freq()/1_000_000)) + "MHz"

  def handle_freq_change(self, event):
    freq = int(machine.freq() / 1_000_000)
    if (event == Rotary.INC):
      freq += 1
    elif (event == Rotary.DEC):
      freq -= 1

    # limit the boundary to set the freq..
    machine.freq(max(100, min(130, freq)) * 1_000_000)

  def get_contrast(self):
    return str(self.display.get_contrast())

  def handle_contrast_change(self, event):
    contrast = self.display.get_contrast()
    if (event == Rotary.INC):
      contrast += 10
    elif (event == Rotary.DEC):
      contrast -= 10
    self.display.set_contrast(contrast)
```
