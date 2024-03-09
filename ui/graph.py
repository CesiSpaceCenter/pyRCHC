from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np


class GraphData:
    x = []
    y = []

    def __init__(self, graph: pg.PlotWidget, name: str, color: tuple[int, int, int], n_points: int = 100) -> None:
        self.n_points = n_points
        self.reset()

        self.data_line = graph.plot(
            self.x,
            self.y,
            pen=pg.mkPen(color=color),
            name=name
        )

        graph.getAxis('bottom').labelUnits = 's'

    def reset(self) -> None:
        self.x = list(np.linspace(int(-self.n_points * 0.05), 0, self.n_points))
        self.y = [0.0] * self.n_points

    def append(self, data: float | int) -> None:
        self.y.pop(0)  # on enlève le 1er élément
        self.y.append(data)  # on ajoute la nouvelle valeur

        self.data_line.setData(self.x, self.y)  # mise à jour des données


class Graph:
    data_series = {}

    def __init__(self, MainWindow, parent, parent_grid, properties):
        self.MainWindow = MainWindow
        self.properties = properties

        self.element = pg.PlotWidget(parent)
        self.element.setObjectName(self.properties['name'])
        self.element.addLegend()

        for data_element, data_properties in self.properties['data'].items():
            self.data_series[data_element] = GraphData(self.element, data_properties['name'], data_properties['color'])

        parent_grid.addWidget(self.element,
                             self.properties['row'],
                             self.properties['col'],
                             self.properties['height'],
                             self.properties['width'])

    def set_data(self, data):
        if 'data' in self.properties:
            for data_element, data_properties in self.properties['data'].items():
                if data_element in data:
                    self.data_series[data_element].append(data[data_element])
