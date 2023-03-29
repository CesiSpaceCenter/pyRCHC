import os

class Data:
    buffer = bytes()

    def __init__(self, logger) -> None:
        self.logger = logger
        
    def check(self, data : bytes) -> str | dict:
        if data.endswith(b'\r\n'): # les données doivent finir par \r\n (Carriage Return & New Line)
            data = data.replace(b'\r\n', b'')
        else:
            return 'No data terminator'

        try:
            data = data.decode('ascii') # on convertit en chaine de caractère (ASCII)
        except UnicodeDecodeError: # si les caractères non ASCII sont dans les données
            return 'Incorrect encoding'

        data = data.split(',') # toutes les données sont séparées par des virgules
        if len(data) != 8: # il doit avoir exactement 8 éléments de données
            return 'Incorrect data length'
        
        try:
            data = [float(e) for e in data] # on convertit toutes les données en float
        except ValueError: # s'il y a des éléments de données qui ne sont pas des nombres
            return 'Data not numeric'
        
        return data

    def process(self, raw_data : bytes) -> dict | bool:
        data = self.check(raw_data)
        if type(data) == type(''): # si la fonction retourne une chaîne de caractères, alors la vérification n'est pas bonne
            self.logger.log('Data integrity failed:', data, raw_data)
            return False
        
        self.buffer += raw_data

        data = { # on assigne un nom aux données
            'time': data[0],
            'accX': data[1],
            'accY': data[2],
            'accZ': data[3],
            'gyroX': data[4],
            'gyroY': data[5],
            'gyroZ': data[6],
            'temp': data[7]
        }

        return data
    
    def save(self, session) -> None: # on sauvegarde à la fois les données et le log
        if session != None: # ne faire ca que si la session est ouverte
            with open(os.path.join(session.folder, 'data.txt'), 'ab') as f: # fichier data.txt dans le dossier de session
                f.write(self.buffer)
                self.buffer = bytes() # réinitialisation du buffer

        self.logger.save() # en même temps, on sauvegarde les logs