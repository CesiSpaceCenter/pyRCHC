from __future__ import annotations

from .base_ui import Ui_MainWindow
from .box import Box
from .lcd import Lcd
from .graph import Graph

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow

from PyQt5 import QtWidgets
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
        print(isinstance(parent, QtWidgets.QWidget), isinstance(parent_grid, QtWidgets.QLayout))
        element = self.element_classes[properties['type']](self.window, parent, parent_grid, properties)

        if 'content' in properties:
            for sub_element in properties['content']:
                self.elements.append(self.process_element(sub_element, element.element, element.grid))

        return element
