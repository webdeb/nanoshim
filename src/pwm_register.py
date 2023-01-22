import uctypes

PWM_BASE = 0x40050000
PWM_CH_COUNT = 8
PWM_REG_W = 0x14
PWM_CSR_LAYOUT = {
  "RES1":       8 << uctypes.BF_POS | 24 << uctypes.BF_LEN | uctypes.BFUINT8,
  "PH_ADV":     7 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  "PH_RET":     6 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  "DIVMODE":    4 << uctypes.BF_POS | 2 << uctypes.BF_LEN | uctypes.BFUINT8,
  "B_INV":      3 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  "A_INV":      2 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  "PH_CORRECT": 1 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
  "EN":         0 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT8,
}

PWM_CSR = [uctypes.struct(PWM_BASE + n*PWM_REG_W, PWM_CSR_LAYOUT) for n in range(0, PWM_CH_COUNT)]

PWM_CTR_ADD = 0x08
PWM_CTR_LAYOUT = {
  "COUNTER":    0 << uctypes.BF_POS | 16 << uctypes.BF_LEN | uctypes.BFUINT32,
}
PWM_CTR = [uctypes.struct(
  PWM_BASE + # base for all PWM Registers
  n*PWM_REG_W + # The Offset this slice
  PWM_CTR_ADD, # The offset of this register, at the slice base
  PWM_CTR_LAYOUT # The Layout to apply
) for n in range(0, PWM_CH_COUNT)]

# PWM EN Register alias for all slices
PWM_EN = 0xa0
PWM_ENR = uctypes.bytearray_at(PWM_BASE + PWM_EN, 4)

# PWM EN register offset

# Enable or disable PWM channels

def set_pwm_channels(channels, en):
  en_reg = PWM_ENR[0]
  for channel in channels:
    if en:
      PWM_CSR[channel].EN = 0
      PWM_CTR[channel].COUNTER = 0
      en_reg |= (1 << channel)
    else:
      en_reg &= ~(1 << channel)

  PWM_ENR[0] = en_reg

def reset_pwm_counter(channel):
  PWM_CTR[channel].COUNTER = 0

def set_divmode_in_channel(n, divmode=1):
  PWM_CSR[n].DIVMODE = divmode

def set_channel_inverted(n, channel="B", inverted=1):
  if (channel == "B"):
    PWM_CSR[n].B_INV = inverted
  else:
    PWM_CSR[n].A_INV = inverted
