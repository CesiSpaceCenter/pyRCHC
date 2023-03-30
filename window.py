from PyQt5 import QtWidgets, QtCore, uic
import serial.tools.list_ports
from datetime import datetime
import serial
import math
import time
import subprocess

import utils
from data import Data
from graph import GraphData
from session import Session
from constants import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

    def init(self, settings, logger) -> None: # fonction séparée pour pouvoir passer les args (non autorisé par la classe QMainWindow sinon)
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

        self.session = None

        self.sessionButton.clicked.connect(self.session_button)
        self.sessionLabel.mousePressEvent = lambda e: self.open_session_folder()

        self.resetGyroButton.clicked.connect(lambda: self.send_command(0))

        # timer qui refresh la liste des ports séries
        self.update_serial_list()
        utils.init_qtimer(self, 5000, self.update_serial_list)
        self.serialComboBox.activated.connect(self.connect_serial)

        # timer pour l'horloge
        utils.init_qtimer(self, 1000, self.update_clock)

        # timer pour le timer (?)
        utils.init_qtimer(self, 10, self.update_timer)

        # timer principal pour la mise à jour des données
        utils.init_qtimer(self, 50, self.update_data)

        # timer d'écriture des données reçu sur le disque dur
        utils.init_qtimer(self, 5000, lambda: self.data.save(self.session))

    def handle_log(self, line : str) -> None:
        self.logTextEdit.appendPlainText(line)

    def send_command(self, command : int) -> None:
        self.serial.write(command)
        self.logger.log(f'Commande {command} envoyée')

    def session_button(self) -> None:
        if self.session == None: # session fermé, on doit alors la créer
            self.session = Session(self, self.logger)
        else: # session déjà ouverte, on doit alors la fermer
            self.session.end()

    def open_session_folder(self) -> None:
        if self.session != None:
            subprocess.Popen(['open', self.session.folder])
        else:
            subprocess.Popen(['open', SESSION_DIR])

    def update_clock(self) -> None:
        date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.clockLabel.setText(date_time)

    def update_timer(self) -> None:
        if self.session != None:
            date_time = round((datetime.now() - self.session.timer_start).total_seconds(), 1)
            self.timerLabel.setText('t+' + str(date_time) + 's')
        else:
            self.timerLabel.setText('t+0s')

    def connect_serial(self, device_index : int) -> None:
        if device_index == len(self.serial_list): # dernier élément du combobox, élément "Déconnecter"
            if self.serial.is_open:
                self.logger.log(f'Déconnexion du port série {self.serial.port}')
                self.serial.close()
        else:
            if self.serial.is_open: # si la connexion est déjà ouverte
                self.serial.close() # on la ferme
            self.serial.port = self.serial_list[device_index].device # on prends le port série sélectionner dans le combobox
            self.logger.log(f'Connexion au port série {self.serial.port}')
            self.serial.open()


    def update_serial_list(self):
        self.serialComboBox.clear() # on enlève tous les élements du combobox
        self.serial_list = serial.tools.list_ports.comports()
        for device in self.serial_list:
            self.serialComboBox.addItem(device.device + ' : ' + device.description) # on ajoute le port à la liste (port + nom)
        self.serialComboBox.addItem('Déconnecter')

    graph_data = {}
    def init_graph(self):
        self.accGraph.addLegend()
        self.gyroGraph.addLegend()

        self.graph_data['temp'] = GraphData(self.tempGraph, 'Temperature', (255, 0, 0))
        self.graph_data['accX'] = GraphData(self.accGraph, 'x', (255, 0, 0))
        self.graph_data['accY'] = GraphData(self.accGraph, 'y', (0, 255, 0))
        self.graph_data['accZ'] = GraphData(self.accGraph, 'z', (0, 0, 255))
        self.graph_data['gyroX'] = GraphData(self.gyroGraph, 'x', (255, 0, 0))
        self.graph_data['gyroY'] = GraphData(self.gyroGraph, 'y', (0, 255, 0))
        self.graph_data['gyroZ'] = GraphData(self.gyroGraph, 'z', (0, 0, 255))

    def update_data(self):
        if not self.serial.is_open:
            return

        data = self.serial.readline()
        data = self.data.process(data)

        if not data:
            return

        self.graph_data['temp'].append(data['temp'])
        self.graph_data['accX'].append(data['accX'])
        self.graph_data['accY'].append(data['accY'])
        self.graph_data['accZ'].append(data['accZ'])
        self.graph_data['gyroX'].append(data['gyroX'])
        self.graph_data['gyroY'].append(data['gyroY'])
        self.graph_data['gyroZ'].append(data['gyroZ'])

    def update_data_random(self):
        self.graph_data['temp'].append(math.sin(time.monotonic()*2))
        self.graph_data['accX'].append(math.sin(time.monotonic()*2))
        self.graph_data['accY'].append(math.sin(time.monotonic()*2+1))
        self.graph_data['accZ'].append(math.sin(time.monotonic()*2+2))
        self.graph_data['gyroX'].append(math.sin(time.monotonic()*2))
        self.graph_data['gyroY'].append(math.sin(time.monotonic()*2+1))
        self.graph_data['gyroZ'].append(math.sin(time.monotonic()*2+2))