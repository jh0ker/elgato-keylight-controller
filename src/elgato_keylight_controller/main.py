from time import sleep

from elgato_keylight_controller import hotkeys, controller


def start():
    controller.start()
    hotkeys.setup()
    controller.do(controller.Action.REFRESH)

    # Wait for Ctrl+C
    try:
        while True:
            sleep(5)
    except (Exception, KeyboardInterrupt, SystemExit):
        pass

    hotkeys.teardown()
    controller.stop()
