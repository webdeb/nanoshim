from hackpwm import PWMSystem
from .store import store
from hackpwm.programs import ALL_PROGRAMS


def load_systems():
    systems = []
    for (k, s) in dict(store.get('systems')).items():
        label = s.get("title")
        system = PWMSystem(
            title=label,
            programs=[create_program(p) for p in s.get("programs")]
        )
        systems.append(system)

    return systems


def create_program(p):
    id = p.pop("pid")
    ProgramClass = next(filter(lambda p: p.id == id, ALL_PROGRAMS))

    return ProgramClass(**p)


# class PWMSystemLoader():
#     title = None
#     system: PWMSystem
#     programs = []
#     def __init__(self, title, programs) -> None:
#         self.title = title
#         self.programs = programs

#     def start(self):
#         self.system = PWMSystem(self.title, [])
