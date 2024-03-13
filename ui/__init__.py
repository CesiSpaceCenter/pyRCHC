from __future__ import annotations

from .base_ui import Ui_MainWindow
from .box import Box
from .lcd import Lcd
from .graph import Graph

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow

from PyQt6 import QtWidgets
import json
from constants import *


class Ui:
    elements = []

    def __init__(self, window: MainWindow):
        self.window = window

        with open(os.path.join(APP_DIR, 'ui.json'), 'r') as f:
            self.config = json.loads(f.read())

        for element in self.config:
            self.elements.append(self.process_element(element, self.window.centralwidget, self.window.gridCustomUi))

    element_classes = {
        'box': Box,
        'lcd': Lcd,
        'graph': Graph
    }

    def process_element(self, properties: dict, parent: QtWidgets.QWidget, parent_grid: QtWidgets.QLayout):
        element = self.element_classes[properties['type']](self.window, parent, parent_grid, properties)
        if isinstance(element.element, QtWidgets.QLayout):
            parent_grid.addLayout(element.element,
                             properties['row'],
                             properties['col'],
                             properties['height'],
                             properties['width'])
        elif isinstance(element.element, QtWidgets.QWidget):
            parent_grid.addWidget(element.element,
                              properties['row'],
                              properties['col'],
                              properties['height'],
                              properties['width'])

        if 'content' in properties:
            for sub_element in properties['content']:
                self.elements.append(self.process_element(sub_element, element.element, element.grid))

        return element

    def reset(self):
        for element in self.elements:
            if hasattr(element, 'reset'):
                element.reset()

    def update_data(self, data: dict):
        for element in self.elements:
            if hasattr(element, 'set_data'):
                element.set_data(data)
