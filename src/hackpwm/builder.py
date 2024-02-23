from lib.ui_program import UIListProgram


class PWMSystemBuilder(UIListProgram):
    def __init__(self, on_exit=None):
        super().__init__(on_exit)


"""
Idea is to allow creation of PWM Programs through the MC UI.
"""

"""
{
    "program": PWM,
    "options": {
        "label": {
            "type": "text",
        },
        "pin": {
            "type": "select",
            "options": []
        }
    }
}

{
    "program": PWM_WITH_PIN,
    "options": {
        "label": {
            "type": "text",
        },
        "pin": {
            "type": "select",
            "options": []
        },
        "wait_pin": {
            "type": "select",
            "options": []
        }
    }
}

{
    "program": TRIGGER_45,
    "options": {
        "label": {
            "type": "text",
        }
    }
}

{
    "program": PWM,
    "options": {
        "label": {
            "type": "text",
        },
        "pin": {
            "type": "select",
            "options": []
        }
    }
}


{
    "program": PWM,
    "options": {
        "label": {
            "type": "text",
        },
        "pin": {
            "type": "select",
            "options": []
        }
    }
}

"""
