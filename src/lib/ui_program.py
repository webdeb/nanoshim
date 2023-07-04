from user_inputs import (
    Buttons, SW1, SW2, SW3, SW4, SW5,
    Encoder,
)
from display import display


class UIListProgram:
    title = ""
    display = display
    selected_item = 0
    items = []

    MINUS = 1
    PLUS = 2
    INC = 3
    DEC = 4
    TAP = 5

    def __init__(self):
        self.set_items_text()

    def set_items_text(self):
        self.items_text = list(map(lambda i: i["text"], self.items))

    def start(self):
        # set button handler to this button handler
        Buttons.on(SW1, self.on_sw1)
        Buttons.on(SW2, self.on_sw2)
        Buttons.on(SW3, self.on_sw3)
        Buttons.on(SW4, self.on_sw4)
        Buttons.on(SW5, self.on_sw5)

        Encoder.set_handler(self.encoder_handler)
        self.render()

    def render(self):
        self.display.render_menu(
            self.title, self.items_text, self.selected_item)

    def handle_button(self):
        pass

    def on_sw1(self):
        if ("handle_button" in self.items[self.selected_item]):
            self.items[self.selected_item]["handle_button"]()
        else:
            self.handle_button()

    def on_sw2(self):
        self.selected_item = (self.selected_item - 1) % len(self.items)
        self.render()

    def on_sw3(self):
        self.selected_item = (self.selected_item + 1) % len(self.items)
        self.render()

    def on_sw4(self):
        self.event_handler(UIListProgram.MINUS)

    def on_sw5(self):
        self.event_handler(UIListProgram.PLUS)

    def encoder_handler(self, event):
        if (event == Encoder.INC):
            self.event_handler(UIListProgram.INC)
        elif (event == Encoder.DEC):
            self.event_handler(UIListProgram.DEC)
        elif (event == Encoder.TAP):
            self.event_handler(UIListProgram.TAP)

    def event_handler(self, event):
        if ("handle_change" in self.items[self.selected_item]):
            self.items[self.selected_item]["handle_change"](event)
            self.render()
