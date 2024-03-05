from PyQt5 import QtWidgets


class Box:
    def __init__(self, MainWindow, parent, parent_grid, properties):
        self.MainWindow = MainWindow

        self.element = QtWidgets.QGroupBox(parent)
        self.element.setObjectName(properties['name'])
        self.element.setTitle(properties['title'])

        self.grid = QtWidgets.QGridLayout(self.element)
        self.grid.setObjectName(f'{properties["name"]}_grid')

        parent_grid.addWidget(self.element,
                             properties['row'],
                             properties['col'],
                             properties['height'],
                             properties['width'])