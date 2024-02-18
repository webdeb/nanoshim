from rp2 import asm_pio, PIO
from .wrapper import PIOWrapper


# 13
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


class TRIGGER_45Program(PIOWrapper):
    instructions = 13
    program = trigger_45


# 9 instructions
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # l
    jmp(not_y, "load")               # l
    mov(x, osr)                      # l

    wait(1, pin, 0)                  # l
    label("high")
    jmp(y_dec, "high")  .side(1)     # h + y
    label("low")
    jmp(x_dec, "low")   .side(0)     # l + x

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
    wrap_target()
    wait(1, pin, 0)     .side(1)
    wait(0, pin, 0)     .side(0)
    wrap()

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


@asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def triggered_push_pull():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)             .side(0b00)        # l
    jmp(not_y, "load")      .side(0b00)        # l
    mov(x, osr)             .side(0b00)        # l
    wait(0, irq, 4)         .side(0b00)
    wait(1, irq, 4)            .side(0b00)        # l
    label("high_1")
    jmp(y_dec, "high_1")    .side(0b01)     # h
    wait(0, irq, 5)            .side(0b00)
    wait(1, irq, 5)            .side(0b00)        # l
    label("high_2")
    jmp(x_dec, "high_2")    .side(0b10)     # h

    wrap()

# 12


@asm_pio(sideset_init=PIO.OUT_LOW)
def count_after_4():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)             .side(0)        # l
    jmp(not_y, "load")      .side(0)        # l

    wait(0, irq, 4)         .side(0)        # l
    wait(1, irq, 4)         .side(0)        # l
    label("phase")
    jmp(y_dec, "phase")     .side(0)        # l
    mov(x, osr)             .side(1)        # l
    label("count")
    wait(1, pin, 0)
    wait(0, pin, 0)
    jmp(x_dec, "count")     .side(1)        # h

    wrap()


@asm_pio(sideset_init=PIO.OUT_LOW)
def count_after_5():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)             .side(0)        # l
    jmp(not_y, "load")      .side(0)        # l

    wait(0, irq, 5)         .side(0)        # l
    wait(1, irq, 5)         .side(0)        # l
    label("phase")
    jmp(y_dec, "phase")     .side(0)        # l
    mov(x, osr)             .side(1)        # l
    label("count")
    wait(1, pin, 0)
    wait(0, pin, 0)
    jmp(x_dec, "count")     .side(1)        # h

    wrap()


class COUNT_AFTER_45(PIOWrapper):
    X = 1
    Y = 6
    instructions = 12
    required = ["in_base", "sideset_base"]
