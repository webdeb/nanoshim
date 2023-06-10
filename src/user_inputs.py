# Define here all User Inputs like Buttons and Rotary Encoder
import lib.rotary as rotary
from lib.levels import Levels

from constants import (
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

Buttons = Levels(
    pin=PIN_KEYS,
    levels=(SW1, SW2, SW3, SW4, SW5),
    cb=lambda level: print("No callback yet for", level)
)

Encoder = rotary.Rotary(
    PIN_ENC_A,
    PIN_ENC_B,
    PIN_ENC_C
)
