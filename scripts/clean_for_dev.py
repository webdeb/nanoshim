from utils import nuke_and_wait, copy_file, relative

nuke_and_wait()
micropython_distro = relative("./micropython-v1.22.1.uf2")
copy_file(micropython_distro)

print("copied")
