import uuid
from datetime import datetime

import utils
from constants import *


class Session:
    def __init__(self, main_window, logger) -> None:
        self.main_window = main_window
        self.logger = logger

        self.timer_start = datetime.now()
        self.id = str(uuid.uuid4())
        self.folder = os.path.join(SESSION_DIR, self.id)
        os.mkdir(self.folder)
        self.main_window.sessionButton.setText('Terminer la session')
        self.logger.log('Nouvelle session:', self.id)

        self.main_window.custom_ui.reset()

    def end(self) -> None:
        self.main_window.sessionButton.setText('Ouvrir une session')
        self.main_window.data.save(self)
        self.main_window.session = None
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
