import os
import json
import micropython

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

  def ensure_file(self):
    for path_part in self.dir.split("/"):
      if (path_part not in os.listdir()):
        os.mkdir(path_part)
      os.chdir(path_part)

    os.chdir("/")

    if (self.file_name not in os.listdir(self.dir)):
      self.save(self.inital_data) # Initialy it will save

  def load(self):
    self.is_loading = True
    f = open(self.path)
    self.data = json.loads(f.read())
    f.close()
    self.is_loading = False

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

    self.save()

  def get(self, path, data=None):
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

  def save(self, data=None):
    if data == None:
      data = self.data

    self.is_saving_scheduled = False
    f = open(self.path, "w")
    f.write(json.dumps(data))
    f.close()
