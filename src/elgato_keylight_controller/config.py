from enum import Enum
from functools import cached_property
from pathlib import Path


import yaml
from pydantic import BaseModel, Field
from elgato import Elgato, State

WORKING_DIR = Path()
CONFIG_FILE = WORKING_DIR / "config.yaml"


class LightConfig(BaseModel):
    name: str | None = None
    ip: str = Field(frozen=True)

    _state: State | None = None

    @property
    def state(self):
        if self._state is None:
            raise ValueError("State is None, call update_state first")

        return self._state

    @state.setter
    def state(self, state: State):
        self._state = state

    @cached_property
    def client(self):
        return Elgato(self.ip)


class Action(str, Enum):
    REFRESH = "refresh"
    SYNC = "sync"
    TOGGLE = "toggle"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    TEMPERATURE_UP = "temperature_up"
    TEMPERATURE_DOWN = "temperature_down"
    STOP = "stop"


class HotkeyConfig(BaseModel):
    key: str
    action: Action


class Config(BaseModel):
    lights: list[LightConfig]
    hotkeys: list[HotkeyConfig]


print(f"Loading config from {CONFIG_FILE.absolute()}...", end="")
config = Config.model_validate(yaml.safe_load(CONFIG_FILE.read_text()))
print(" done.")
