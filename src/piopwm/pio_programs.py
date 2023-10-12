from rp2 import PIO, asm_pio

LOW = 5
HIGH = 5
PERIOD = LOW + HIGH
# 96ns min period (48ns + 48ns), 32bit per high and low (70s per period up to 96ns per period with a 8ns step.)

# 9 Instructions


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_program():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # l
    jmp(not_y, "load")               # l
    mov(x, osr)[1]  # 2xl

    label("high")
    jmp(y_dec, "high")  .side(1)     # h
    nop()[3]  # 4h
    label("low")
    jmp(x_dec, "low")   .side(0)     # l + x

    wrap()


# 10 instructions
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_with_pin_program():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # l
    mov(x, osr)                      # l
    jmp(not_y, "load")               # l

    wait(1, pin, 0)                  # l
    label("high")
    jmp(y_dec, "high")  .side(1)     # h + y
    nop()[3]     # 4xh
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
    nop()[3]  # 4h
    label("low")
    jmp(x_dec, "low")     .side(0)    # l + x

    # other shoulder..
    mov(y, isr)                       # l
    jmp(not_y, "load")                # l
    mov(x, osr)[1]  # 2xl

    label("high_2")
    jmp(y_dec, "high_2")  .side(0b10)  # h
    nop()[3]  # 4h
    label("low_2")
    jmp(x_dec, "low_2")   .side(0)    # l + x

    wrap()


"""
Triggered Push Pull
"""


@asm_pio()
def trigger_low_high():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)                      # l
    jmp(not_y, "load")               # l
    mov(x, osr)[1]  # 2xl

    irq(4)
    label("high")
    jmp(y_dec, "high")
    nop()[2]  # 4h

    irq(5)
    label("low")
    jmp(x_dec, "low")               # l + x

    wrap()


@asm_pio(sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def triggered_push_pull():
    label("load")
    pull()
    out(isr, 32)
    pull()

    wrap_target()

    mov(y, isr)             .side(0)        # l
    jmp(not_y, "load")      .side(0)        # l
    mov(x, osr)             .side(0)        # l

    wait(1, irq, 4)            .side(0)        # l
    label("high_1")
    jmp(y_dec, "high_1")    .side(0b01)     # h
    wait(1, irq, 5)            .side(0)        # l
    label("high_2")
    jmp(x_dec, "high_2")    .side(0b10)     # h

    wrap()
