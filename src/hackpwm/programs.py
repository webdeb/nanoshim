from hackpwm.pio import PIOWrapper, PIO, asm_pio
from lib.utils import percent_str, ticks_to_time_str, ticks_to_freq_str
from lib.fields import Field, LabelField


class BasePIOControl(PIOWrapper):
    instructions = 8
    param_1_label = "X"
    param_2_label = "Y"
    fields = None

    store_structure = {
        "version": 0,
        "x": 10000,
        "y": 10000,
    }
    extend_store_structure = {}

    # Creation of the StateMachine inside a PWMSystem
    def __init__(self, label=None):
        self.label = label

    def run(self):
        self.active(1)

    def setup_store(self, store):
        self.store = store

    def get_fields(self):
        if (self.fields == None):
            self.fields = self.create_fields()

        return self.fields

    # change params for each machine/program.
    def setup_machine(self, sm_id):
        self.create_sm(sm_id)
        self.init_params()

    def init_params(self):
        self.x(self.store.get("y"))
        self.y(self.store.get("x"))

        self.update_params()

    def update_params(self, apply=0):
        self.store.set("x", self.x())
        self.store.set("y", self.y())

        if (apply):
            self.apply_params()

    def on_change_x(self, value):
        self.x(value)
        self.update_params()

    def on_change_y(self, value):
        self.x(value)
        self.update_params()

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label).item())

        fields.append(Field(self.param_1_label,
                            get_value=self.x,
                            on_change=self.on_change_x,
                            ).item())
        fields.append(Field(self.param_2_label,
                            get_value=self.y,
                            on_change=self.on_change_y,
                            ).item())

        return fields


"""
PWM Program
"""

# 8 Instructions


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_program():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # x
    jmp(not_y, "load")               # x
    mov(x, osr)                      # x

    label("high")
    jmp(y_dec, "high")  .side(1)     # y

    label("low")
    jmp(x_dec, "low")   .side(0)     # x

    wrap()


