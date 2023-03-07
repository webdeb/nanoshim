import uasyncio as asyncio
from program_menu import MainMenu
from program_settings import Settings
from program_pwm_new import Pwm
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

if __name__ == "__main__":
  asyncio.run(main())
