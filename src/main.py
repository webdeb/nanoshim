import uasyncio as asyncio
# from program_menu import MainMenu
# from program_settings import Settings
# from pupapupu.program import Program as PupaPuPu
from misc.testinputs import test_ui
from misc.images import LOGO
from display import display
from time import sleep


async def main():
    print("Start main")

    # def open_pwm(): return pwm_program.active(1)
    # def open_menu(): return main_menu_program.active(1)
    # def open_settings(): return settings_program.active(1)

    # run this first, this is the critical part.
    # pwm_program = PupaPuPu(on_exit=open_menu)
    # settings_program = Settings(on_exit=open_menu)

    # main_menu_program = MainMenu({
    #     # "PWM": open_pwm,
    #     "Settings": open_settings
    # })

    # open_pwm()
    display.render_image()
    display.display.invert(0)

if __name__ == "__main__":
    try:
        print("main..")
        asyncio.run(test_ui())
    except:
        print("Something went wrong..")
