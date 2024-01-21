from lib.simple_json_store import Store

store = Store("/store/autostart.json", {
    "version": 1,
    "title": ""
})

autostart_program = None
autostartable = []


def get_autostart_title():
    return store.get("title")


def set_autostart_title(title):
    store.set("title", title)


def add_to_autostartable(title, instance):
    autostartable.append(title)
    if (get_autostart_title() == title):
        autostart(instance)


def autostart(p):
    global autostart_program
    autostart_program = p


def get_autostart():
    global autostart_program
    return autostart_program
