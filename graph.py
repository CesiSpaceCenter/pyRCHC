import pyqtgraph as pg
import time
import numpy as np

class GraphData:
    x = []
    y = []
    def __init__(self, graph, name : str, color: tuple[int, int, int], n_points: int = 100) -> None:
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
        self.x = list(np.linspace(int(-self.n_points*0.05), 0, self.n_points))
        self.y = [0.0] * self.n_points

    def append(self, data : float | int) -> None:
        self.y.pop(0) # on enlève le 1er élément
        self.y.append(data) # on ajoute la nouvelle valeur

        self.data_line.setData(self.x, self.y) # mise à jour des données