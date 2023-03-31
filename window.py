from PyQt5 import QtWidgets, QtCore, uic
import serial.tools.list_ports
from datetime import datetime
import serial
import math
import time
import subprocess

import utils
from data import Data, IntegrityCheckException
from graph import GraphData
from session import Session
from logger import Logger
from settings import Settings
from constants import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

    test_mode = False

    def init(self, settings : Settings, logger : Logger) -> None: # fonction séparée pour pouvoir passer les args (non autorisé par la classe QMainWindow sinon)
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

        self.update_serial_list()
        self.serialComboBox.activated.connect(self.handle_serial_combobox)

        # timer pour l'horloge
        self.update_clock()
        utils.init_qtimer(self, 1000, self.update_clock)

        # timer pour le timer (?)
        utils.init_qtimer(self, 10, self.update_timer)

        # timer principal pour la mise à jour des données
        utils.init_qtimer(self, 50, self.update_data)

        # timer d'écriture des données reçues sur le disque dur
        utils.init_qtimer(self, 5000, lambda: self.data.save(self.session) if self.session != None else None) # on n'éxecute la fonction save que si la session est ouverte

    def handle_log(self, line : str) -> None:
        self.logTextEdit.appendPlainText(line)

    def send_command(self, command : int) -> None:
        if self.serial.is_open and not self.test_mode:
            self.serial.write(bytes(command))
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

    def handle_serial_combobox(self, device_index : int) -> None:
        combobox_items = [self.serialComboBox.itemText(i) for i in range(self.serialComboBox.count())]
        selected_item = combobox_items[device_index]

        if self.test_mode and selected_item == 'Déconnecter':
                self.logger.log('Fermeture du mode test')
                self.serial.is_open = False
                self.test_mode = False

        elif selected_item == 'TEST':
            self.logger.log('Activation du mode test')
            self.serial.is_open = True
            self.test_mode = True

        elif selected_item == 'Actualiser':
            pass # dans tous les cas, la liste est actualisée à la fin de la fonction
            
        elif selected_item == 'Déconnecter': # dernier élément du combobox, élément "Déconnecter"
            if self.serial.is_open:
                self.logger.log(f'Déconnexion du port série {self.serial.port}')
                self.serial.close()
        else:
            if self.serial.is_open: # si la connexion est déjà ouverte
                self.serial.close() # on la ferme
            self.serial.port = self.serial_list[device_index].device # on prends le port série sélectionner dans le combobox
            self.logger.log(f'Connexion au port série {self.serial.port}')
            self.serial.open()

        self.update_serial_list()
    
    def update_serial_list(self):
        self.serialComboBox.clear() # on enlève tous les élements du combobox
        self.serial_list = serial.tools.list_ports.comports()
        for device in self.serial_list:
            self.serialComboBox.addItem(device.device + ' : ' + device.description) # on ajoute le port à la liste (port + nom)
        self.serialComboBox.addItem('TEST')
        self.serialComboBox.addItem('Actualiser')
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
        self.graph_data['misc'] = GraphData(self.graph, '', (255, 0, 0))

    def update_data(self) -> None:
        if not self.serial.is_open:
            return

        if not self.test_mode:
            raw_data = self.serial.readline()
        else:
            raw_data = self.generate_test_data()

        try:
            data = self.data.process(raw_data)
        except IntegrityCheckException as err:
            self.logger.log('Vérification des données échouée:', str(err), raw_data)
            return

        self.graph_data['temp'].append(data['temp'])
        self.graph_data['accX'].append(data['accX'])
        self.graph_data['accY'].append(data['accY'])
        self.graph_data['accZ'].append(data['accZ'])
        self.graph_data['gyroX'].append(data['gyroX'])
        self.graph_data['gyroY'].append(data['gyroY'])
        self.graph_data['gyroZ'].append(data['gyroZ'])

    def generate_test_data(self) -> bytes:        
        clock = time.monotonic()
        temp = round(math.sin(time.monotonic()*2), 2)
        accX = round(math.sin(time.monotonic()*2), 2)
        accY = round(math.sin(time.monotonic()*2+1), 2)
        accZ = round(math.sin(time.monotonic()*2+2), 2)
        gyroX = round(math.sin(time.monotonic()*2), 2)
        gyroY = round(math.sin(time.monotonic()*2+1), 2)
        gyroZ = round(math.sin(time.monotonic()*2+2), 2)

        return f'{clock},{accX},{accY},{accZ},{gyroX},{gyroY},{gyroZ},{temp}\r\n'.encode('ascii')