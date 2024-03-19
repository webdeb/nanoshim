from hackpwm.pwm_system import PWMSystem
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
