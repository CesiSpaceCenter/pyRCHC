import os

from PyQt6 import QtCore


# créer un QTimer en 1 ligne, au lieu de 4
def init_qtimer(parent, interval: int, connector) -> None:
    timer = QtCore.QTimer(parent)
    timer.setInterval(interval)
    timer.timeout.connect(connector)
    timer.start()


def get_dir_size(path: str) -> int:
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total
