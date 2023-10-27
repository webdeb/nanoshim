import os
import json
import uasyncio as asyncio


class Store:
    is_loading = False
    is_saving_scheduled = False
    data = None

    def __init__(self, path, inital_data):
        self.path = path
        self.inital_data = inital_data
        self.dir = "/".join(path.split("/")[0:-1])
        self.file_name = path.split("/")[-1]

        self.ensure_file()
        self.load()
        self.ensure_version()

    """
    Ensure the file exists and is initialised
    """

    def ensure_file(self):
        for path_part in self.dir.split("/"):
            if (path_part and path_part not in os.listdir()):
                os.mkdir(path_part)
            os.chdir(path_part)

        os.chdir("/")

        if (self.file_name not in os.listdir(self.dir)):
            self.save(self.inital_data)  # Initialy it will save

    def ensure_version(self):
        if (self.data.get("version", None) != self.inital_data.get("version", None)):
            self.save(self.inital_data)
            self.load()

    def set(self, path, value):
        path_parts = path.split(".")
        obj = self.data

        for part in path_parts[:-1]:
            if part.isdigit():
                obj = obj[int(part)]
            else:
                obj = obj[part]

        if path_parts[-1].isdigit():
            obj[int(path_parts[-1])] = value
        else:
            obj[path_parts[-1]] = value

        if (self.is_saving_scheduled == False):
            self.is_saving_scheduled = True
            loop = asyncio.get_event_loop()
            loop.create_task(self.save_async())

    def get(self, path, data=None):
        try:
            if (data):
                obj = data
            else:
                obj = self.data

            path_parts = path.split(".")

            for part in path_parts:
                if part.isdigit():
                    obj = obj[int(part)]
                else:
                    obj = obj[part]
            return obj
        except:
            print(path)
            return 0

    def load(self):
        self.is_loading = True
        with open(self.path) as f:
            self.data = json.loads(f.read())
            f.close()

        self.is_loading = False

    def save(self, data=None):
        if data == None:
            data = self.data

        try:
            with open(str(self.path), "w") as f:
                f.write(json.dumps(data))
                f.close()
        except OSError as exc:
            print("Error saving to file.", self.path)

        # clean()
        self.is_saving_scheduled = False

    async def save_async(self):
        await asyncio.sleep_ms(100)
        self.save()
