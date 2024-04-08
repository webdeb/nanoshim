from lib.store import Stores

store = Stores.get_store("/store/autostart.json", {
    "version": 1,
    "title": ""
})

autostartables = {}


def get_autostart_title():
    title = str(store.get("title"))
    if (title in autostartables):
        return title
    return "Menu"


def set_autostart_title(title): store.set("title", title)
def add_to_autostartable(title, instance): autostartables[title] = instance
def get_autostart(): return autostartables[get_autostart_title()]
