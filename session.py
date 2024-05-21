from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import utils
from constants import *
from logger import Logger
if TYPE_CHECKING:
    from window import MainWindow


class Session:
    def __init__(self, window: MainWindow) -> None:
        self.window = window
        self.logger = Logger()

        self.timer_start = datetime.now()

        # create the session folder
        self.id = str(uuid.uuid4())
        self.folder = os.path.join(SESSION_DIR, self.id)
        os.mkdir(self.folder)

        self.window.sessionButton.setText('End session')
        self.logger.log('New session:', self.id)

        self.window.custom_ui.reset()  # reset the ui elements (graphs, etc)

    def end(self) -> None:
        self.window.sessionButton.setText('Open a session')
        self.window.data.save(self)
        self.window.session = None
        folder_size = utils.get_dir_size(self.folder)

        # log & save some metadata
        self.logger.log(f'Session ended: {self.id}')
        self.logger.log(f'  Started on {self.timer_start}')
        self.logger.log(f'  Total size: {folder_size}o')
        with open(os.path.join(self.folder, 'info.txt'), 'w') as f:
            f.writelines([
                f'id: {self.id}\n',
                f'start: {self.timer_start.timestamp()}\n',
                f'end: {datetime.now().timestamp()}\n',
                f'size: {folder_size}'
            ])
