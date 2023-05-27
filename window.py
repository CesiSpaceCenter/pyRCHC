import math
import subprocess
import time
from datetime import datetime

import serial
import serial.serialutil
import serial.tools.list_ports
from PyQt5 import QtWidgets, uic

import utils
from constants import *
from data import Data, IntegrityCheckException
from graph import GraphData
from logger import Logger
from session import Session
from settings import Settings


class MainWindow(QtWidgets.QMainWindow):
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

        uic.loadUi('rchc.ui', self)
        self.show()
        self.init_graph()

        self.logger.setMainWindow(self)

        self.serial = serial.Serial()
        self.serial.baudrate = 9600
        self.serial.timeout = 0.5

        self.data = Data(self.logger)

        self.sessionButton.clicked.connect(self.session_button)
        self.sessionLabel.mousePressEvent = lambda e: self.open_session_folder()

        self.resetGyroButton.clicked.connect(lambda: self.send_command(0))
        self.incSpeedButton.clicked.connect(lambda: self.send_command(1))
        self.decSpeedButton.clicked.connect(lambda: self.send_command(2))
        self.startButton.clicked.connect(lambda: self.send_command(3))
        self.stopButton.clicked.connect(lambda: self.send_command(4))

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

    def send_command(self, command: int) -> None:
        if self.serial.is_open:
            command_ascii = bytes(str(command), 'utf-8')
            self.serial.write(command_ascii)
            self.logger.log(f'Commande {command} envoyée')

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

    graph_data = {}

    def init_graph(self) -> None:
        self.accGraph.addLegend()
        self.gyroGraph.addLegend()
        self.motorGraph.addLegend()

        self.graph_data['temp'] = GraphData(self.tempGraph, 'Temperature', (255, 0, 0))
        self.graph_data['accX'] = GraphData(self.accGraph, 'x', (255, 0, 0))
        self.graph_data['accY'] = GraphData(self.accGraph, 'y', (0, 255, 0))
        self.graph_data['accZ'] = GraphData(self.accGraph, 'z', (0, 0, 255))
        self.graph_data['gyroX'] = GraphData(self.gyroGraph, 'x', (255, 0, 0))
        self.graph_data['gyroY'] = GraphData(self.gyroGraph, 'y', (0, 255, 0))
        self.graph_data['gyroZ'] = GraphData(self.gyroGraph, 'z', (0, 0, 255))

        self.graph_data['leftSpeed'] = GraphData(self.motorGraph, 'left', (255, 0, 0))
        self.graph_data['rightSpeed'] = GraphData(self.motorGraph, 'right', (0, 0, 255))

    status = {}
    last_successful_data = 0

    def update(self) -> None:
        self.update_data()
        self.update_status()

    def update_data(self) -> None:
        self.status = {
            'connexion': 0,
            'integrite': 0,
            'recepteur': 0,
            'timeout': 0,

            'motors': 0,
            'motorL': 0,
            'motorR': 0,

            'sensors': 0,
            'ir': 0,
            'acc': 0
        }

        if not self.serial.is_open:
            self.status['connexion'] = 1
            self.status['recepteur'] = 2
            return

        if time.time() - self.last_successful_data > 4:  # pas de données valides pour plus de 4s
            self.status['connexion'] = 1
            self.status['timeout'] = 1

        try:
            raw_data = self.serial.readline()
            self.status['recepteur'] = 4
        except serial.serialutil.SerialException:
            self.logger.log('Erreur: communication avec le récepteur impossible')
            self.status['connexion'] = 1
            self.status['recepteur'] = 1
            return

        if raw_data.decode().split(',')[0] == 'msg':
            self.telemetryTextEdit.appendPlainText(raw_data.decode().split(',')[1].replace('\r\n', ''))
            return

        try:
            data = self.data.process(raw_data)
            self.status['connexion'] = 4
            self.status['integrite'] = 4
        except IntegrityCheckException as err:
            self.logger.log('Vérification des données échouée:', str(err), raw_data)
            self.status['connexion'] = 1
            self.status['integrite'] = 1
            return

        if data['leftSpeed'] > 0:
            self.status['motorL'] = 4

        if data['rightSpeed'] > 0:
            self.status['motorR'] = 4

        self.last_successful_data = time.time()

        self.graph_data['temp'].append(data['temp'])
        self.graph_data['accX'].append(data['accX'])
        self.graph_data['accY'].append(data['accY'])
        self.graph_data['accZ'].append(data['accZ'])
        self.graph_data['gyroX'].append(data['gyroX'])
        self.graph_data['gyroY'].append(data['gyroY'])
        self.graph_data['gyroZ'].append(data['gyroZ'])

        self.graph_data['leftSpeed'].append(data['leftSpeed'])
        self.graph_data['rightSpeed'].append(data['rightSpeed'])

        if data['state'] == 0:
            self.statusLabel_global.setText('READY')
        elif data['state'] == 1:
            self.statusLabel_global.setText('FORWARD')
        elif data['state'] == 2:
            self.statusLabel_global.setText('TURN')
        elif data['state'] == -1:
            self.statusLabel_global.setText('INIT')
        else:
            self.statusLabel_global.setText('UNKNOWN')

    def update_status(self) -> None:
        for item in self.status:
            if self.status[item] == 0:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #363636')  # gris
            elif self.status[item] == 1:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: red')  # rouge
            elif self.status[item] == 2:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #f1c40f')  # orange
            elif self.status[item] == 3:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #3498db')  # bleu
            elif self.status[item] == 4:
                self.__dict__[f'statusLabel_{item}'].setStyleSheet('background-color: #27ae60')  # vert
