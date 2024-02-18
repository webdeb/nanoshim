import os
from lib.menu import Menu
from lib.autostart import get_autostart, add_to_autostartable

# PWM Programms
from programs.twopwm import Program as TwoPWM
# Utils
from programs.rlc_calculator.program import Program as RLCCalculator
# Settings
from programs.program_settings import Settings


async def create_main_menu():
    custom = import_custom()
    main_menu_items = [
        Menu([

            # PPPP,
            TwoPWM,
            # TwoFAM,
            # SixMix,
        ], "PWM Programms"),
        Menu([
            RLCCalculator,
        ], "Utils"),
        Settings,
    ]

    if (custom):
        print("Add custom programs")
        main_menu_items.insert(1, custom)
    else:
        print("No custom programs")

    main_menu = Menu(main_menu_items)
    add_to_autostartable("Menu", main_menu)
    autostart_program = get_autostart()
    if (autostart_program):
        autostart_program.start()
    else:
        main_menu.start()


def import_custom():
    try:
        programs = []
        for f in os.listdir('/plugins'):
            if (f.endswith("_program.py")):
                programs.append(__import__(
                    f"/plugins/{f[0:-3]}", None, None, ["Program"]).Program)

        return Menu(programs, "My Programs")
    except:
        return False
