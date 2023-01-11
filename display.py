from machine import Pin, I2C
import framebuf
import images
import ssd1306
from store import store, CONTRAST_PATH

class Display:
  def __init__(self):
    # Set up the I2C interface
    self.i2c = I2C(id=1, scl=Pin(27), sda=Pin(26), freq=400_000)

    # Set up the display
    self.display = ssd1306.SSD1306_I2C(128, 64, self.i2c)
    self.display.contrast(store.get(CONTRAST_PATH))

  def render_menu(self, title, items, active_idx = None, edit_mode = False):
    menubuf = framebuf.FrameBuffer(bytearray(1024), 128, 64, framebuf.MONO_HLSB)
    menubuf.text(title, 0, 0, 1)
    menubuf.hline(0, 12, 128, 1)

    for idx, item in enumerate(items, start=0):
      text_y_pos = 8 + 12 * (idx + 1)

      if type(item) is list:
        [text, fun] = item
        text_addition = fun()
        empty_string_len = int(max(0, (120 - len(text + text_addition) * 8))/8)
        item = text + (" " * empty_string_len) + text_addition
      if idx == active_idx and not edit_mode:
        menubuf.fill_rect(0, text_y_pos - 2, 128, 12, 1)
        menubuf.text(item, 2, text_y_pos, 0)
      elif idx == active_idx and edit_mode:
        menubuf.rect(0, text_y_pos - 2, 128, 12, 1)
        menubuf.text(item, 2, text_y_pos, 1)
      else:
        menubuf.text(item, 2, text_y_pos, 1)

    self.display.blit(menubuf, 0, 0)
    self.display.show()

  def render_image(self, image=images.EYES):
    self.display.fill(image)
    self.display.show()

  def get_contrast(self):
    return store.get(CONTRAST_PATH)

  def set_contrast(self, contrast):
    value = max(0, min(255, contrast))
    store.set(CONTRAST_PATH, value)
    self.display.contrast(value)

display = Display()
