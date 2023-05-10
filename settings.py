import json

from constants import *
from logger import Logger


class Settings:
    settings = {}

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

        self.settings_path = os.path.join(APP_DIR, 'settings.json')

        self.logger.log('Fichier de paramètres:', self.settings_path)

        # création du fichier de paramètres s'il n'existe pas
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as file:
                file.write(json.dumps({}))

        self.update()

    def update(self) -> None:
        with open(self.settings_path, 'r') as file:
            self.settings = json.loads(file.read())

    def get(self, key: str) -> str | int | float | bool | None:
        try:
            return self.settings[key]
        except KeyError:
            return None

    def get_all(self) -> dict[str, str | int | float | bool]:
        return self.settings

    def set(self, key: str, value: str | int | float | bool) -> None:
        self.logger.log(f'Sauvegarde du paramètre {key}: {value}')
        self.settings[key] = value
        with open(self.settings_path, 'w') as file:
            json_settings = json.dumps(self.settings)
            file.write(json_settings)
