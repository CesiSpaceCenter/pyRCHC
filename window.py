import re
import subprocess
import time
from datetime import datetime

import serial
import serial.serialutil
import serial.tools.list_ports
from PyQt6 import QtWidgets

import ui
import utils
from constants import *
from data import Data
from logger import Logger
from session import Session
from settings import Settings


class MainWindow(QtWidgets.QMainWindow, ui.base_ui.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

    logger = None
    settings = None
    session = None
    data = None
    serial = None

    # fonction séparée pour pouvoir passer les args (non autorisé par la classe QMainWindow sinon)
    def init(self, settings: Settings, logger: Logger) -> None:
        self.settings = settings
        self.logger = logger

        self.logger.log('Création de la fenêtre')

        self.setupUi(self)  # load the base ui
        # load the custom ui
        self.custom_ui = ui.Ui(self)

        with open('style.css', 'r') as style_file:
            self.setStyleSheet(style_file.read())

        self.show()

        self.logger.setMainWindow(self)

        self.serial = serial.Serial()
        self.serial.baudrate = 9600
        self.serial.timeout = 0.5

        self.data = Data(self.logger, self.serial)

        self.sessionButton.clicked.connect(self.session_button)

        self.update_serial_list()
        self.serialComboBox.activated.connect(self.handle_serial_combobox)

        # timer pour l'horloge
        self.update_clock()
        utils.init_qtimer(self, 1000, self.update_clock)

        # timer pour le timer (?)
        utils.init_qtimer(self, 10, self.update_timer)

        # timer principal pour la mise à jour des données
        utils.init_qtimer(self, 50, self.update)

        # timer d'écriture des données reçues sur le disque dur
        # on n'exécute la fonction save que si la session est ouverte
        utils.init_qtimer(self, 5000, lambda: self.data.save(self.session) if self.session is not None else None)

    def handle_log(self, line: str) -> None:
        last_line = self.logTextEdit.toPlainText().split('\n')[-1]  # on récupère la dernière ligne
        if last_line.startswith(line):  # si la dernière ligne a le même début que la ligne que l'on veut ajouter
            num = re.findall(r'\d+', last_line.replace(line, ''))  # on cherche le numéro dans la fin de la dernière ligne
            if not num:  # s'il n'y en a pas
                # cela signifie que c'était la première ligne
                # on rajoute donc le suffixe pour indiquer que la ligne se répète
                self.logTextEdit.setPlainText(self.logTextEdit.toPlainText() + ' (x2)')  # ici on évite d'utiliser appendPlainText(), car il ajoute un \n avant
            else:  # s'il y en a
                # cela signifie que la dernière ligne était déjà répétée
                num = int(num[0]) + 1  # on ajoute 1 au nombre de répétitions
                # on prend le texte, on enlève le nombre de répétitions de la ligne précédente
                # puis on ajoute le nouveau
                self.logTextEdit.setPlainText(' '.join(self.logTextEdit.toPlainText().split(' ')[:-1]) + f' (x{num})')
        else:  # si c'est une nouvelle ligne, on l'ajoute juste à la suite
            self.logTextEdit.appendPlainText(line)

        self.logTextEdit.verticalScrollBar().setValue(self.logTextEdit.verticalScrollBar().maximum())  #  on scroll à la fin

    def session_button(self) -> None:
        if self.session is None:  # session fermée, on doit alors la créer
            self.session = Session(self, self.logger)
        else:  # session déjà ouverte, on doit alors la fermer
            self.session.end()

    def open_session_folder(self) -> None:
        if self.session is not None:
            subprocess.Popen(['open', self.session.folder])
        else:
            subprocess.Popen(['open', SESSION_DIR])

    def update_clock(self) -> None:
        date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.clockLabel.setText(date_time)

    serial_list = None

    def update_timer(self) -> None:
        if self.session is not None:
            date_time = round((datetime.now() - self.session.timer_start).total_seconds(), 1)
            self.timerLabel.setText('t+' + str(date_time) + 's')
        else:
            self.timerLabel.setText('t+0s')

    def handle_serial_combobox(self, device_index: int) -> None:
        combobox_items = [self.serialComboBox.itemText(i) for i in range(self.serialComboBox.count())]
        selected_item = combobox_items[device_index]

        if selected_item == 'Actualiser':
            pass  # dans tous les cas, la liste est actualisée à la fin de la fonction

        elif selected_item == 'Déconnecter':  # dernier élément du combobox, élément "Déconnecter"
            if self.serial.is_open:
                self.logger.log(f'Déconnexion du port série {self.serial.port}')
                self.serial.close()
        else:
            if self.serial.is_open:  # si la connexion est déjà ouverte
                self.serial.close()  # on la ferme
            self.serial.port = self.serial_list[
                device_index].device  # on prend le port série sélectionné dans le combobox
            self.logger.log(f'Connexion au port série {self.serial.port}')
            self.serial.open()

        self.update_serial_list()

    def update_serial_list(self) -> None:
        self.serialComboBox.clear()  # on enlève tous les élements du combobox
        self.serial_list = serial.tools.list_ports.comports()
        for device in self.serial_list:
            self.serialComboBox.addItem(
                device.device + ' : ' + device.description)  # on ajoute le port à la liste (port + nom)
        self.serialComboBox.addItem('Actualiser')
        self.serialComboBox.addItem('Déconnecter')

    last_successful_data = 0
    status = {}
    
    def update(self) -> None:
        self.update_data()
        self.update_status()

    def update_data(self) -> None:
        self.status = {
            'connexion': 0,
            'integrite': 0,
            'recepteur': 0,
            'timeout': 0
        }

        if time.time() - self.last_successful_data > 4:  # pas de données valides pour plus de 4s
            self.status['connexion'] = 1
            self.status['timeout'] = 1

        if not self.serial.is_open and False:
            self.status['connexion'] = 1
            self.status['recepteur'] = 2
            return

        try:
            data, errors = self.data.fetch()
            self.status['recepteur'] = 4
        except serial.serialutil.SerialException:
            self.logger.log('Erreur: communication avec le récepteur impossible')
            self.status['connexion'] = 1
            self.status['recepteur'] = 1
            return

        if errors:
            print(errors)
            for error in errors:
                self.logger.log(f'Erreur: {error["message"]}')
                self.status[error['status_item']] = error['severity']

        self.last_successful_data = time.time()

        self.custom_ui.update_data(data)

    def update_status(self) -> None:
        for item in self.status:
            if self.status[item] == 0:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #bbb')  # gris
            elif self.status[item] == 1:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: red')  # rouge
            elif self.status[item] == 2:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #f1c40f')  # orange
            elif self.status[item] == 3:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #3498db')  # bleu
            elif self.status[item] == 4:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #27ae60')  # vert
