from micropython import const
from rp2 import StateMachine, PIO, asm_pio
from lib.utils import percent_str, ticks_to_time_str, ticks_to_freq_str, is_int
from lib.fields import Field, LabelField
from hackpwm.pins import OUT1, OUT6, get_pin_value

def generate_out_pins(mode=0, inverted=0, pins=3):
  out_pins = []
  mask = ((1 << pins) - 1) * inverted
  for i in range(0, pins):
    a = mode * (pow(2, (i - 1) % pins) + pow(2, i))
    out_pins.append(a^mask)
    b = pow(2, i)
    out_pins.append(b^mask)

  return out_pins


class PIOWrapper:
    MAX_VALUE = (1 << 31) - 1
    X = None
    Y = None

    _x = None
    _y = None

    pid = None
    program = None
    required = []
    instructions = None
    create_program = None
    paused = False
    sm_id = None
    d = None # Defaults

    def get_machine_args(self):
        return {}

    def init_machine(self):
        args = self.get_machine_args()
        missing_required = [
            attribute for attribute in self.required if attribute not in args]

        if (len(missing_required) > 0):
            raise AttributeError(f"Missing attributes: {
                                 ', '.join(missing_required)}")

        if (self.program is None):
            raise AttributeError(f"Missing PIO program")

        self.sm = StateMachine(self.sm_id, self.program, **args)

    def setup_machine(self, sm_id):
        self.sm_id = sm_id
        self.init_machine()
        self.init_params()

    def init_params(self):
        if (isinstance(self.d, dict) and self.store.get("init")):
            self.store.set("init", False)
            self.store.set("y", self.d.get("y"))
            self.store.set("x", self.d.get("x"))
            if (hasattr(self.store.initial_data, "%")
                and hasattr(self.d, "%")):
                self.store.set("%", self.d.get("%"))

        self.x(self.store.get("x"))
        self.y(self.store.get("y"))

        self.update_params()

    def update_params(self):
        self.store.set("x", self.x())
        self.store.set("y", self.y())

        if (self.sm.active()):
            self.apply_params()

    def on_change_x(self, value):
        self.x(value)
        self.update_params()

    def on_change_y(self, value):
        self.y(value)
        self.update_params()


    def __init__(self):
        if (callable(self.create_program)):
            program, instructions, X, Y = tuple(self.create_program())
            self.instructions = instructions
            self.program = program
            self.X = X
            self.Y = Y

    def x(self, x=None):
        if self.X is None:
            raise KeyError("This program does not support `x` parameter")
        if x is not None:
            self._x = min(self.MAX_VALUE, max(0, int(x) - self.X))
            if (self._y == 0):
                self.pause()
            elif (self.paused):
                self.resume()

        return self._x + self.X

    def y(self, y=None):
        if self.Y == None:
            raise KeyError("This program does not support `y` parameter")
        if y is not None:
            self._y = min(self.MAX_VALUE, max(0, int(y) - self.Y))
            if (self._y == 0):
                self.pause()
            elif (self.paused):
                self.resume()

        return self._y + self.Y

    def active(self, on=1):
        if (on == 1):
            self.apply_params()
            self.sm.active(1)
        else:
            self.sm.active(0)
            self.init_machine()

    def pause(self):
        self.active(0)
        self.paused = True

    def resume(self):
        self.active(1)
        self.paused = False

    def apply_params(self):
        if self.paused:
            return

        if is_int(self._y): self.sm.put(self._y)
        if is_int(self._x): self.sm.put(self._x)

        if self.sm.tx_fifo() > 0:
            self.sm.exec("in_(null, 32)")

    def remove(self):
        PIO(pio_by_sid(self.sm_id)).remove_program(self.program)

    # The base store structure
    def setup_store(self, store):
        self.store = store

    store_structure = {
        "version": 0,
        "init": True,
        "x": 10000,
        "y": 10000,
    }
    additional_store_items = {}

    def get_store_structure(self):
        store_struct = dict(self.store_structure,
                            **({"pid": self.pid}),
                            **self.additional_store_items)
        return store_struct

    def run(self):
        self.active(1)

