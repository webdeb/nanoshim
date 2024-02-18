import shutil
import time
import os


def relative(path, f=__file__):
    dir = os.path.dirname(f)
    return os.path.join(dir, path)


nuke_file = relative("flash_nuke.uf2")
pico_dist = "/Volumes/RPI-RP2"


def copy_file(src, dest=pico_dist):
    try:
        shutil.copy(src, os.path.join(
            dest, "firmware.uf2"), follow_symlinks=True)
        print(f"Successfully copied {src} to {dest}")
    except Exception as e:
        print(f"Error copying {src} to {dest}: {e}")


def wait_reconnect(file_path=pico_dist, timeout=10):
    wait_disconnect(file_path, timeout)
    wait_connect(file_path, timeout)


def wait_connect(file_path=pico_dist, timeout=60):
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {file_path} to connect.")
            return False
        time.sleep(1)

    return True


def wait_disconnect(file_path=pico_dist, timeout=10):
    start_time = time.time()
    while os.path.exists(file_path):
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {file_path} to disconnect.")
            return False
        time.sleep(1)


def nuke_and_wait():
    print("Waiting for PICO")
    connected = wait_connect()
    if (connected):
        print("connected successfully")
    else:
        print("No Pico connected")

    copy_file(nuke_file, pico_dist)
    return wait_reconnect(pico_dist)
