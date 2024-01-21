import os

try:
    programs = []
    for f in os.listdir('/plugins'):
        if (f.endswith("_program.py")):
            print(f)
            programs.append(__import__(
                f"/plugins/{f[0:-3]}", None, None, ["Program"]).Program)
            print(programs)
except ImportError as e:
    print("Error:", e)