class BasePIOControl(PIOWrapper):
    # program = None
    # instructions = 0
    label_x = "X"
    label_y = "Y"
    fields = None
    wait_pin = None
    wait_level = 1
    count_pin = None
    inverted = False
    label = None
    pin = None
    pid = None

    # Creation of the StateMachine inside a PWMSystem
    def __init__(self, label=None, pin=None, wait_pin=None, count_pin=None, wait_level=1, d=None, inverted=False, **kwargs):
        self.label = label
        self.count_pin = get_pin_value(count_pin)
        self.wait_pin = get_pin_value(wait_pin)
        self.wait_level = wait_level
        self.pin = get_pin_value(pin)
        self.inverted = inverted
        self.d = d
        super().__init__()

    def get_fields(self):
        if (self.fields == None):
            self.fields = list(map(lambda i: i.item(), self.create_fields()))

        return self.fields

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.extend([
            Field(self.label_x, get_value=self.x,
                  on_change=self.on_change_x, render_value=self.render_x),
            Field(self.label_y, get_value=self.y,
                  on_change=self.on_change_y, render_value=self.render_y)
        ])

        return fields

    def render_x(self, v):
        return str(v)

    def render_y(self, v):
        return str(v)

"""
PWM Program
"""
class PWM(BasePIOControl):
    pid = "PWM"
    label_period = "F"
    label_duty = "D"
    wait_pin = None

    additional_store_items = {
        "%": None,
    }

    def create_pwm_program(self, wait_pin=None, wait_level=1):
        @asm_pio(sideset_init=PIO.OUT_LOW)
        def program():
            label("load")
            pull()
            out(isr, 32)
            pull()

            wrap_target()

            mov(y, isr)                      # x
            jmp(not_y, "load")               # x
            mov(x, osr)                      # x

            if isinstance(wait_pin, int):
                 wait(wait_level, gpio, wait_pin) # x

            label("high")
            jmp(y_dec, "high")  .side(1)     # y
            label("low")
            jmp(x_dec, "low")   .side(0)     # x

            wrap()

        X = 5 if is_int(wait_pin) else 4
        return program, len(program[0]), X, 1

    def create_program(self):
        return self.create_pwm_program(
            wait_pin=self.wait_pin, wait_level=self.wait_level)

    def get_duty(self): return self.y()

    def get_period(self):
        return self.x() + self.y()

    def get_duty_percent(self): return self.store.get("%")

    def get_machine_args(self):
        return {"sideset_base": self.pin}

    def render_period(self, value):
        return ticks_to_freq_str(value)

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.extend([
            Field(
                self.label_period,
                get_value=self.get_period,
                render_value=self.render_period,
                on_change=self.on_change_period,
                with_exp=True,
                is_freq=True
            ),
            Field(
                self.label_duty,
                get_value=self.y,
                render_value=self.render_duty,
                on_change=self.on_change_duty,
                on_mode=self.switch_duty_mode,
                with_exp=True
            )
        ])

        return fields

    # renderer
    def render_duty(self, value):
        if (self.is_duty_percent()):
            return percent_str(self.get_duty_percent())
        else:
            return ticks_to_time_str(value)

    # update functions
    def on_change_period(self, value):
        duty = self.y()
        if (self.is_duty_percent()):
            duty = round(value * self.get_duty_percent())
        self.y(duty)
        self.on_change_x(value - duty)

    def on_change_duty(self, value):
        period = self.get_period()
        y = self.y(min(value, period - self.X))
        if (self.is_duty_percent()):
            self.store.set("%", y / period)
        self.x(period - y)
        self.on_change_y(y)

    def switch_duty_mode(self, e):
        if (self.is_duty_percent()):
            self.store.set("%", None)
        else:
            self.store.set("%", self.y() / self.get_period())

    def is_duty_percent(self):
        return self.store.get("%") is not None


