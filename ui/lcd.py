from PyQt5 import QtWidgets


class Lcd:
    def __init__(self, MainWindow, parent, parent_grid, properties):
        self.MainWindow = MainWindow
        self.properties = properties

        self.element = QtWidgets.QHBoxLayout()
        self.element.setObjectName(f'{self.properties["name"]}_layout')

        self.label = QtWidgets.QLabel(parent)
        self.label.setObjectName(f'{self.properties["name"]}_label')
        self.label.setText(self.properties['text'])

        self.lcd = QtWidgets.QLCDNumber(parent)
        self.lcd.setObjectName(f'{self.properties["name"]}_lcd')
        self.lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.element.addWidget(self.label)
        self.element.addWidget(self.lcd)

        parent_grid.addLayout(self.element,
                             properties['row'],
                             properties['col'],
                             properties['height'],
                             properties['width'])

    def set_data(self, data):
        if 'data' in self.properties and self.properties['data'] in data:
            self.lcd.setProperty('value', data[self.properties['data']])