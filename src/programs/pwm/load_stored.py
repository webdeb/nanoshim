from hackpwm import PWMSystem
from .store import store

def load_systems():
    systems = []
    for s in store.get('systems'):
        label = s.get("title")
        system = PWMSystem(
            title=label,
            programs_info = s.get("programs")
        )
        systems.append(system)

    return systems

# class PWMSystemLoader():
#     title = None
#     system: PWMSystem
#     programs = []
#     def __init__(self, title, programs) -> None:
#         self.title = title
#         self.programs = programs

#     def start(self):
#         self.system = PWMSystem(self.title, [])
