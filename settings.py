import json

from constants import *
from singleton import Singleton
from logger import Logger


class Settings(metaclass=Singleton):
    settings = {}

    def __init__(self) -> None:
        self.logger = Logger()

        self.settings_path = os.path.join(APP_DIR, 'settings.json')

        self.logger.log('Settings file:', self.settings_path)

        # create the settings file if it does not exists
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as file:
                file.write('{}')  # write empty json into it, or we won't be able to parse it

        self.update()  # load the current settings

    def update(self) -> None:
        with open(self.settings_path, 'r') as file:
            self.settings = json.loads(file.read())

    def __getitem__(self, key: str) -> str | int | float | bool | None:
        return self.settings.get(key)

    def get_all(self) -> dict[str, str | int | float | bool]:
        return self.settings

    def __setitem__(self, key: str, value: str | int | float | bool):
        self.settings[key] = value
        with open(self.settings_path, 'w') as file:
            json_settings = json.dumps(self.settings)
            file.write(json_settings)

        self.logger.log(f'Setting changed: {key}: {value}')
