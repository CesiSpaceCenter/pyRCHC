from PyQt5 import QtWidgets


class Lcd:
    def __init__(self, MainWindow, parent, parent_grid, properties):
        self.MainWindow = MainWindow

        self.element = QtWidgets.QHBoxLayout()
        self.element.setObjectName(f'{properties["name"]}_layout')

        self.label = QtWidgets.QLabel(parent)
        self.label.setObjectName(f'{properties["name"]}_label')
        self.label.setText(properties['text'])

        self.lcd = QtWidgets.QLCDNumber(parent)
        self.lcd.setObjectName(f'{properties["name"]}_lcd')
        self.lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.element.addWidget(self.label)
        self.element.addWidget(self.lcd)

        parent_grid.addLayout(self.element,
                             properties['row'],
                             properties['col'],
                             properties['height'],
                             properties['width'])