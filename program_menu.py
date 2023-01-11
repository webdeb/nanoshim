from ui_program import UIListProgram

class MainMenu(UIListProgram):
  def __init__(self, open_pwm, open_settings):
    self.title = "Menu"
    self.items = [
      { "text": "PWM", "handle_button": open_pwm },
      { "text": "Board Settings", "handle_button": open_settings }
    ]

    super().__init__()
