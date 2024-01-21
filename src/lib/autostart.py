from lib.simple_json_store import Store

store = Store("/store/autostart.json", {
    "version": 1,
    "title": ""
})

autostart_program = None
autostartable = []

prev_autostart_title = store.get("title")


def add_to_autostartable(instance, title):
    autostartable.append((instance, title))
    if (prev_autostart_title == title):
        autostart(instance)


def autostart(p):
    global autostart_program
    autostart_program = p


def get_autostart():
    global autostart_program
    return autostart_program
