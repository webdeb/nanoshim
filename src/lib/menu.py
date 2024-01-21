from lib.ui_program import UIListProgram
from lib.autostart import add_to_autostartable


class Menu(UIListProgram):
    def __init__(self, items, title=None):
        self.title = title or "Menu"
        self.items = [self.create_program_item(p) for p in items]

        super().__init__()

    def create_program_item(self, instance):
        if (not isinstance(instance, UIListProgram)):
            instance = instance(on_exit=self.start)
            if (hasattr(instance, "title") and instance.autostartable):
                add_to_autostartable(instance.title, instance)
        elif (isinstance(instance, Menu)):
            self.add_back_button_to_menu_instance(instance)

        return {
            "text": instance.title,
            "handle_button": instance.start
        }

    def add_back_button_to_menu_instance(self, instance):
        instance.items = [{
            "text": "< Back",
            "handle_button": self.start
        }] + instance.items

        instance.set_items_text()
