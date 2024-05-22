import re
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
    session = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.settings = Settings()
        self.logger = Logger()

        self.logger.log('Creating window')

        self.setupUi(self)  # load the base ui
        self.custom_ui = ui.Ui(self)  # load the custom ui

        # load the stylesheet
        with open('style.css', 'r') as style_file:
            self.setStyleSheet(style_file.read())

        self.show()

        self.logger.set_main_window(self)

        self.data = Data()

        self.sessionButton.clicked.connect(self.session_button)  # button to start or end a session

        self.update_serial_list()  # update the serial devices list
        self.serialComboBox.activated.connect(self.handle_serial_combobox)  # choose a new serial device

        # timer used to update the clock
        self.update_clock()
        utils.init_qtimer(self, 1000, self.update_clock)

        # timer for the timer (???)
        utils.init_qtimer(self, 10, self.update_timer)

        # main timer to update data
        utils.init_qtimer(self, 50, self.update)

        # timer d'écriture des données reçues sur le disque dur
        # timer to write data on the disk
        utils.init_qtimer(self, 5000, lambda: self.data.save(self.session))

    def handle_log(self, line: str) -> None:
        # in the log box, we don't want to write a message if it is logged multiple times, so we add a number
        # example instead of :
        #   warning! somethings happening
        #   warning! somethings happening
        #   warning! somethings happening
        # we have :
        #   warning! somethings happening (x3)

        last_line = self.logTextEdit.toPlainText().split('\n')[-1]  # fetch the last line of the log box
        if last_line.startswith(line):  # if the last line's beginning is the same as the new line, it is a repetition
            # remove the log message (so we end up with "(x3)", and then find the number in that (3)
            num = re.findall(r'\d+', last_line.replace(line, ''))
            if not num:  # if there is no number yet
                # that means this is the first time this line is repeating
                # so we just add the suffix
                # we don't use appendPlainText() here because it adds a newline before
                self.logTextEdit.setPlainText(self.logTextEdit.toPlainText() + ' (x2)')
            else:  # if there is a number
                # that means this line has already been repeated
                num = int(num[0]) + 1  # we add 1 to this repeat count
                # remove the part after the last space (which is the (x3)),
                # and add the new suffix
                self.logTextEdit.setPlainText(self.logTextEdit.toPlainText().rpartition(' ')[0] + f' (x{num})')
        else:  # this is just a new message, not a repetition
            self.logTextEdit.appendPlainText(line)

        # scroll to th end
        self.logTextEdit.verticalScrollBar().setValue(self.logTextEdit.verticalScrollBar().maximum())

    def session_button(self) -> None:
        if self.session is None:  # session is closed, we open a new one
            self.session = Session(self)
        else:  # session is open, we close it
            self.session.end()

    def update_clock(self) -> None:
        date_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.clockLabel.setText(date_time)

    serial_list = None

    def update_timer(self) -> None:
        if self.session is not None:
            # seconds since the timer started
            date_time = round((datetime.now() - self.session.timer_start).total_seconds(), 1)
            self.timerLabel.setText('t+' + str(date_time) + 's')
        else:
            self.timerLabel.setText('t+0s')

    def handle_serial_combobox(self, device_index: int) -> None:
        selected_item = self.serialComboBox.itemText(device_index)

        if selected_item == 'Refresh':
            pass  # refresh is done in every case at the end of the function

        elif selected_item == 'Disconnect':
            # close the serial connection if it is open
            if self.data.serial.is_open:
                self.logger.log(f'Closing serial connection {self.data.serial.port}')
                self.data.serial.close()

        else:  # a serial device is selected
            if self.data.serial.is_open:  # if the connection is already open
                self.data.serial.close()
            # get the selected device & connect
            self.data.serial.port = self.serial_list[device_index].device
            self.logger.log(f'Connecting to serial port {self.data.serial.port}')
            self.data.serial.open()

        self.update_serial_list()

    def update_serial_list(self) -> None:
        self.serialComboBox.clear()  # remove every elements from the combobox
        self.serial_list = serial.tools.list_ports.comports()  # get the devices list
        for device in self.serial_list:
            self.serialComboBox.addItem(
                device.device + ' : ' + device.description)  # add a combobox item (name + path)

        # add non devices items
        self.serialComboBox.addItem('Refresh')
        self.serialComboBox.addItem('Disconnect')

    # the following section is not commented because it will be completely changed in a future update

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

        if time.time() - self.last_successful_data > 4:  # no data for more than 4 seconds
            self.status['connexion'] = 1
            self.status['timeout'] = 1

        if not self.data.serial.is_open and not bool(os.environ.get('DEBUG', False)):  # serial port is not open
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

        for error in errors:
            self.logger.log(error["message"])
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
