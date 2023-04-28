import uctypes

PWM_LAYOUT = {
  "TOP": (0x10, {
    "RES_4":      16 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
    "WRAP":        0 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
  }),

  "COMPARE": (0x0c, {
    "B":          16 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
    "A":          0 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
  }),

  "COUNTER": (0x08, {
    "RES_3":      16 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
    "COUNTER":    0 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
  }),

  "DIV": (0x04, {
    "RES_2":      12 << uctypes.BF_POS | 20 << uctypes.BF_LEN | uctypes.BFUINT8,
    "INT":        4 << uctypes.BF_POS | 8 << uctypes.BF_LEN | uctypes.BFUINT32,
    "FRAC":       0 << uctypes.BF_POS | 4 << uctypes.BF_LEN | uctypes.BFUINT32,
  }),

  "CSR": (0, {
    "RES_1":      8 << uctypes.BF_POS | 24 << uctypes.BF_LEN | uctypes.BFUINT8,
    "PH_ADV":     7 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
    "PH_RET":     6 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
    "DIVMODE":    4 << uctypes.BF_POS | 2 << uctypes.BF_LEN | uctypes.BFUINT8,
    "B_INV":      3 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
    "A_INV":      2 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
    "PH_CORRECT": 1 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
    "EN":         0 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  }),
}
PWM_BASE = 0x40050000
PWM_CH_COUNT = 8
PWM_REG_W = 0x14
PWM_REGISTERS = [uctypes.struct(PWM_BASE + n*PWM_REG_W, PWM_LAYOUT) for n in range(0, PWM_CH_COUNT)]

# PWM EN register offset
PWM_EN = 0xa0
PWM_ENR = uctypes.bytearray_at(PWM_BASE + PWM_EN, 4)

# Enable or disable PWM channels
def set_pwm_channels(channels, en):
  en_reg = PWM_ENR[0]
  for channel in channels:
    channel, shift = channel
    if en:
      PWM_REGISTERS[channel].CSR.EN = 0
      PWM_REGISTERS[channel].COUNTER.COUNTER = shift

      en_reg |= (1 << channel)

      # print("PWM EN", PWM_REGISTERS[channel].CSR.EN)
      # print("PWM COUNTER", PWM_REGISTERS[channel].COUNTER.COUNTER)
      # print("PWM TOP", PWM_REGISTERS[channel].TOP.WRAP)
      # print("PWM COMPARE A", PWM_REGISTERS[channel].COMPARE.A)
      # print("PWM COMPARE B", PWM_REGISTERS[channel].COMPARE.B)
    else:
      en_reg &= ~(1 << channel)

  # print("PWM ENR",   f'0b{PWM_ENR[0]:08b}', f'0b{en_reg:08b}')
  PWM_ENR[0] = en_reg

def increase_top(pin, steps = 1):
  slice_number = get_pins_slice(pin)
  # print("INCREASE WRAP", PWM_REGISTERS[slice_number].TOP.WRAP, steps)
  PWM_REGISTERS[slice_number].TOP.WRAP += steps
  # print("INCREASE WRAP RESULT", PWM_REGISTERS[slice_number].TOP.WRAP)

def decrease_top(pin, steps = 1):
  slice_number = get_pins_slice(pin)
  # print("DECREASE WRAP", PWM_REGISTERS[slice_number].TOP.WRAP, steps)
  PWM_REGISTERS[slice_number].TOP.WRAP -= steps
  # print("DECREASE WRAP RESULT", PWM_REGISTERS[slice_number].TOP.WRAP)

def set_channel_inverted(n, channel="B", inverted=1):
  if (channel == "A"):
    PWM_REGISTERS[n].CSR.A_INV = inverted
  else:
    PWM_REGISTERS[n].CSR.B_INV = inverted

def set_slice_top(slice, top):
  PWM_REGISTERS[slice].TOP.WRAP = top

def get_pins_slice(pin):
  return pin // 2 % 8
    
def get_pins_channel(pin):
  return "A" if pin % 2 == 0 else "B"
