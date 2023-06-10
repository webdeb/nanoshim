import uasyncio as asyncio
from lib.ui_program import (
    UIListProgram,
    Encoder,
)


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

    def handle_event(self, event):
        if self._last_event != event:
            self._counter = 0

        self._counter += 1
        self._last_event = event

        self.render()

    def on_sw1(self): self.handle_event("SW1")
    def on_sw2(self): self.handle_event("SW2")
    def on_sw3(self): self.handle_event("SW3")
    def on_sw4(self): self.handle_event("SW4")
    def on_sw5(self): self.handle_event("SW5")

    def encoder_handler(self, event):
        if (event == Encoder.DEC):
            self.handle_event("DEC")
        elif (event == Encoder.INC):
            self.handle_event("INC")
        elif (event == Encoder.TAP):
            self.handle_event("TAP")


async def test_ui():
    testprogram = TestProgram()
    testprogram.active(1)

    while True:
        await asyncio.sleep(1)
