from __future__ import annotations

from .base_ui import Ui_MainWindow
from .box import Box
from .lcd import Lcd
from .graph import Graph
from .data_box import DataBox
from .scene_3d import Scene3D

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

        self.window.gridCustomUi.setRowStretch(0, 0)

    element_classes = {
        'box': Box,
        'lcd': Lcd,
        'graph': Graph,
        'data box': DataBox,
        '3d scene': Scene3D
    }

    def process_element(self, properties: dict, parent: QtWidgets.QWidget, parent_grid: QtWidgets.QGridLayout):
        # get the class corresponding to the element name, and initialize it
        element = self.element_classes[properties['type']](self.window, parent, parent_grid, properties)

        if isinstance(element.element, QtWidgets.QLayout):  # if the element is a layout
            parent_grid.addLayout(element.element,
                                  properties['row'],
                                  properties['col'],
                                  properties['height'],
                                  properties['width'])
        elif isinstance(element.element, QtWidgets.QWidget):  # if the element is a widget
            parent_grid.addWidget(element.element,
                                  properties['row'],
                                  properties['col'],
                                  properties['height'],
                                  properties['width'])

        parent_grid.setRowStretch(properties['row'], properties['height'])
        parent_grid.setColumnStretch(properties['col'], properties['width'])

        if 'content' in properties:  # if the element has children, process them
            for sub_element in properties['content']:
                self.elements.append(self.process_element(sub_element, element.element, element.grid))

        return element

    def reset(self):
        # reset every elements (eg: remove all data in graphs)
        for element in self.elements:
            if hasattr(element, 'reset'):
                element.reset()

    def update_data(self, data: dict):
        # set (or add) new data for every elements
        for element in self.elements:
            if hasattr(element, 'set_data'):
                element.set_data(data)
