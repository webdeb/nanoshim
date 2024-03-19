from lib.utils import is_int
from lib.constants import (
    OUT1,
    OUT2,
    OUT3,
    OUT4,
    OUT5,
    OUT6,

    PIN_GP02,
    PIN_GP03,
    PIN_GP04,
)


PIN_MAPPING = {
    "OUT1": OUT1,
    "OUT2": OUT2,
    "OUT3": OUT3,
    "OUT4": OUT4,
    "OUT5": OUT5,
    "OUT6": OUT6,
    "GP02": PIN_GP02,
    "GP03": PIN_GP03,
    "GP04": PIN_GP04,
}

def resolve_pin(v):
    if (v is None):
        return None
    if (is_int(v)):
        return v
    return PIN_MAPPING[v] or None


def get_pin_value(v, optional=True):
    pin = resolve_pin(v)
    if isinstance(pin, int):
        return pin
