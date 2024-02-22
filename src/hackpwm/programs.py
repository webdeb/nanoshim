from rp2 import StateMachine, PIO, asm_pio
from hackpwm.pio_programs import create_pwm_program
from lib.utils import percent_str, ticks_to_time_str, ticks_to_freq_str, is_int
from lib.fields import Field, LabelField
from struct import pack


class PIOWrapper:
    MAX_VALUE = (1 << 31) - 1
    X = None
    Y = None

    _x = None
    _y = None

    program = None
    required = []
    instructions = None
    create_program = None
    paused = False

    def create_sm(self, id, **kwargs):
        missing_required = [
            attribute for attribute in self.required if attribute not in kwargs]

        if (len(missing_required) > 0):
            raise AttributeError(f"Missing attributes: {
                                 ', '.join(missing_required)}")
        if (callable(self.create_program)):
            self.program = self.create_program()

        if (self.program == None):
            raise AttributeError(f"Missing PIO program")

        self.id = id
        self.sm = StateMachine(self.id, prog=self.program, **kwargs)

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
        if (on):
            self.apply_params()
        self.sm.active(on)

    def pause(self):
        self.active(0)
        self.paused = True

    def resume(self):
        self.active(1)
        self.paused = False

    def apply_params(self):
        if self.paused:
            return
        if is_int(self._y):
            self.sm.put(self._y)
        if is_int(self._x):
            self.sm.put(self._x)

        self.sm.exec("in_(null, 32)")

    def stop_and_remove(self):
        pio = 0
        if (self.id > 3):
            pio = 1

        self.active(0)
        PIO(pio).remove_program(self.program)


class BasePIOControl(PIOWrapper):
    program = None
    instructions = 0
    label_x = "X"
    label_y = "Y"
    fields = None
    wait_pin = None
    count_pin = None
    pin = None

    # The base store structure
    store_structure = {
        "version": 0,
        "x": 10000,
        "y": 10000,
    }
    additional_store_items = {}

    def get_store_structure(self):
        return dict(self.store_structure, **self.additional_store_items)

    # Creation of the StateMachine inside a PWMSystem
    def __init__(self, label=None, pin=None, in_pin=None, wait_pin=None, count_pin=None):
        self.label = label
        self.in_pin = in_pin
        self.count_pin = count_pin
        self.wait_pin = wait_pin
        self.pin = pin

    def run(self):
        self.active(1)

    def setup_store(self, store):
        self.store = store

    def get_fields(self):
        if (self.fields == None):
            self.fields = list(map(lambda i: i.item(), self.create_fields()))

        return self.fields

    def get_machine_args(self):
        return {}

    def setup_machine(self, sm_id):
        self.create_sm(sm_id, **self.get_machine_args())
        self.init_params()

    def init_params(self):
        self.x(self.store.get("x"))
        self.y(self.store.get("y"))

        self.update_params()

    def update_params(self, apply=True):
        self.store.set("x", self.x())
        self.store.set("y", self.y())

        if (apply and self.sm.active()):
            self.apply_params()

    def on_change_x(self, value):
        self.x(value)
        self.update_params()

    def on_change_y(self, value):
        self.y(value)
        self.update_params()

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.extend([
            Field(self.label_x, get_value=self.x,
                  on_change=self.on_change_x),
            Field(self.label_y, get_value=self.y,
                  on_change=self.on_change_y)
        ])

        return fields


"""
PWM Program
"""