class PWM(BasePIOControl):
    DUTY_MODE_PERCENT = 1
    program = pwm_program
    instructions = 8
    param_period_label = "F"
    param_duty_label = "D"
    X = 4
    Y = 1
    fields = None

    extend_store_structure = {
        "version": 1,
        "duty_percent": None,
    }

    def get_duty(self): return self.x()
    def get_period(self): return self.x() + self.y()
    def get_duty_percent(self): return self.store.get("duty_percent")

    # Creation of the StateMachine inside a PWMSystem
    def __init__(self, label=None, pin=None):
        self.label = label
        self.pin = pin

    def setup_machine(self, sm_id):
        self.create_sm(sm_id, sideset_base=self.pin)
        self.init_params()

    def create_fields(self):
        fields = []
        if (self.label):
            fields.append(LabelField(self.label).item())

        fields.extend([
            Field(
                self.param_1_label,
                get_value=self.get_period,
                render_value=ticks_to_freq_str,
                on_change=self.on_change_period,
                with_exp=True,
                is_freq=True
            ).item(),
            Field(
                self.param_2_label,
                get_value=self.x,
                render_value=self.render_duty,
                on_change=self.on_change_duty,
                on_mode=self.switch_duty_mode,
                with_exp=True
            ).item()
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
        duty = self.x()
        if (self.is_duty_percent()):
            duty = round(value * self.get_duty_percent())

        self.x(duty)
        self.y(value - duty)

        self.update_params(1)

    def on_change_duty(self, value):
        y = self.y(min(value, self.get_period()))
        if (self.is_duty_percent()):
            self.store.set("duty_percent", y / self.get_period())
        self.store.set("duty", y)

    def switch_duty_mode(self, e):
        if (self.is_duty_percent()):
            self.store.set("duty_percent", None)
        else:
            self.store.set("duty_percent", self.x() / self.get_period())

    def is_duty_percent(self):
        return self.store.get("duty_percent") is not None


"""
PWM_WITH_PIN("Puls", pin=OUT2, in_pin=OUT1)
"""


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program():
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


class PWM_WITH_PIN(PWM):
    instructions = 9
    X = 5
    Y = 1
    program = pwm_with_pin_program

    def __init__(self, label, pin, in_pin):
        self.label = label
        self.pin = pin
        self.in_pin = in_pin

    def setup_machine(self, sm_id):
        self.create_sm(sm_id, sideset_base=self.pin, in_base=self.in_pin)
        self.init_params()


"""
TRIGGER_45
"""


@asm_pio()
def trigger_45():
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


class TRIGGER_45(PWM):
    instructions = 12
    program = trigger_45
    X = 6
    Y = 3
    param_2_label = "Sym"


"""
TRIGGER_45_WITH_PIN
"""


@asm_pio()
def trigger_45_with_pin():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # x
    jmp(not_y, "load")               # x
    mov(x, osr)                      # x

    irq(clear, 5)                    # x
    wait(1, pin, 0)                  # x
    irq(4)                           # y
    label("high")
    jmp(y_dec, "high")               # y

    irq(clear, 4)                    # y
    irq(5)                           # x
    label("low")
    jmp(x_dec, "low")                # x

    wrap()


class TRIGGER_45_WITH_PIN(PWM_WITH_PIN):
    instructions = 13
    program = trigger_45_with_pin
    param_2_label = "Sym"
    X = 7

    def setup_machine(self, sm_id):
        self.create_sm(sm_id, in_base=self.in_pin)

    def __init__(self, label, in_pin):
        self.label = label
        self.in_pin = in_pin


@asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def push_pull_45():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                 .side(0b00)        #
    jmp(not_y, "load")          .side(0b00)        #
    mov(x, osr)                 .side(0b00)        #
    wait(1, irq, 4)             .side(0b00)        #
    label("high_1")
    jmp(y_dec, "high_1")        .side(0b01)        # x
    wait(1, irq, 5)             .side(0b00)        #
    label("high_2")
    jmp(x_dec, "high_2")        .side(0b10)        # y

    wrap()


class PUSH_PULL_45(PWM):
    program = push_pull_45
    instructions = 10
    X = 1
    Y = 1
    param_x_label = "D1"
    param_y_label = "D2"
    store_structure = {
        "version": 1,
        "x": 1000,
        "y": 1000,
    }

    # getters
    def get_duty_x(self): return self.store.get("x")
    def get_duty_y(self): return self.store.get("y")

    def on_change_x(self, x):
        x = self.x(x)
        self.store.set("x", x)
        self.update_params(1)

    def on_change_y(self, y):
        y = self.y(y)
        self.store.set("y", y)
        self.update_params(1)

    def init_params(self):
        self.x(self.get_duty_x())
        self.y(self.get_duty_y())
        self.update_params()

    def update_params(self, apply=0):
        self.store.set("x", self.x())
        self.store.set("y", self.y())

        if (apply):
            self.apply_params()

    def create_fields(self):
        return [
            Field(self.param_x_label, get_value=self.get_duty_x, with_exp=True,
                  on_change=self.on_change_x, render_value=ticks_to_time_str),
            Field(self.param_y_label, get_value=self.get_duty_y, with_exp=True,
                  on_change=self.on_change_y, render_value=ticks_to_time_str),
        ]


@asm_pio(sideset_init=PIO.OUT_LOW)
def counter_after_4():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)         .side(0)     # x
    jmp(not_y, "load")               # x
    mov(x, osr)                      # x

    wait(1, irq, 4)                  # x
    label("wait")
    jmp(x_dec, "wait")               # x

    label("high")
    wait(1, pin, 0)     .side(1)     #
    jmp(y_dec, "high")               # y

    wrap()


class COUNT_AFTER_4(BasePIOControl):
    instructions = 10
    program = counter_after_4
    X = 5
    Y = 1

    param_phase_label = "Phase"
    param_count_label = "Count"

    def create_fields(self):
        return [
            Field(self.param_phase_label, get_value=self.x, with_exp=True,
                  on_change=self.on_change_x, render_value=ticks_to_time_str),
            Field(self.param_count_label, get_value=self.y,
                  on_change=self.on_change_y),
        ]


@asm_pio(sideset_init=PIO.OUT_LOW)
def counter_after_5():
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

    label("high")
    wait(1, pin, 0)     .side(1)
    jmp(y_dec, "high")       # y

    wrap()


class COUNT_AFTER_5(COUNT_AFTER_4):
    program = counter_after_5
