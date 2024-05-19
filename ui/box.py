from __future__ import annotations
from PyQt6 import QtWidgets
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow


class Box:
    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, _parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window

        self.element = QtWidgets.QGroupBox(parent)
        self.element.setObjectName(properties['name'])
        self.element.setTitle(properties['title'])
        self.element.setMinimumHeight(1)

        self.grid = QtWidgets.QGridLayout(self.element)
        self.grid.setObjectName(properties['name'] + '_grid')
