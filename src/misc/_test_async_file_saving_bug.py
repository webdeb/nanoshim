# Probably because of relaive path...

def test_files_async():
    data = {}

    async def write(i):
        try:
            data["i"] = i
            f = open("/test.json", "w")
            f.write(json.dumps(data))
            f.close()
        except:
            print("Error on iteration:", i)

    async def infinite_loop():
        while True:
            await asyncio.sleep_ms(300)

    async def write_file():

        for i in range(1000):
            loop = asyncio.get_event_loop()
            loop.create_task(write(i))
            await asyncio.sleep_ms(10)

    async def start_test():
        set_global_exception()
        loop = asyncio.get_event_loop()
        loop.create_task(infinite_loop())
        loop.create_task(write_file())
        loop.run_forever()

    asyncio.run(start_test())
