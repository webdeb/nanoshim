from utils import nuke_and_wait, copy_file, relative
import subprocess
p = subprocess.Popen(["make"], cwd="../micropython/ports/rp2")

nuke_and_wait()
print("flash nuked")

p.wait()
print("Program build")


copy_file(relative("hackpwm.uf2"))
print("firmware flashed")
