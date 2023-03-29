import os

#APP_DIR = os.path.join(os.getenv('APPDATA'), 'pyRCHC')
APP_DIR = os.path.realpath('.')

LOG_DIR = os.path.join(APP_DIR, 'logs')

SESSION_DIR = os.path.join(APP_DIR, 'sessions')