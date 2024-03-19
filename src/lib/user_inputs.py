# Define here all User Inputs like Buttons and Rotary Encoder
from lib.rotary import Rotary, INC, DEC, TAP
from lib.levels import Levels

from lib.constants import (
    PIN_ENC_A,
    PIN_ENC_B,
    PIN_ENC_C,
    PIN_KEYS
)

# Use Levels
SW1 = 100
SW2 = 9100
SW3 = 21000
SW4 = 33000
SW5 = 43000

_Buttons = None
_Encoder = None


def get_inputs():
    if (_Buttons == None or _Encoder == None):
        raise TypeError('Buttons or Encoder not initialized')

    return _Buttons, _Encoder


async def create_inputs():
    global _Buttons, _Encoder

    _Buttons = Levels(
        pin=PIN_KEYS,
        levels=(SW1, SW2, SW3, SW4, SW5),
        cb=lambda level: print("No callback yet for", level)
    )

    _Encoder = Rotary(
        PIN_ENC_A,
        PIN_ENC_B,
        PIN_ENC_C
    )

    return _Buttons, _Encoder
