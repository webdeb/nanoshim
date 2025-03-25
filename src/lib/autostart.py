from lib.store import Stores

last = "Last"
store = Stores.get_store("/store/autostart.json", {
    "version": 1,
    "title": "",
    "last": None
})

autostartables = {}


def get_autostart_title():
    title = str(store.get("title"))
    if (title in autostartables): return title
    if (title == last): return last
    return "Menu"


def set_autostart_title(title): store.set("title", title)
def add_to_autostartable(title, instance): autostartables[title] = instance
def get_autostart(): 
    title = get_autostart_title()
    if (title == last):
        title = str(store.get('last'))
    
    return autostartables[title]
