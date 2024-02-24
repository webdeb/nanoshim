import os
from lib.menu import Menu
from lib.autostart import get_autostart, add_to_autostartable

from programs.pwm.load_stored import load_systems
from programs.utilities.lc import Program as RLCCalculator
from programs.utilities.freq_calculator import FreqCalculator
from programs.settings import Settings

async def create_main_menu():
    custom = import_custom()
    main_menu_items = [
        Menu(title="PWM Systems", items=load_systems()),
        Menu(title="Utils", items=[RLCCalculator, FreqCalculator]),
        Settings,
    ]

    if (custom):
        main_menu_items.insert(1, custom)

    main_menu = Menu(items=main_menu_items)
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
