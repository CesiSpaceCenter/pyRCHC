import os
import json
import serial
import random

from constants import *
from logger import Logger
from session import Session
from decoders import decoders


class DecodeException(Exception):
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

    def process(self, data: list) -> (dict, list):
        config_item_index = 0
        expected_data_count = 0
        out_data = {}
        errors = []
        
        for item_value in data:
            # on récupère la configuration de l'élément
            while True:
                try:
                    item_name = list(self.config['items'].keys())[config_item_index]
                    config_item = self.config['items'][item_name]
                    config_item_index += 1
                except Exception as e:  # on a pas trouvé l'élément de config
                    raise IncorrectConfigurationException(f'Incorrect configuration: {e}')

                # si l'élément de config actuel n'a pas de condition, ou alors si cette condition est validée
                # alors on arrête le while et on passe à la suite
                if 'if' not in config_item or out_data[config_item['if']['key']] == config_item['if']['value']:
                    expected_data_count += 1
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
                errors.append({
                    'message': f'Cannot convert {item_value} to {config_item["type"]}',
                    'status_item': 'integrite',
                    'severity': 2
                })

            # on effectue toutes les vérifications (minimum, maximum, etc)
            if 'checks' in config_item:
                for check_item in config_item['checks']:
                    error_message = None
                    # dans le cas ou il y a bien une erreur, on définit le message puis on ajoute à la liste
                    if check_item['check'] == 'min_length' and len(item_value) < check_item['value']:
                        error_message = f'{item_name} is not long enough ({len(item_value)} < {check_item["value"]})'

                    elif check_item['check'] == 'max_length' and len(item_value) > check_item['value']:
                        error_message = f'{item_name} is too long ({len(item_value)} > {check_item["value"]})'

                    elif check_item['check'] == 'min' and item_value < check_item['value']:
                        error_message = f'{item_name} is below min ({item_value} < {check_item["value"]})'

                    elif check_item['check'] == 'max' and item_value > check_item['value']:
                        error_message = f'{item_name} is above max ({item_value} > {check_item["value"]})'

                    elif check_item['check'] == 'values_enum' and item_value not in check_item["value"]:
                        error_message = f'{item_name}\'s value is not in defined enum {check_item["value"]}'

                    if error_message is not None:
                        errors.append({
                            'message': error_message,
                            'status_item': 'integrite',
                            'severity': 2
                        })
            out_data[item_name] = item_value
        if len(out_data) != expected_data_count:
            errors.append({
                'message': f'Incorrect data count. Expected {expected_data_count} got {len(out_data)}',
                'status_item': 'integrite',
                'severity': 2
            })
        return out_data, errors

    def fetch(self) -> (dict, list):
        raw_data = self.serial.readline()
        self.serial.flush()

        """raw_data = '0,'  # pt
        raw_data += str(random.randint(0, 50) / 10) + ','  # accX
        raw_data += str(random.randint(0, 50) / 10) + ','  # accY
        raw_data += str(random.randint(0, 50) / 10) + ','  # accZ
        raw_data += str(random.randint(0, 50) / 10) + ','  # gyrX
        raw_data += str(random.randint(0, 50) / 10) + ','  # gyrY
        raw_data += str(random.randint(0, 50) / 10) + ','  # gyrZ
        raw_data += str(random.randint(0, 50) / 10) + ','  # pres
        raw_data += str(random.randint(0, 1000) / 10) + '\n'  # temp
        raw_data = raw_data.encode()"""

        self.raw_buffer += raw_data

        # on décode les données brutes
        try:
            decoded_raw = decoders[self.config['format']].decode(raw_data, self.config)
        except UnicodeDecodeError:
            raise DecodeException('Failed to decode')

        # on applique les vérifications, les filtres
        decoded, errors = self.process(decoded_raw)
        self.buffer.append(decoded)
        return decoded, errors

    def save(self, session: Session) -> None:  # on sauvegarde à la fois les données et le log
        if session is not None:  # ne faire ça que si la session est ouverte
            # fichier data_raw.bin dans le dossier de session
            with open(os.path.join(session.folder, 'data_raw.bin'), 'ab') as f:
                f.write(self.raw_buffer)
                self.raw_buffer = bytes()  # réinitialisation du buffer

            csv_path = os.path.join(session.folder, 'data.csv')
            # si le dossier data.csv n'existe pas encore, on écrit la première ligne (noms des colonnes)
            if not os.path.exists(csv_path):
                with open(csv_path, 'w') as f:
                    f.write(','.join(self.buffer[0].keys()))

            # on écrit les données du buffer dans data.csv
            with open(csv_path, 'a') as f:
                for line in self.buffer:
                    f.write('\n')
                    f.write(','.join( [str(val) for val in line.values()] ))
                self.buffer = []  # réinitialisation du buffer

        self.logger.save()  # en même temps, on sauvegarde les logs
