import uasyncio as asyncio
from program_menu import MainMenu
from program_settings import Settings
from programs.pupapupu.program import Program as PupaPuPu
from programs.sixpwm.program import Program as SixPWM
from programs.twofam.program import Program as TwoFAM


def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def main_menu():
    def open_4p(): return pwm_4p_program.start()
    def open_6pwm(): return pwm_6pwm_program.start()
    def open_menu(): return main_menu_program.start()
    def open_settings(): return settings_program.start()
    def open_2fam(): return twofam.start()

    # run this first, this is the critical part.
    twofam = TwoFAM(on_exit=open_menu)
    pwm_4p_program = PupaPuPu(on_exit=open_menu)
    pwm_6pwm_program = SixPWM(on_exit=open_menu)
    settings_program = Settings(on_exit=open_menu)
    main_menu_program = MainMenu({
        "Settings": open_settings,
        "4P Program": open_4p,
        "6 PWM": open_6pwm,
        "2F AM": open_2fam,
    })

    open_menu()
    # asyncio.create_task(test_ui())


async def main():
    set_global_exception()
    loop = asyncio.get_event_loop()
    loop.create_task(main_menu())
    loop.run_forever()


if __name__ == "__main__":
    print("Starting...")
    try:
        asyncio.run(main())
    except:
        asyncio.new_event_loop()
