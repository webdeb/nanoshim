from rp2 import PIO, asm_pio

LOW = 5
HIGH = 5
PERIOD = LOW + HIGH

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
  nop()                    [3]     # 4xh
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x

  wrap()

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
  nop()                    [3]     # 4xh
  wrap()

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_program():
  label("load")
  pull()
  out(isr, 32)
  pull()

  wrap_target()

  mov(y, isr)                      # l 
  jmp(not_y, "load")               # l
  mov(x, osr)                   [1]# 2xl

  label("high")
  jmp(y_dec, "high")  .side(1)     # h
  nop()                         [3]# 4h
  label("low")
  jmp(x_dec, "low")   .side(0)     # l + x

  wrap()
