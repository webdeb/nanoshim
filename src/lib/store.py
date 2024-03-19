import os
import json
import uasyncio as asyncio

class Store:
    is_loading = False
    is_saving_scheduled = False
    has_updates = False
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

        self.has_updates = True

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
            print(path, "Error", self.data)
            raise KeyError("Smth went very bad...")

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
                self.has_updates = False
        except OSError as exc:
            print("Error saving to file.", self.path, exc)


class ChildStore():
    parent_store: Store

    def __init__(self, key, initial_data, check_key):
        self.key = str(key)
        self.check_key = check_key
        self.initial_data = initial_data

    def set_parent(self, store: Store):
        self.parent_store = store
        if (self.initial_data.get(self.check_key) != self.get(self.check_key)):
            self.parent_store.set(self.key, self.initial_data)

    def get(self, key):
        return self.parent_store.get(f"{self.key}.{key}")

    def set(self, key, value):
        return self.parent_store.set(f"{self.key}.{key}", value)

class StoreRegistry():
    _store_paths = []
    _stores = {}

    def get_store(self, path, initial_data):
        if (path not in self._store_paths):
            self._add_store(path, Store(path, initial_data))
        
        return self._stores[path]

    async def start_saver(self):
        self._run = asyncio.create_task(self._saver())

    async def _saver(self):
        while True:
            for p in self._store_paths:
                if (self._stores[p].has_updates):
                    self._stores[p].save()

            await asyncio.sleep(1)
    def _add_store(self, path, store):
        self._stores[path] = store
        self._store_paths.append(path)



Stores = StoreRegistry()
