from ahk import AHK

from elgato_keylight_controller import controller
from elgato_keylight_controller.config import config, Action

client = AHK(version="v2")


def setup():
    print("Setting up hotkeys...", end="")

    def make_callback(action: Action):
        def _callback():
            controller.do(action)

        return _callback

    for hotkey in config.hotkeys:
        client.add_hotkey(hotkey.key, callback=make_callback(hotkey.action))

    client.start_hotkeys()
    print(" done.")


def teardown():
    print("Tearing down hotkeys...", end="")
    client.stop_hotkeys()
    print(" done.")
