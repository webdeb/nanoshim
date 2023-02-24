from ui_program import UIListProgram

class MainMenu(UIListProgram):
  def __init__(self, items):
    self.title = "Menu"
    self.items = [{ "text": k, "handle_button": v } for k, v in items.items()]

    super().__init__()