"""
PUSH PULL Program
"""


class PUSH_PULL(PWM):
    pid = "PUSH_PULL"

    def create_push_pull_program(self, wait_pin=None, wait_level=1):
        @asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
        def program():
            label("load")
            pull()
            out(isr, 32)
            pull()

            wrap_target()

            mov(y, isr)                             # l
            jmp(not_y, "load")                      # l
            mov(x, osr)                             # l
            if isinstance(wait_pin, int):
                wait(wait_level, gpio, wait_pin)    # l
            label("high_1")
            jmp(y_dec, "high_1")    .side(0b01)     # h
            label("low_1")
            jmp(x_dec, "low_1")     .side(0)        # l + x

            # other shoulder..
            mov(y, isr)                             # l
            jmp(not_y, "load")                      # l
            mov(x, osr)[int(wait_pin is not None)]           # l
            label("high_2")
            jmp(y_dec, "high_2")  .side(0b10)       # h
            label("low_2")
            jmp(x_dec, "low_2")   .side(0)          # l + x

            wrap()

        X = 5 if is_int(wait_pin) else 4
        return program, len(program[0]), X, 1

    def render_period(self, value):
        return ticks_to_freq_str(value * 2)

    def create_program(self):
        return self.create_push_pull_program(
            wait_pin=self.wait_pin,
            wait_level=self.wait_level
        )


"""
PHASE PULSE
"""

class PHASE_PULSE(BasePIOControl):
    pid = "PHASE_PULSE"
    label_phase = "Phs"
    label_count = "Count"
    label_duty = "D"

    def create_phase_pulse_program(self, wait_pin=None, wait_level=None, count_pin=None):
        @asm_pio(set_init=PIO.OUT_LOW)
        def program():
            label("load")
            pull()
            out(isr, 32)
            pull()

            wrap_target()
            label("wrap")
            set(pins, 0)
            mov(y, isr)                      # x
            jmp(not_y, "load")               # x
            mov(x, osr)                      # x
            wait(int(not wait_level), gpio, wait_pin)
            wait(wait_level, gpio, wait_pin)                  # x

            label("wait")
            jmp(x_dec, "wait")               # x

            set(pins, 1)
            if (isinstance(count_pin, int)):
                label("run")
                jmp(not_y, "wrap")
                wait(1, gpio, count_pin)
                wait(0, gpio, count_pin)
            else:
                label("run")
            jmp(y_dec, "run")
            wrap()

        return program, len(program[0]), 6, 0 if is_int(count_pin) else 1


    def create_program(self):
        return self.create_phase_pulse_program(
            wait_pin=self.wait_pin,
            wait_level=self.wait_level,
            count_pin=self.count_pin
        )

    def get_machine_args(self):
        return {"set_base": self.pin}

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.append(Field(self.label_phase, get_value=self.x, with_exp=True,
                      on_change=self.on_change_x, render_value=ticks_to_time_str))

        if (is_int(self.count_pin)):
            duty_field = Field(
                self.label_count, get_value=self.y,
                with_exp=True, on_change=self.on_change_y)
        else:
            duty_field = Field(
                self.label_duty, get_value=self.y, render_value=ticks_to_time_str,
                with_exp=True, on_change=self.on_change_y)

        fields.append(duty_field)
        return fields

class INVERT(BasePIOControl):
    pid = "INVERT"
    X = None
    Y = None

    def get_machine_args(self):
        return {"sideset_base": self.pin}

    def create_program(self):
        @asm_pio(sideset_init=PIO.OUT_LOW)
        def program():
            wait(0, gpio, self.wait_pin) .side(0)
            wait(1, gpio, self.wait_pin) .side(1)

        return program, len(program[0]), 0, 0

    def get_fields(self):
        return []

