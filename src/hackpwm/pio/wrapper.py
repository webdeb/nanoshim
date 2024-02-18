from rp2 import StateMachine, PIO

MAX_VALUE = (1 << 31) - 1
# PIO_PROGRAMS = []


def is_int(n):
    return isinstance(n, int)


class PIOWrapper:
    # Program min amount of X and Y
    X = None
    Y = None

    _x = None
    _y = None

    program = None
    required = []
    instructions = None

    def create_sm(self, id, **kwargs):
        missing_required = [
            attribute for attribute in self.required if attribute not in kwargs]
        if (len(missing_required) > 0):
            raise AttributeError(f"Missing attributes: {
                                 ', '.join(missing_required)}")
        if (self.program == None):
            raise AttributeError(f"Missing PIO program")

        self.id = id
        self.sm = StateMachine(self.id, prog=self.program, **kwargs)

    def x(self, x=None):
        if self.X == None:
            raise KeyError("This program does not support `x` parameter")
        if (x is not None):
            self._x = min(MAX_VALUE, max(0, int(x) - self.X))

        return self._x + self.X

    def y(self, y=None):
        if self.Y == None:
            raise KeyError("This program does not support `y` parameter")
        if (y is not None):
            self._y = min(MAX_VALUE, max(0, int(y) - self.Y))

        return self._y + self.Y

    def active(self, on=1):
        if (on):
            self.apply_params()
        self.sm.active(on)

    def apply_params(self):
        if isinstance(self._x, int):
            self.sm.put(self._x)
        if isinstance(self._y, int):
            self.sm.put(self._y)

        self.sm.exec("in_(null, 32)")

    def stop_and_remove(self):
        pio = 0
        if (self.id > 3):
            pio = 1

        self.active(0)
        # PIO(pio).state_machine(self.id % 4, self.program).active(0)
        PIO(pio).remove_program(self.program)


# def clearPIO():
#     while PIO_PROGRAMS:
#         pio = 0
#         (sid, program) = PIO_PROGRAMS.pop()
#         if (sid > 3):
#             pio = 1

#         PIO(pio).state_machine(sid % 4, program).active(0)
#         PIO(pio).remove_program(program)
