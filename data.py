import os
import json
import serial
import random

from constants import *
from logger import Logger
from session import Session
from decoders import decoders


class DataCheckException(Exception):
    pass

class DecodeException(Exception):
    pass

class ConnectionTimeoutException(Exception):
    pass

class IncorrectConfigurationException(Exception):
    pass


class Data:
    raw_buffer = bytes()
    buffer = []

    def __init__(self, logger: Logger, serial: serial.Serial) -> None:
        self.logger = logger
        self.serial = serial
        with open(os.path.join(APP_DIR, 'data_config.json'), 'r') as f:
            self.config = json.loads(f.read())

    def process(self, data: list) -> dict:
        config_item_index = 0
        out_data = {}

        for item_value in data:
            # on récupère la configuration de l'élément
            while True:
                try:
                    item_name = list(self.config['items'])[config_item_index]
                    config_item = self.config['items'][item_name]
                    config_item_index += 1
                except Exception as e:
                    raise IncorrectConfigurationException(e)

                # si l'élément de config actuel n'a pas de condition, ou alors si cette condition est validée
                # alors on arrête la boucle
                if 'if' not in config_item or out_data[config_item['if']['key']] == config_item['if']['value']:
                    break

            # on convertit l'élément au type correspondant
            item_type = {
                'string': str,
                'int8': int,
                'uint8': int,
                'int16': int,
                'uint16': int,
                'int32': int,
                'uint32': int,
                'float': float,
                'double': float
            }[config_item['type']]
            try:
                item_value = item_type(item_value)
            except ValueError:
                raise DecodeException(f'Cannot convert {item_value} to {config_item["type"]}')

            # on effectue toutes les vérifications (minimum, maximum, etc)
            for check_item in config_item['checks']:
                # on initialise l'erreur
                e = DataCheckException()
                e.severity = check_item['severity']
                e.status_item = check_item['status_item']

                # dans le cas ou il y a bien une erreur, on définit le message puis on raise
                if check_item['check'] == 'min_length' and len(item_value) < check_item['value']:
                    e.args = (f'{item_name} is not long enough ({len(item_value)} < {check_item["value"]})',)
                    raise e

                elif check_item['check'] == 'max_length' and len(item_value) > check_item['value']:
                    e.args = (f'{item_name} is too long ({len(item_value)} > {check_item["value"]})',)
                    raise e

                elif check_item['check'] == 'min' and item_value < check_item['value']:
                    e.args = (f'{item_name} is below min ({item_value} < {check_item["value"]})',)
                    raise e

                elif check_item['check'] == 'max' and item_value > check_item['value']:
                    e.args = (f'{item_name} is above max ({item_value} > {check_item["value"]})',)
                    raise e

                elif check_item['check'] == 'values_enum' and item_value not in check_item["value"]:
                    e.args = (f'{item_name}\'s value is not in defined enum {check_item["value"]}',)
                    raise e

            out_data[item_name] = item_value
        return out_data

    def fetch(self) -> dict:
        #raw_data = self.serial.readline()

        if random.randint(0,6) == 1:
            raw_data = '1,'  # pt
            raw_data += 'coucou\n'  # alt
        else:
            raw_data = '0,'  # pt
            raw_data += str(random.randint(0, 50) / 10) + ','  # accX
            raw_data += str(random.randint(0, 50) / 10) + ','  # accY
            raw_data += str(random.randint(0, 50) / 10) + ','  # accZ
            raw_data += str(random.randint(0, 50) / 10) + ','  # vitX
            raw_data += str(random.randint(0, 50) / 10) + ','  # vitY
            raw_data += str(random.randint(0, 50) / 10) + ','  # vitZ
            raw_data += str(random.randint(0, 1000) / 10) + '\n'  # alt

        raw_data = raw_data.encode()
        self.raw_buffer += raw_data
        raw_data = raw_data.replace(b'\n', b'')


        # on décode les données brutes
        try:
            decoded_raw = decoders[self.config['format']].decode(raw_data, self.config)
        except UnicodeDecodeError:
            raise DecodeException('Failed to decode')

        # on applique les vérifications, les filtres
        decoded = self.process(decoded_raw)
        self.buffer += decoded
        return decoded


    def save(self, session: Session) -> None:  # on sauvegarde à la fois les données et le log
        if session is not None:  # ne faire ça que si la session est ouverte
            # fichier data_raw.bin dans le dossier de session
            with open(os.path.join(session.folder, 'data_raw.bin'), 'ab') as f:
                f.write(self.raw_buffer)
                self.raw_buffer = bytes()  # réinitialisation du buffer

            # fichier data.csv dans le dossier de session
            with open(os.path.join(session.folder, 'data.csv'), 'a') as f:
                for line in self.buffer:
                    f.write(','.join(line))
                self.buffer = bytes()  # réinitialisation du buffer

        self.logger.save()  # en même temps, on sauvegarde les logs
