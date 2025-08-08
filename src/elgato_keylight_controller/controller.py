import asyncio
from dataclasses import asdict
from typing import Protocol
from threading import Thread, Event

from elgato import State

from elgato_keylight_controller.config import LightConfig, Action, config

BRIGHTNESS_MIN = 2
BRIGHTNESS_MAX = 100
BRIGHTNESS_STEP = 1

TEMPERATURE_MIN = 143
TEMPERATURE_MAX = 344
TEMPERATURE_STEP = -5


_queue: asyncio.Queue[Action]
_loop: asyncio.AbstractEventLoop


def start():
    started = Event()

    async def main():
        global _queue

        _queue = asyncio.Queue()
        started.set()

        while True:
            try:
                stop_received = await process_next()
            except Exception as e:
                print(f"Error: {e}")
                continue

            if stop_received:
                break

        print(" done.")

    def initialize_event_loop():
        global _loop
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        _loop.run_until_complete(main())

    print("Starting controller...", end="")
    t = Thread(target=initialize_event_loop)
    t.start()
    started.wait()
    print(" done.")


def do(action: Action):
    _loop.call_soon_threadsafe(_queue.put_nowait, action)


def stop():
    print("Stopping controller...", end="")
    _loop.call_soon_threadsafe(_queue.put_nowait, Action.STOP)


async def process_next():
    action = await _queue.get()

    if action != Action.STOP:
        print(action)

    match action:
        case Action.STOP:
            await asyncio.gather(*[light.client.close() for light in config.lights])
            _queue.task_done()
            return True

        case Action.SYNC:
            await sync()

        case Action.REFRESH:
            await apply_to_all_lights(update_state)

        case Action.TOGGLE:
            await apply_to_all_lights(toggle_light)

        case Action.BRIGHTNESS_UP:
            await apply_to_all_lights(brightness_up)

        case Action.BRIGHTNESS_DOWN:
            await apply_to_all_lights(brightness_down)

        case Action.TEMPERATURE_UP:
            await apply_to_all_lights(temperature_up)

        case Action.TEMPERATURE_DOWN:
            await apply_to_all_lights(temperature_down)

    _queue.task_done()


class Callback(Protocol):
    async def __call__(self, light: LightConfig): ...


async def apply_to_all_lights(callback: Callback):
    await asyncio.gather(*[callback(light) for light in config.lights])


async def update_state(light: LightConfig):
    light.state = await light.client.state()
    print(f'Updated state for light "{light.name or light.ip}":', light.state)


async def toggle_light(light: LightConfig):
    if light.state is None:
        print(f"Light {light.name} has no state yet")
        return

    light.state.on = not light.state.on
    await light.client.light(on=light.state.on)


def clamp_brightness(brightness: int):
    return max(BRIGHTNESS_MIN, min(BRIGHTNESS_MAX, brightness))


async def brightness_up(light: LightConfig):
    if light.state is None:
        print(f"Light {light.name} has no state yet")
        return

    light.state.brightness = clamp_brightness(light.state.brightness + BRIGHTNESS_STEP)
    await light.client.light(brightness=light.state.brightness)


async def brightness_down(light: LightConfig):
    if light.state is None:
        print(f"Light {light.name} has no state yet")
        return

    light.state.brightness = clamp_brightness(light.state.brightness - BRIGHTNESS_STEP)
    await light.client.light(brightness=light.state.brightness)


def clamp_temperature(temperature: int):
    return max(TEMPERATURE_MIN, min(TEMPERATURE_MAX, temperature))


async def temperature_up(light: LightConfig):
    if light.state is None or light.state.temperature is None:
        print(f"Light {light.name} has no state yet")
        return

    light.state.temperature = clamp_temperature(
        light.state.temperature + TEMPERATURE_STEP
    )
    await light.client.light(temperature=light.state.temperature)


async def temperature_down(light: LightConfig):
    if light.state is None or light.state.temperature is None:
        print(f"Light {light.name} has no state yet")
        return

    light.state.temperature = clamp_temperature(
        light.state.temperature - TEMPERATURE_STEP
    )
    await light.client.light(temperature=light.state.temperature)


async def sync():
    print("Start syncing lights...")
    await update_state(config.lights[0])
    target_state = config.lights[0].state

    async def sync_light(light: LightConfig):
        light.state = State(**asdict(target_state))

        await light.client.light(
            on=light.state.on,
            brightness=light.state.brightness,
            temperature=light.state.temperature,
        )

    print("Applying state to all other lights...")
    await asyncio.gather(*[sync_light(light) for light in config.lights[1:]])

    print("Updating state of all lights...")
    await apply_to_all_lights(update_state)

    print("Syncing lights done.")
