import inspect
import os
import sys
from datetime import datetime

from constants import *

class Logger:
    def __init__(self) -> None:
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        time = datetime.now().strftime('%d.%m.%Y-%H.%M.%S')
        filename = f'{time}.log'
            
        self.log_path = os.path.join(LOG_DIR, filename)
        self.stdout = sys.stdout

        self.secondary_action = lambda line: 0

        self.file = open(self.log_path, 'a')

        self.log('Démarrage du logger')

    def save(self) -> None:
        # pour sauvegarder, on ferme puis on réouvre le fichier
        self.file.close()
        self.file = open(self.log_path, 'a')
        
    MainWindow = None
    def setMainWindow(self, mw) -> None:
        self.MainWindow = mw

    def log(self, *raw_data : str | int | float | bool | list | dict | bytes) -> None:
        # on converti tout en string, et on nettoie
        data = ''
        for element in raw_data:
            data += ' ' + str(element) 
        data = data.rstrip()
        if len(data) == 0:
            return
        # on récupère quelques infos: le fichier, la ligne, le temps
        stack = inspect.stack()[1]
        filename = os.path.basename(stack.filename)
        lineno = stack.lineno
        time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        line = f'[{filename}:{lineno}] [{time}] {data}'
        # on print dans la console, on appelle la fonction handle_log pour quelques actions spéciales et on écrit dans le fichier
        print(line)
        if self.MainWindow != None:
            self.MainWindow.handle_log(data)
        self.file.write(line + '\n')

    def close(self) -> None:
        self.file.close()