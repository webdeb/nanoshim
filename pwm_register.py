import uctypes

PWM_CH_COUNT = 8
PWM_BASE = 0x40050000
PWM_CSR_WIDTH = 0x14
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

PWM_CSR = [uctypes.struct(PWM_BASE + n*PWM_CSR_WIDTH, PWM_CSR_LAYOUT) for n in range(0, PWM_CH_COUNT)]

def set_divmode_in_channel(n, divmode=1):
  PWM_CSR[n].DIVMODE = divmode
