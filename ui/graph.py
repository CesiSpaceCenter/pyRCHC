from __future__ import annotations
from PyQt6 import QtWidgets
from PyQt6.QtCore import QElapsedTimer
import pyqtgraph as pg
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from window import MainWindow


class GraphData:  # represents one data series, a graph can contain multiple data series

    def __init__(self, graph: pg.PlotWidget, name: str, color: tuple[int, int, int]) -> None:
        self.timer = QElapsedTimer()  # used to display elapsed time on the y axis

        self.x = []
        self.y = []

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
        self.x.append(self.timer.elapsed()/1000)  # add the time on the x axis
        self.y.append(data)  # add the new data point on the y axis

        self.data_line.setData(self.x, self.y)


class Graph:
    data_series = {}

    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, _parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window
        self.properties = properties

        self.element = pg.PlotWidget(parent)
        self.element.setObjectName(self.properties['name'])
        self.element.addLegend()

        for data_element, graph_properties in self.properties['data'].items():
            # create a new data series
            self.data_series[data_element] = GraphData(self.element, graph_properties['name'], graph_properties['color'])

    def set_data(self, data: dict):
        if 'data' in self.properties:
            for data_element, graph_properties in self.properties['data'].items():
                if data_element in data:
                    self.data_series[data_element].append(data[data_element])

    def reset(self):
        for series in self.data_series.values():
            series.reset()
