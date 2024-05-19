import os
from PyQt6.QtCore import QStandardPaths

if bool(os.environ.get('DEBUG', False)):
    APP_DIR = os.path.realpath('.')
else:
    APP_DIR = os.path.join(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppDataLocation), 'pyRCHC')

LOG_DIR = os.path.join(APP_DIR, 'logs')

SESSION_DIR = os.path.join(APP_DIR, 'sessions')
