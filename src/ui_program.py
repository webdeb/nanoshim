import user_inputs
from display import display
from rotary import Rotary
import machine

TAP_LEFT = 5
TAP_RIGHT = Rotary.TAP
INC = Rotary.INC
DEC = Rotary.DEC

class UIListProgram:
  rotary_one = user_inputs.ENCODER_LEFT
  rotary_two = user_inputs.ENCODER_RIGHT
  button = user_inputs.BUTTON
  display = display

  handle_button = None
  selected_item = 0

  def __init__(self):
    self.set_items_text()

  def set_items_text(self):
    self.items_text = list(map(lambda i: i["text"], self.items))

  def active(self, active):
    if active:
      # set button handler to this button handler
      self.button.set_handler(self.button_handler)
      self.rotary_one.set_handler(self.rotary_one_handler)
      self.rotary_two.set_handler(self.rotary_two_handler)
      self.render()

  def render(self):
    self.display.render_menu(self.title, self.items_text, self.selected_item)

  def rotary_one_handler(self, event):
    if (event == Rotary.INC):
      self.selected_item = (self.selected_item + 1) % len(self.items)
    elif (event == Rotary.DEC):
      self.selected_item = (self.selected_item - 1) % len(self.items)
    elif (event == Rotary.TAP):
      self.rotary_two_handler(TAP_LEFT)
    else:
      return

    self.render()

  def rotary_two_handler(self, event):
    if ("handle_change" in self.items[self.selected_item]):
      self.items[self.selected_item]["handle_change"](event)
    else:
      return

    self.render()

  def button_handler(self):
    if ("handle_button" in self.items[self.selected_item]):
      self.items[self.selected_item]["handle_button"]()
    elif (hasattr(self, "handle_button")):
      self.handle_button()
