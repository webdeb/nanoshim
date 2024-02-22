from rp2 import asm_pio, PIO
from lib.utils import is_int


def create_pwm_program(wait_gpio=None, wait_polarity=1):
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

        if (wait_gpio):
            wait(wait_polarity, gpio, wait_gpio)

        label("high")
        jmp(y_dec, "high")  .side(1)     # y
        label("low")
        jmp(x_dec, "low")   .side(0)     # x

        wrap()

    return program


"""
[array('H', [32928, 24768, 32928, 41030, 96, 40999, 6278, 4167]), -1, -1, 1073770880, 0, None, None, 2]
[array('H', [32928, 24768, 32928, 8332, 41030, 96, 40999, 6279, 4168]), -1, -1, 1073774976, 0, None, None, 2]
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

    irq(4)                           # x
    label("high")
    jmp(y_dec, "high")               # y
    irq(clear, 4)                    # y

    irq(5)                           # x
    label("low")
    jmp(x_dec, "low")                # x
    irq(clear, 5)                    # x

    wrap()


# 10 Instructions
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program_inverted():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)         .side(0)     # l
    jmp(not_y, "load")               # l (dont care about "load" delay)
    mov(x, osr)                      # l

    wait(1, pin, 0)                  # l
    label("low")
    jmp(y_dec, "low")                # l + x
    label("high")
    jmp(x_dec, "high")  .side(1)     # h + y
    nop()[3]     # 4xh
    wrap()


# 10 Instructions
@asm_pio(sideset_init=PIO.OUT_HIGH)
def inverted_pin():
    wait(1, pin, 0)     .side(1)
    wait(0, pin, 0)     .side(0)

# 10 Instructions


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program_inverted_once():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)         .side(0)     # l
    jmp(not_y, "load")               # l (dont care about "load" delay)
    mov(x, osr)                      # l
    wait(0, pin, 0)                  # l
    wait(1, pin, 0)                  # l
    label("low")
    jmp(y_dec, "low")                # l + x
    label("high")
    jmp(x_dec, "high")  .side(1)     # h + y
    nop()[3]     # 4xh
    wrap()


# 16 Instructions
@asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def pushpull_program():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                       # l
    jmp(not_y, "load")                # l
    mov(x, osr)[1]  # 2xl

    label("high")
    jmp(y_dec, "high")    .side(0b01)  # h
    label("low")
    jmp(x_dec, "low")     .side(0)    # l + x

    # other shoulder..
    mov(y, isr)                       # l
    jmp(not_y, "load")                # l
    mov(x, osr)[1]  # 2xl

    label("high_2")
    jmp(y_dec, "high_2")  .side(0b10)  # h
    label("low_2")
    jmp(x_dec, "low_2")   .side(0)    # l + x

    wrap()

# 12


def create_asymmetric_push_pull(wait_irq=None, wait_pin=None):
    if (wait_irq is None and wait_pin is None):
        raise AttributeError(
            "Count after program: define wait_irq or wait_pin")

    @asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
    def push_pull():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)                         .side(0b00)        # l
        jmp(not_y, "load")                  .side(0b00)        # l
        mov(x, osr)                         .side(0b00)        # l
        if is_int(wait_irq):
            wait(0, irq, wait_irq)          .side(0b00)        # l
            wait(1, irq, wait_irq)          .side(0b00)        # l
        elif is_int(wait_pin):
            wait(1, gpio, wait_pin)         .side(0b00)        # l
        label("high_1")
        jmp(y_dec, "high_1")                .side(0b01)        # h
        if is_int(wait_irq):
            wait(0, irq, wait_irq + 1)      .side(0b00)        # l
            wait(1, irq, wait_irq + 1)      .side(0b00)        # l
        elif is_int(wait_pin):
            wait(0, gpio, wait_pin)         .side(0b00)        # l
        label("high_2")
        jmp(x_dec, "high_2")                .side(0b10)        # h

        wrap()

    return push_pull


def create_run_after_program(wait_irq=None, wait_pin=None):
    if (wait_irq is None and wait_pin is None):
        raise AttributeError(
            "Count after program: define wait_irq or wait_pin")

    @asm_pio(sideset_init=PIO.OUT_LOW)
    def program():
        label("load")
        pull()
        out(isr, 32)
        pull()

        wrap_target()

        mov(y, isr)             .side(0)        # l
        jmp(not_y, "load")                      # l
        if is_int(wait_irq):
            wait(0, irq, wait_irq)               # l
            wait(1, irq, wait_irq)               # l
        elif is_int(wait_pin):
            wait(0, gpio, wait_pin)
            wait(1, gpio, wait_pin)
        label("phase")
        jmp(y_dec, "phase")     .side(0)        # l
        mov(x, osr)             .side(1)        # l
        label("count")
        wait(1, pin, 0)
        wait(0, pin, 0)
        jmp(x_dec, "count")     .side(1)        # h

        wrap()

    return program