class PWM(BasePIOControl):
    instructions = 8
    label_period = "F"
    label_duty = "D"
    X = 4
    Y = 1
    fields = None
    wait_pin = None

    additional_store_items = {
        "version": 1,
        "duty_percent": None,
    }

    def get_duty(self): return self.y()

    def get_period(self):
        return self.x() + self.y()

    def get_duty_percent(self): return self.store.get("duty_percent")

    def create_program(self):
        return create_pwm_program(wait_gpio=self.wait_pin)

    def get_machine_args(self):
        return {"sideset_base": self.pin}

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label))

        fields.extend([
            Field(
                self.label_period,
                get_value=self.get_period,
                render_value=ticks_to_freq_str,
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
        y = self.y(min(value, period))
        if (self.is_duty_percent()):
            self.store.set("duty_percent", y / period)
        self.x(period - y)
        self.on_change_y(y)

    def switch_duty_mode(self, e):
        if (self.is_duty_percent()):
            self.store.set("duty_percent", None)
        else:
            self.store.set("duty_percent", self.y() / self.get_period())

    def is_duty_percent(self):
        return self.store.get("duty_percent") is not None


"""
PWM_WITH_PIN("Puls", pin=OUT2, in_pin=OUT1)
"""


class PWM_WITH_PIN(PWM):
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

        wait(1, pin, 0)                  # x
        label("high")
        jmp(y_dec, "high")  .side(1)     # y

        label("low")
        jmp(x_dec, "low")   .side(0)     # x

        wrap()

    instructions = 9
    X = 5
    Y = 1

    def get_machine_args(self):
        return {"sideset_base": self.pin, "in_base": self.in_pin}


"""
TRIGGER_45
"""


class TRIGGER_45(PWM):
    @asm_pio()
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)                      # x
        jmp(not_y, "load")               # x
        mov(x, osr)                      # x

        irq(clear, 5)                    # x
        irq(4)                           # y
        label("high")
        jmp(y_dec, "high")               # y

        irq(clear, 4)                    # y
        irq(5)                           # x
        label("low")
        jmp(x_dec, "low")                # x

        wrap()

    instructions = 12
    X = 6
    Y = 3
    label_duty = "Sym"

    # just rewrite some to always use %
    def switch_duty_mode(self, e): pass
    def is_duty_percent(self): return True


"""
TRIGGER_45_WITH_PIN
"""


class TRIGGER_45_WITH_PIN(TRIGGER_45):
    @asm_pio()
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        wait(1, pin, 0)                  # x
        mov(y, isr)                      # x
        jmp(not_y, "load")               # x
        mov(x, osr)                      # x

        irq(clear, 5)                    # x
        irq(4)                           # y
        label("high")
        jmp(y_dec, "high")               # y

        irq(clear, 4)                    # y
        irq(5)                           # x
        label("low")
        jmp(x_dec, "low")                # x

        wrap()

    def get_machine_args(self):
        return {"in_base": self.in_pin}

    instructions = 13
    X = 7


class PUSH_PULL_45(BasePIOControl):
    @asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)                 .side(0b00)        #
        jmp(not_y, "load")          .side(0b00)        #
        wait(1, irq, 4)             .side(0b00)        #
        label("high_1")
        jmp(y_dec, "high_1")        .side(0b01)        # x
        mov(x, osr)                 .side(0b00)        #
        wait(1, irq, 5)             .side(0b00)        #
        label("high_2")
        jmp(x_dec, "high_2")        .side(0b10)        # y

        wrap()

    instructions = 10
    X = 1
    Y = 1
    label_x = "D1"
    label_y = "D2"

    def get_machine_args(self):
        return {"sideset_base": self.pin}

    def create_fields(self):
        return [
            Field(self.label_x, get_value=self.x, with_exp=True,
                  on_change=self.on_change_x, render_value=ticks_to_time_str),
            Field(self.label_y, get_value=self.y, with_exp=True,
                  on_change=self.on_change_y, render_value=ticks_to_time_str),
        ]

    # Nice to have
    # need to provide context information.
    # could potentially lead to a circular dependency
    # Maybe simpler to use one class, but dependency would still be there..
    # additional_store_items = {
    #     "duty_percent_x": None,
    #     "duty_percent_y": None
    # }
    # def set_context(self, program: TRIGGER_45):
    #     self.context = program
    # def get_context_period(self):
    #     return self.context.get_period()
    # def on_context_change(self):
    #     duty_percent_x = self.get_duty_percent("x")
    #     duty_percent_y = self.get_duty_percent("y")
    #     if (duty_percent_x is not None):
    #         self.x(round(duty_percent_x * ))

    # def get_duty_percent(self, k):
    #     return self.store.get(f"duty_percent_{k}")

class ONCE_AFTER():
    

class COUNT_AFTER(BasePIOControl):
    instructions = 11
    label_phase = "Phs"
    label_count = "Count"
    X = 5
    Y = 1

    # def y(self, value=None):
    #     if (value is not None and value <= 0 and self.running):
    #         self.sm.active(0)

    #     if (self.sm.active() == 0 and self.running):
    #         self.sm.active(1)
    #     super().y(value)

    def get_machine_args(self):
        return {"sideset_base": self.pin, "in_base": self.in_pin}

    def create_program(self):
        return

    def create_fields(self):
        return [
            LabelField(self.label),
            Field(self.label_phase, get_value=self.x, with_exp=True,
                  on_change=self.on_change_x, render_value=ticks_to_time_str),
            Field(self.label_count, get_value=self.y, with_exp=True,
                  on_change=self.on_change_y),
        ]


def create_count_after_program(count_pin, wait_pin, wait_level=1):
    @asm_pio(sideset_init=PIO.OUT_LOW)
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)         .side(0)     # x
        jmp(not_y, "load")               # x
        mov(x, osr)                      # x

        wait(wait_level, gpio, wait_pin)                  # x
        label("wait")
        jmp(x_dec, "wait")               # x

        label("count")
        wait(1, gpio, count_pin)     .side(1)     #
        wait(0, gpio, count_pin)
        jmp(y_dec, "count")               # y

        wrap()

    return program


class COUNT_AFTER_5(COUNT_AFTER_4):
    @asm_pio(sideset_init=PIO.OUT_LOW)
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)         .side(0)     # x
        jmp(not_y, "load")               # x
        mov(x, osr)                      # x

        wait(1, irq, 5)
        label("low")
        jmp(x_dec, "low")                # x

        label("count")
        wait(1, pin, 0)     .side(1)
        wait(0, pin, 0)
        jmp(y_dec, "count")       # y

        wrap()
