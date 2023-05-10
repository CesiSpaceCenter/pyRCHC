import os

from session import Session
from logger import Logger

class IntegrityCheckException(Exception):
    pass


class ConnectionTimeoutException(Exception):
    pass


class Data:
    buffer = bytes()

    def __init__(self, logger : Logger) -> None:
        self.logger = logger
        
    def check(self, data_bytes : bytes) -> list[float]:
        if len(data_bytes) == 0: # aucune données reçus
            raise IntegrityCheckException('Empty data packet')

        if data_bytes.endswith(b'\r\n'): # les données doivent finir par \r\n (Carriage Return & New Line)
            data_bytes = data_bytes.replace(b'\r\n', b'')
        else:
            raise IntegrityCheckException('No data terminator')

        try:
            data_str = data_bytes.decode('ascii') # on convertit en chaine de caractère (ASCII)
        except UnicodeDecodeError: # si les caractères non ASCII sont dans les données
            raise IntegrityCheckException('Incorrect encoding')

        data_list = data_str.split(',') # toutes les données sont séparées par des virgules
        if len(data_list) != 11: # il doit avoir exactement 8 éléments de données
            raise IntegrityCheckException('Incorrect data length')
        
        try:
            data_list = [float(e) for e in data_list] # on convertit toutes les données en float
        except ValueError: # s'il y a des éléments de données qui ne sont pas des nombres
            raise IntegrityCheckException('Data not numeric')
        
        return data_list

    last_packet = 0

    def process(self, raw_data : bytes) -> dict[str, float]:
        data = self.check(raw_data)
        
        self.buffer += raw_data

        data = { # on assigne un nom aux données
            'time': data[0],
            'state': data[1],
            'accX': data[2],
            'accY': data[3],
            'accZ': data[4],
            'gyroX': data[5],
            'gyroY': data[6],
            'gyroZ': data[7],
            'temp': data[8],
            'leftSpeed': data[9],
            'rightSpeed': data[10]
        }

        return data
    
    def save(self, session: Session) -> None: # on sauvegarde à la fois les données et le log
        if session != None: # ne faire ca que si la session est ouverte
            with open(os.path.join(session.folder, 'data.txt'), 'ab') as f: # fichier data.txt dans le dossier de session
                f.write(self.buffer)
                self.buffer = bytes() # réinitialisation du buffer

        self.logger.save() # en même temps, on sauvegarde les logs