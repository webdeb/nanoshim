from machine import Pin, I2C
import framebuf
import images
import ssd1306
from store import store, CONTRAST_PATH

# specialchars = {}
# with open('promille.pbm', 'rb') as f:
#     f.readline() # Magic number
#     f.readline() # Creator comment
#     f.readline() # Dimensions
#     data = bytearray(f.read())

# specialchars["‰"] = framebuf.FrameBuffer(data, 9, 8, framebuf.MONO_HLSB)

class Display:
  def __init__(self):
    # Set up the I2C interface
    self.i2c = I2C(id=1, scl=Pin(27), sda=Pin(26), freq=400_000)

    # Set up the display
    self.display = ssd1306.SSD1306_I2C(128, 64, self.i2c)
    self.display.contrast(store.get(CONTRAST_PATH))

  def render_menu(self, title, items, active_idx = 0, exp = None, edit_mode = False):
    menubuf = framebuf.FrameBuffer(bytearray(1024), 128, 64, framebuf.MONO_HLSB)
    menubuf.text(title, 0, 0, 1)
    menubuf.hline(0, 12, 128, 1)
    start = max(0, active_idx - 2)
    items = items[start:]

    for idx, item in enumerate(items, start=0):
      text_y_pos = 8 + 12 * (idx + 1)
      is_active = idx + start == active_idx

      if type(item) is not list:
        item = [item, lambda: ""]

      [text, fun] = item
      text_addition = fun()

      # Fill a white rect around the item, when its active
      if is_active:
        menubuf.fill_rect(0, text_y_pos - 3, 128, 12, 1)

      # Put the static text, which is mostly the label 
      menubuf.text(text, 0, text_y_pos, int(not is_active))

      # add text addition, align to right.
      # we have max 128pixel calculate the text_addition pixel len
      # and substract the result from 128, we should get the position of the text.
      text_addition_len = len(text_addition)
      if (text_addition_len == 0):
        continue

      menubuf.text(text_addition, 128 - text_addition_len*8, text_y_pos, int(not is_active))

      # we start from end of the text_addtion string
      # Ok, this code is a bit tricky, but it does the job.
      # Because we have to display numbers as text, they don't look very pretty.
      # Like 12787800, it difficult to read, so we should add some decimal separator after each 3 digits.
      # We also have the ability to change the number by a factor of 10 with each encoder turn,
      # So the exp is passed along into this function, and if this item is currently selected,
      # we can show the user which factor he/she is currently using.
      # Lets go!

      it = 0
      digits_count = 0
      while (it <= text_addition_len):
        it += 1
        if (text_addition[text_addition_len - it].isdigit()):
          digits_count += 1
          if (digits_count > 1 and (digits_count - 1) % 3 == 0):
            menubuf.hline(128 - (it - 1) * 8 - 1, text_y_pos + 7, 2, int(not is_active))

          if (is_active and exp is not None and digits_count == exp + 1):
            menubuf.hline(128 - (it) * 8 + 2, text_y_pos - 2, 4, int(not is_active))

        elif (digits_count > 0):
          break

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
