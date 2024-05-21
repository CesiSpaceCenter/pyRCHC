import sys
import signal

import pyqtgraph as pg
from PyQt6 import QtWidgets

from constants import *
from window import MainWindow

signal.signal(signal.SIGINT, signal.SIG_DFL)  # allows to quit on KeyboardInterrupt

pg.setConfigOption('background', (0, 0, 0, 0))  # transparent background
pg.setConfigOption('antialias', True)

if __name__ == '__main__':
    if not os.path.exists(APP_DIR):
        os.mkdir(APP_DIR)

    if not os.path.exists(SESSION_DIR):
        os.mkdir(SESSION_DIR)

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.init()
    win.show()
    sys.exit(app.exec())
