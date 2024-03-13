from __future__ import annotations
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTime, QElapsedTimer
import pyqtgraph as pg
import numpy as np
import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow


class GraphData:
    x = []
    y = []

    def __init__(self, graph: pg.PlotWidget, name: str, color: tuple[int, int, int]) -> None:
        self.timer = QElapsedTimer()

        self.reset()

        self.data_line = graph.plot(
            self.x,
            self.y,
            pen=pg.mkPen(color=color),
            name=name
        )

    def reset(self) -> None:
        self.timer.restart()
        self.x = []
        self.y = []

    def append(self, data: float | int) -> None:
        self.x.append(self.timer.elapsed()/1000)
        self.y.append(data)  # on ajoute la nouvelle valeur

        self.data_line.setData(self.x, self.y)  # mise à jour des données

class Graph:
    data_series = {}

    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window
        self.properties = properties

        self.element = pg.PlotWidget(parent)
        self.element.setObjectName(self.properties['name'])
        self.element.addLegend()

        for data_element, data_properties in self.properties['data'].items():
            self.data_series[data_element] = GraphData(self.element, data_properties['name'], data_properties['color'])

    def set_data(self, data: dict):
        if 'data' in self.properties:
            for data_element, data_properties in self.properties['data'].items():
                if data_element in data:
                    self.data_series[data_element].append(data[data_element])

    def reset(self):
        for series in self.data_series.values():
            series.reset()