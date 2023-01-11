import uasyncio as asyncio
from program_menu import MainMenu
from program_settings import Settings
from program_pwm import Pwm

async def main():
  open_pwm = lambda: pwm_program.active(1)
  open_menu = lambda: main_menu_program.active(1)
  open_settings = lambda: settings_program.active(1)

  # run this first, this is the critical part.
  pwm_program = Pwm(on_exit=open_menu)

  main_menu_program = MainMenu(
    open_pwm=open_pwm,
    open_settings=open_settings
  )

  settings_program = Settings(on_exit=open_menu)

  # Start with menu
  open_menu()

if __name__ == "__main__":
  asyncio.run(main())
