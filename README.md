# nanoSHIM aka hackPWM

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
