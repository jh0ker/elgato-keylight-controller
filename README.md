# elgato-keylight-controller

A simple Python program that controls your Elgato Key Lights using hotkeys.

It uses the [elgato](https://github.com/elgato/elgato-python) library to communicate with the lights and [AutoHotkey](https://www.autohotkey.com/) to handle the hotkeys.


## Requirements
- AutoHotkey v2 (https://www.autohotkey.com/)
- `uv` (https://astral.sh/uv/)


## Usage

1. Clone the repository
2. Install the dependencies:
    ```bash
    uv sync
    ```
3. Copy `config.yaml.sample` to `config.yaml` and edit it to your liking
4. Run the program:
    ```bash
    uv run start
    ```
