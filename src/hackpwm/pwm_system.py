from lib.ui_program import UIListProgram
from lib.store import Stores, ChildStore
from hackpwm.programs import ALL_PROGRAMS
from misc.rgbled import Led
import gc

def first_fit_pio(instructions_per_sm):
    free_instructions = [32, 32]
    sorted_sm = sorted(instructions_per_sm, key=lambda sm: sm[1], reverse=True)
    for (pio_idx, free) in enumerate(free_instructions):
        free_slots = 4
        for next_large in sorted_sm:
            if (free >= next_large[1] and len(next_large) == 2):
                sm_id = abs(free_slots - 4) + (pio_idx * 4)
                next_large.append(sm_id)
                free = free - next_large[1]
                free_slots = free_slots - 1

            if (free == 0 or free_slots == 0):
                break

    return sorted(sorted_sm, key=lambda sm: sm[0])

class PWMSystem(UIListProgram):
    autostartable = True
    running = False
    pwms = {}
    programs = []
    version = 4

    def __init__(self, title, programs_info):
        self.title = title
        self.programs_info = programs_info

    def on_exit(self):
        self.remove()
        self.programs.clear()
        gc.collect()

        self.leave()

    def set_exit(self, on_exit):
        self.leave = on_exit

    def get_items(self):
        items = []
        for program in self.programs:
            items.extend(program.get_fields())
        return items

    def start(self):
        self.load()
        super().start()

    def load(self):
        instructions = []
        programs_store = []
        version = self.version

        # 1. loop load programs data
        for idx, p in enumerate(self.programs_info):
            program = self.create_program(p)
            program_store = ChildStore(
                f"programs.{idx}",
                program.get_store_structure(),
                check_key="pid"
            )
            programs_store.append(program_store)
            instructions.append([idx, program.instructions])
            version += int(program_store.initial_data.get("version", 0))
            self.programs.append(program)

        self.store = Stores.get_store(f"/store/{self.title}.json", {
            "version": version,
            "programs": [p.initial_data for p in programs_store]
        })

        programs_sm = first_fit_pio(instructions)

        # setup machines
        for idx, program in enumerate(self.programs):
            program.setup_store(programs_store[idx])
            program.store.set_parent(self.store)
            program.setup_machine(programs_sm[idx][2])

    def handle_button(self):
        if self.running: return

        self.on_exit()

    def run(self):
        for program in self.programs:
            program.active(1)
        self.running = True
        Led(Led.COLORS.red)

    def stop(self):
        for program in self.programs:
            program.active(0)
        self.running = False
        Led.normal()

    def on_long_press(self):
        if (self.running):
            self.stop()
        else:
            self.run()

    def remove(self):
        for program in self.programs:
            program.remove()

    def create_program(self, p):
        pid = p.get("pid")
        ProgramClass = next(filter(lambda p: p.pid == pid, ALL_PROGRAMS))

        return ProgramClass(**p)
