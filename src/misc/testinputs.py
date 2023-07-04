from lib.ui_program import UIListProgram
from misc.rgbled import Led


class TestProgram(UIListProgram):
    title = "Input test"
    _counter = 0
    _last_event = "..."

    def __init__(self):
        self.items = [
            {"text": "Press keys"},
            {"text": ["Result: ", lambda: f"{self._counter} {self._last_event}"]}
        ]
        super().__init__()
        self.selected_item = None

    def handle_event(self, event, color=Led.COLORS.white):
        if self._last_event != event:
            self._counter = 0

        self._counter += 1
        self._last_event = event
        Led(color)

        if (self._counter % 2 == 0):
            Led.off()

        self.render()

    def on_sw1(self): self.handle_event("SW1", Led.COLORS.blue)
    def on_sw2(self): self.handle_event("SW2", Led.COLORS.cyan)
    def on_sw3(self): self.handle_event("SW3", Led.COLORS.purple)
    def on_sw4(self): self.handle_event("SW4", Led.COLORS.purple)
    def on_sw5(self): self.handle_event("SW5", Led.COLORS.yellow)

    def encoder_handler(self, event):
        if (event == UIListProgram.DEC):
            self.handle_event("DEC", Led.COLORS.green)
        elif (event == UIListProgram.INC):
            self.handle_event("INC", Led.COLORS.red)
        elif (event == UIListProgram.TAP):
            self.handle_event("TAP", Led.COLORS.white)


async def test_ui():
    testprogram = TestProgram()
    testprogram.active(1)
