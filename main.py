from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys

from constants import *
from window import MainWindow
from logger import Logger
from settings import Settings

pg.setConfigOption('background', (0,0,0, 0)) # fond transparent
pg.setConfigOption('antialias', True)

if __name__ == '__main__':
    if not os.path.exists(APP_DIR):
        os.mkdir(APP_DIR)

    if not os.path.exists(SESSION_DIR):
        os.mkdir(SESSION_DIR)

    logger = Logger()
    settings = Settings(logger)

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.init(settings, logger)
    win.show()
    sys.exit(app.exec_())
