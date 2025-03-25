from lib.ui_program import UIListProgram
from lib.fields import LabelField, Field
from lib.units import FRenderer
from lib.utils import ticks_to_freq_str
from programs.settings.settings import set_freq
import machine

class FreqCalculator(UIListProgram):
  title = "Ma.Freq Tool"
  x = 1000000
  mf = 100
  ticks = 1

  def __init__(self, on_exit=None):
    self.items = [
      Field("F", get_value=lambda: self.x, on_change=self.set_x, render_value=self.render_x, with_exp=True).item(),
      LabelField("MF", get_addition=self.get_calculated_freq, on_mode=self.on_mode).item(),
      LabelField("Ticks", get_addition=self.get_calculated_ticks).item(),
      LabelField("Res F", get_addition=self.get_actual_freq).item(),
    ]

    super().__init__(on_exit)

  def set_x(self, x):
    self.x = x
    self.calc()
  
  def render_x(self, x):
     return f"{x}Hz"

  def calc(self):
    self.mf, self.ticks = get_best_machine_freq(self.x)

  def get_calculated_freq(self):
    if (machine.freq()/1_000_000 == self.mf):
       return f"= {self.mf}MHz"

    return f"{self.mf}MHz"

  def on_mode(self):
     machine.freq(self.mf * 1_000_000)
     set_freq(machine.freq())

  def get_calculated_ticks(self):
    return self.ticks

  def get_actual_freq(self):
    return ticks_to_freq_str(self.ticks, self.mf * 1_000_000)

def get_best_machine_freq(freq: int):
    best = float("infinity")
    best_idx: int
    rounded_ticks: int
    for idx, i in enumerate(range(100, 137)):
        ns_per_tick = 1000/i
        period_ns = 1_000_000_000/freq
        unrounded_ticks = period_ns / ns_per_tick
        rounded = round(unrounded_ticks)

        diff = abs(unrounded_ticks - rounded)

        if (diff < best):
            best = diff
            best_idx = idx
            rounded_ticks = rounded

    return best_idx + 100, rounded_ticks