class COPY(BasePIOControl):
    pid = "COPY"
    X = None
    Y = None

    def get_machine_args(self):
        return {"sideset_base": self.pin}

    def create_program(self):
        @asm_pio(sideset_init=PIO.OUT_LOW)
        def program():
            wait(1, gpio, self.wait_pin) .side(0)
            wait(0, gpio, self.wait_pin) .side(1)

        return program, len(program[0]), 0, 0

    def get_fields(self):
        return []


class IRQ_TRIGGER(BasePIOControl):
    pid = "IRQ_TRIGGER"
    label_x = "X"
    label_y = "Y"

    def create_program(self):
        @asm_pio()
        def program():
            label("load")
            pull()
            out(isr, 32)
            pull()

            wrap_target()

            mov(y, isr)                      # x
            jmp(not_y, "load")               # x
            mov(x, osr)
                                             # x
            irq(clear, 5)
            irq(4)                           # x
            label("high")
            jmp(y_dec, "high")               # y
            irq(clear, 4)

            irq(5)                           # x
            label("low")
            jmp(x_dec, "low")                # x

            wrap()

        return program, len(program[0]), 7, 2
    
    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.extend([
            Field(self.label_x, get_value=self.x,
                  on_change=self.on_change_x, render_value=ticks_to_time_str, with_exp=True),
            Field(self.label_y, get_value=self.y,
                  on_change=self.on_change_y, render_value=ticks_to_time_str, with_exp=True)
        ])

        return fields

OVERLAP_MODE = const("OVERLAP")

class MIX(IRQ_TRIGGER):
    pid = const("MIX")
    label_x = "X"
    label_y = "Y"
    sm_id = 0

    def __init__(self, pin=OUT1, mode=None, pins=2, **kwargs):
        self.pins = min(pins, get_pin_value(OUT6) - get_pin_value(pin) + 1)
        self.mode = mode
        super().__init__(pin=pin, **kwargs)

    def create_mix_program(self):
        if (self.pins == 6):
            return create_six_pin_mix_program(self.inverted, self.mode)
        else:
            pins = self.pins
            inverted = self.inverted
            mode = int(self.mode is OVERLAP_MODE)
            inverted = int(inverted)
            init_polarity = PIO.OUT_HIGH if inverted else PIO.OUT_LOW
            out_pins = generate_out_pins(mode, inverted, pins)

            @asm_pio(sideset_init=[init_polarity]*pins)
            def program():
                for i in range(0, len(out_pins), 2):
                    wait(1, irq, 4).side(out_pins[i])
                    wait(1, irq, 5).side(out_pins[i+1])

            return program, len(program), 0, 0

    def init_params(self):
        super().init_params()


    def init_machine(self):
        mix_args = {"sideset_base": self.pin}
        if (self.pins == 6): mix_args["set_base"] = OUT6

        self.sm = StateMachine(self.sm_id[0], self.program)
        self.mix_sm = StateMachine(self.sm_id[1], self.mix_program, **mix_args)

    def active(self, on=1):
        if (on == 1):
            super().active(1)
            self.mix_sm.active(on)
        else:
            self.mix_sm.active(on)
            super().active(0)

    def remove(self):
        PIO(pio_by_sid(self.sm_id[0])).remove_program(self.program)
        PIO(pio_by_sid(self.sm_id[1])).remove_program(self.mix_program)

    def create_program(self):
        self.mix_program, mix_inst, _, _ = self.create_mix_program()
        self.program, instructions, X, Y = tuple(super().create_program())
        return (self.program, [instructions, mix_inst], X, Y)

    def on_change_x(self, value):
        if (self.mode is OVERLAP_MODE):
            period = self.y() + 2*self.x()
            self.y(max(int(self.Y), (period - value*2)))

        return super().on_change_x(value)

ALL_PROGRAMS = [PWM, PUSH_PULL, PHASE_PULSE, COPY, INVERT, IRQ_TRIGGER, MIX]

