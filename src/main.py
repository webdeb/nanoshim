import uasyncio as asyncio
from lib.user_inputs import create_inputs
from main_menu import create_main_menu
from lib.store import Stores


def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def start_app():
    await Stores.start_saver()
    await create_inputs()
    await create_main_menu()

async def main():
    set_global_exception()
    loop = asyncio.get_event_loop()
    loop.create_task(start_app())
    loop.run_forever()


def start():
    print("Starting...")
    try:
        asyncio.run(main())
    except:
        print("Started new event loop")
        asyncio.new_event_loop()

if __name__ == "__main__":
    start()
