import inspect
from datetime import datetime

from singleton import Singleton
from constants import *


class Logger(metaclass=Singleton):
    def __init__(self) -> None:
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        time = datetime.now().strftime('%d.%m.%Y-%H.%M.%S')
        filename = f'{time}.log'

        self.log_path = os.path.join(LOG_DIR, filename)

        self.file = open(self.log_path, 'a')

        self.log('Logger started')

    def save(self) -> None:
        # to save the content of the file, close it and reopen it
        self.file.close()
        self.file = open(self.log_path, 'a')

    MainWindow = None

    def set_main_window(self, mw) -> None:
        self.MainWindow = mw

    def log(self, *raw_data: str | int | float | bool | list | dict | bytes) -> None:
        # convert everything to string, and clean it
        data = ''
        for element in raw_data:
            data += ' ' + str(element)

        data = data.rstrip()

        if len(data) == 0:  # don't log anything if there is no data
            return

        # get some traceback: filename, line number, time
        stack = inspect.stack()[1]
        filename = os.path.basename(stack.filename)
        lineno = stack.lineno
        time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        line = f'[{filename}:{lineno}] [{time}] {data}'

        # print into stdout
        print(line)

        # write it into the log box
        if self.MainWindow is not None:
            self.MainWindow.handle_log(data)

        # write it into the log file
        self.file.write(line + '\n')
