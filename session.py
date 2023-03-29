import uuid
import os
from datetime import datetime

from constants import *
import utils

class Session:
    def __init__(self, MainWindow, logger) -> None:
        self.MainWindow = MainWindow
        self.logger = logger

        self.timer_start = datetime.now()
        self.id = str(uuid.uuid4())
        self.MainWindow.sessionLabel.setText(self.id)
        self.folder = os.path.join(SESSION_DIR, self.id)
        os.mkdir(self.folder)
        self.MainWindow.sessionButton.setText('Terminer la session')
        self.logger.log('Nouvelle session:', self.id)

    def end(self) -> None:
        for i in self.MainWindow.graph_data:
            self.MainWindow.graph_data[i].reset() # réinitialisation de tout les graphiques
        self.MainWindow.sessionLabel.setText('Aucune session en cours')
        self.MainWindow.sessionButton.setText('Ouvrir une session')
        self.MainWindow.data.save(self)
        self.MainWindow.session = None
        folder_size = utils.get_dir_size(self.folder)
        self.logger.log(f'Session {self.id} terminée')
        self.logger.log(f'  Débutée à {self.timer_start}')
        self.logger.log(f'  Taille totale: {folder_size}o')
        with open(os.path.join(self.folder, 'info.txt'), 'w') as f:
            f.writelines([
                f'id: {self.id}\n',
                f'start: {self.timer_start.timestamp()}\n',
                f'end: {datetime.now().timestamp()}\n',
                f'size: {folder_size}'
            ])