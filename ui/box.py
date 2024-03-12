from __future__ import annotations
from PyQt6 import QtWidgets
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow


class Box:
    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window

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

    def set_data(self, data):
        pass
