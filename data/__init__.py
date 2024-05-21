import json
import serial as pyserial
import random

from constants import *
from logger import Logger
from session import Session
from data.decoders import decoders
from data.checks import check


class DecodeException(Exception):
    pass


class IncorrectConfigurationException(Exception):
    pass


class Data:
    raw_buffer = bytes()
    buffer = []

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

        self.serial = pyserial.Serial()
        self.serial.baudrate = 9600
        self.serial.timeout = 0.5

        with open(os.path.join(APP_DIR, 'data_config.json'), 'r') as f:
            self.config = json.loads(f.read())

    def process(self, data: list) -> (dict, list):
        config_item_index = 0
        expected_data_count = 0
        out_data = {}
        errors = []

        for item_value in data:
            # fetch the configuration (from data_config.json) of the current data item received
            while True:
                try:  # try to get find the item in the config
                    item_name = list(self.config['items'].keys())[config_item_index]
                    config_item = self.config['items'][item_name]
                    config_item_index += 1
                except Exception as e:  # if an exception is raised, it means the we don't know how to decode the received item data
                    raise IncorrectConfigurationException(f'Incorrect configuration: {e}')

                # if the config element does not have condition, or if that condition is true
                # then we stop the while loop, and we proceed
                if 'if' not in config_item or out_data[config_item['if']['key']] == config_item['if']['value']:
                    expected_data_count += 1
                    break

            # we convert the element to the corresponding python type
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
                # the value is not convertible to this type (eg: trying to convert "abc" to int)
                errors.append({
                    'message': f'Cannot convert {item_value} to {config_item["type"]}',
                    'status_item': 'integrite',
                    'severity': 2
                })

            # item_name is the variable name (eg. accX)
            # item_value is the data received for this variable (eg. 3.78)
            # config_item is the config (contained in data_config.json) for this variable (eg. {'type': 'float', 'checks': [...]}

            # proceed to the data coherence check (minimum, maximum, etc)
            if 'checks' in config_item:
                check_messages = check(item_value, config_item['checks'], item_name)
                if check_messages:
                    for message in check_messages:
                        errors.append({
                            'message': message,
                            'status_item': 'integrite',
                            'severity': 2
                        })

            out_data[item_name] = item_value  # add the value to the list that will be returned
        if len(out_data) != expected_data_count:  # if we got more or less data than expected
            errors.append({
                'message': f'Incorrect data count. Expected {expected_data_count} got {len(out_data)}',
                'status_item': 'integrite',
                'severity': 2
            })
        return out_data, errors

    def fetch(self) -> (dict, list):
        if bool(os.environ.get('DEBUG', False)):  # debug mode, so we don't need to have a serial connection
            raw_data = ''
            raw_data += str(random.randint(0, 50) / 10) + ','  # accX
            raw_data += str(random.randint(0, 50) / 10) + ','  # accY
            raw_data += str(random.randint(0, 50) / 10) + ','  # accZ
            raw_data += str(random.randint(0, 50) / 10) + ','  # gyrX
            raw_data += str(random.randint(0, 50) / 10) + ','  # gyrY
            raw_data += str(random.randint(0, 50) / 10) + ','  # gyrZ
            raw_data += str(random.randint(0, 50) / 10) + ','  # pres
            raw_data += str(random.randint(0, 1000) / 10) + ','  # alt
            raw_data += str(random.randint(0, 50) / 10) + '\n'  # temp
            raw_data = raw_data.encode()
        else:
            raw_data = self.serial.readline()
            self.serial.flush()

        self.raw_buffer += raw_data

        # we decode the raw data
        try:
            decoded_raw = decoders[self.config['format']].decode(raw_data, self.config)
        except UnicodeDecodeError:
            raise DecodeException('Failed to decode')

        # we process the raw data (checks, filters)
        decoded, errors = self.process(decoded_raw)
        self.buffer.append(decoded)
        return decoded, errors

    def save(self, session: Session) -> None:  # save the buffered data and the log
        if session is not None:  # only do that if a session is open
            # raw data, not decoded
            with open(os.path.join(session.folder, 'data_raw.bin'), 'ab') as f:
                f.write(self.raw_buffer)
                self.raw_buffer = bytes()  # reset the buffer

            csv_path = os.path.join(session.folder, 'data.csv')
            # if the csv file does not exist, create it and write the columns names
            if not os.path.exists(csv_path):
                with open(csv_path, 'w') as f:
                    f.write(','.join(self.buffer[0].keys()))

            # write the decoded data into the csv
            with open(csv_path, 'a') as f:
                for line in self.buffer:
                    f.write('\n')
                    f.write(','.join(map(str, line.values())))
                self.buffer = []  # reset the buffer

        self.logger.save()
