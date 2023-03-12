import uasyncio as asyncio
from program_menu import MainMenu
from program_settings import Settings
from program_pwm_new import Pwm
from machine import PWM, Pin
# from _pulse_package_pwm import Pwm

async def main():
  print("Start main")
  open_pwm = lambda: pwm_program.active(1)
  open_menu = lambda: main_menu_program.active(1)
  open_settings = lambda: settings_program.active(1)

  # run this first, this is the critical part.
  pwm_program = Pwm(on_exit=open_menu)
  settings_program = Settings(on_exit=open_menu)

  main_menu_program = MainMenu({
    "PWM": open_pwm,
    "Settings": open_settings
  })

  # Start with menu
  # open_menu()
  open_pwm()

async def test():
  pulse = (10, 5, "A")
  package = (14, 7, "A")

  # Push & Pull
  bigpack = (9, 4, "B")
  bigpack_inv = (8, 4, "A")

  pushpull_a = (6, 3, "A")
  pushpull_b = (7, 3, "B")

  pulse_pwm = PWM(Pin(pulse[0]))
  pulse_pwm.freq(1_000_000)
  pulse_pwm.duty_u16(30_000)

  package_pwm = PWM(Pin(package[0]))
  package_pwm.freq(200_000)
  package_pwm.duty_u16(30_000)

  bigpack_pwm = PWM(Pin(bigpack[0]))
  bigpack_pwm.freq(20_000)
  bigpack_pwm.duty_u16(30_000)

  bigpack_inv = PWM(Pin(bigpack_inv[0]))
  bigpack_inv.duty_u16(30000)

  pp_a_pwm = PWM(Pin(pushpull_a[0]))
  pp_a_pwm.freq(100_000)
  pp_a_pwm.duty_u16(20000)

  pp_b_pwm = PWM(Pin(pushpull_b[0]))
  pp_b_pwm.freq(100_000)
  pp_a_pwm.duty_u16(20000)


if __name__ == "__main__":
  asyncio.run(main())