def create_six_pin_mix_program(inverted, mode):
    init_pol = PIO.OUT_HIGH if inverted else PIO.OUT_LOW
    args = {"set_init": init_pol, "sideset_init": [init_pol]*5}
    if inverted and mode == OVERLAP_MODE:
        @asm_pio(**args)
        def program():
            wait(1, irq, 4)     .side(0b11111)  # <- dis 5
            wait(1, irq, 5)     .side(0b11110)  # <- en 1
            set(pins, 1)        .side(0b11110)  # <- dis 6
            wait(1, irq, 4)     .side(0b11110)  # <- just keep to not use opt
            wait(1, irq, 5)     .side(0b11100)  # <- en 2
            wait(1, irq, 4)     .side(0b11101)  # <- dis 1
            wait(1, irq, 5)     .side(0b11001)  # <- en 3
            wait(1, irq, 4)     .side(0b11011)  # <- dis 2
            wait(1, irq, 5)     .side(0b10011)  # <- en 4
            wait(1, irq, 4)     .side(0b10111)  # <- dis 3
            wait(1, irq, 5)     .side(0b00111)  # <- en 5
            wait(1, irq, 4)     .side(0b01111)  # <- dis 4
            set(pins, 0)        .side(0b01111)  # <- en 6
            wait(1, irq, 5)     .side(0b01111)  # <- just keep to not use opt
    elif mode == OVERLAP_MODE:
        @asm_pio(**args)
        def program():
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b00001)  # <- en 1
            set(pins, 0)        .side(0b00001)  # <- dis 6
            wait(1, irq, 4)     .side(0b00001)  # <- just keep to not use opt
            wait(1, irq, 5)     .side(0b00011)  # <- en 2
            wait(1, irq, 4)     .side(0b00010)  # <- dis 1
            wait(1, irq, 5)     .side(0b00110)  # <- en 3
            wait(1, irq, 4)     .side(0b00100)  # <- dis 2
            wait(1, irq, 5)     .side(0b01100)  # <- en 4
            wait(1, irq, 4)     .side(0b01000)  # <- dis 3
            wait(1, irq, 5)     .side(0b11000)  # <- en 5
            wait(1, irq, 4)     .side(0b10000)  # <- dis 4
            set(pins, 1)        .side(0b10000)  # <- en 6
            wait(1, irq, 5)     .side(0b10000)  # <- just keep to not use opt
    elif inverted:
        @asm_pio(**args)
        def program():
            wait(1, irq, 4)     .side(0b11111)
            wait(1, irq, 5)     .side(0b11110)
            wait(1, irq, 4)     .side(0b11111)
            wait(1, irq, 5)     .side(0b11101)
            wait(1, irq, 4)     .side(0b11111)
            wait(1, irq, 5)     .side(0b11011)
            wait(1, irq, 4)     .side(0b11111)
            wait(1, irq, 5)     .side(0b10111)
            wait(1, irq, 4)     .side(0b11111)
            wait(1, irq, 5)     .side(0b01111)
            wait(1, irq, 4)     .side(0b11111)
            set(pins, 0)        .side(0b11111)
            wait(1, irq, 5)     .side(0b11111)
            set(pins, 1)        .side(0b11111)
    else:
        @asm_pio(**args)
        def program():
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b00001)  # <- en 1
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b00010)  # <- en 1
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b00100)  # <- en 1
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b01000)  # <- en 1
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            wait(1, irq, 5)     .side(0b10000)  # <- en 1
            wait(1, irq, 4)     .side(0b00000)  # <- dis 5
            set(pins, 1)        .side(0b00000)
            wait(1, irq, 5)     .side(0b00000)  # <- en 1
            set(pins, 0)        .side(0b00000)

    return program, len(program[0]), 0, 0


def pio_by_sid(sid):
    return 1 if sid > 3 else 0
