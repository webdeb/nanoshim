from lib.ui_program import UIListProgram
from lib.store import Store, ChildStore
from .programs import BasePIOControl
from misc.rgbled import Led


def first_fit_pio(instructions_per_sm):
    print(instructions_per_sm)

    free_instructions = [32, 32]
    sorted_sm = sorted(instructions_per_sm,
                       key=lambda sm: sm[1],
                       reverse=True
                       )

    total = len(sorted_sm) - 1  # just adjust here for comparison.
    for (pio_idx, free) in enumerate(free_instructions):
        free_slots = 4
        for (sm_idx, next_large) in enumerate(sorted_sm):
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

    # store
    version = 3

    def __init__(self, title, programs: list[BasePIOControl]):
        self.title = title
        self.programs = programs  # get text items

    def get_items(self):
        items = []
        for program in self.programs:
            items.extend(program.get_fields())
        return items

    def start(self):
        instructions = []
        programs_store = []
        version = 0

        for idx, program in enumerate(self.programs):
            program.setup_store(ChildStore(
                self.store, f"programs.{idx}", program.store_structure))
            instructions.append([idx, program.instructions])

        self.store = Store(f"/store/{self.title}.json", {"version": self.version,
                           "programs": [dict(p.store_structure, **p.extend_store_structure) for p in self.programs]})

        programs_sm = first_fit_pio(instructions)
        for idx, program in enumerate(self.programs):
            program.setup_machine(programs_sm[idx][2])

        super().start()

    def handle_button(self):
        self.stop_and_remove()  # -> stop and remove programs
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

    def stop_and_remove(self):
        self.stop()
        for program in self.programs:
            program.stop_and_remove()
