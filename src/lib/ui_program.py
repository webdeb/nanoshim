from lib.user_inputs import (
    SW1, SW2, SW3, SW4, SW5,
    INC, DEC, TAP,
    get_inputs,
)

from lib.display import display


class UIListProgram:
    autostartable = False
    title = ""
    display = display
    selected_item = 0
    items = []
    set_exit = None

    MINUS = 1
    PLUS = 2
    INC = 3
    DEC = 4
    TAP = 5

    def __init__(self, on_exit=None):
        if (on_exit):
            self.on_exit = on_exit

    def __call__(self, on_exit=None):
        if (callable(self.set_exit)):
            self.set_exit(on_exit)
        elif (on_exit):
            self.on_exit = on_exit

        return self

    def get_items(self):
        return self.items

    def get_items_text(self):
        items = self.get_items()
        return [i["text"] for i in items]

    def start(self):
        Buttons, Encoder = get_inputs()

        # set button handler to this button handler
        Buttons.on(SW1, self.on_sw1)
        Buttons.on_long(SW1, self.on_long_press)
        Buttons.on(SW2, self.on_sw2)
        Buttons.on(SW3, self.on_sw3)
        Buttons.on(SW4, self.on_sw4)
        Buttons.on(SW5, self.on_sw5)
        Buttons.on_long(SW4, lambda: self.handle_encoder(UIListProgram.TAP))

        Encoder.set_handler(self.encoder_handler)

        self.render()

    def handle_button(self):
        self.on_exit()

    def on_long_press(self): pass

    def render(self):
        self.display.render_menu(
            self.title,
            self.get_items_text(),
            self.selected_item
        )

    def on_sw1(self):
        items = self.get_items()
        if ("handle_button" in items[self.selected_item]):
            items[self.selected_item]["handle_button"]()
        else:
            self.handle_button()

    def on_sw2(self):
        self.selected_item = (self.selected_item - 1) % len(self.get_items())
        self.render()

    def on_sw3(self):
        self.selected_item = (self.selected_item + 1) % len(self.get_items())
        self.render()

    def on_sw4(self):
        self.handle_plusminus(UIListProgram.MINUS)

    def on_sw5(self):
        self.handle_plusminus(UIListProgram.PLUS)

    def encoder_handler(self, event):
        if (event == INC):
            self.handle_encoder(UIListProgram.INC)
        elif (event == DEC):
            self.handle_encoder(UIListProgram.DEC)

    def handle_encoder(self, event):
        items = self.get_items()
        if (f"handle_{event}" in items[self.selected_item]):
            items[self.selected_item][f"handle_{event}"]()
            self.render()
        elif ("handle_encoder" in items[self.selected_item]):
            items[self.selected_item]["handle_encoder"](event)
            self.render()
        else:
            self.event_handler(event)

    def handle_plusminus(self, event):
        items = self.get_items()
        if ("handle_plusminus" in items[self.selected_item]):
            items[self.selected_item]["handle_plusminus"](event)
            self.render()
        else:
            self.event_handler(event)

    def event_handler(self, event):
        items = self.get_items()
        if ("handle_change" in items[self.selected_item]):
            items[self.selected_item]["handle_change"](event)
            self.render()
