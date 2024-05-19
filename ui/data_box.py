from __future__ import annotations
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QFontMetrics
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from window import MainWindow


class DataBox:
    data_series = {}

    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, _parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window
        self.properties = properties

        self.element = QtWidgets.QTextBrowser(parent)
        font = QFont('monospace', 13)
        self.char_width = QFontMetrics(font).averageCharWidth()
        self.element.setFont(font)
        self.element.setObjectName(self.properties['name'])

    def set_data(self, data: dict):
        if 'data' in self.properties:
            text = ''
            current_line = ''
            for i, data_item in enumerate(self.properties['data']):
                if data_item in data:
                    # set the name to be 4 chars exactly (truncate or add spaces before)
                    data_name = ' '*(4-len(data_item[:4])) + data_item[:4]
                    data_text = f'{data_name}: {data[data_item]}   '
                    # if there is no more space in the text browser, start a new line
                    if self.char_width*len(current_line + data_text) > self.element.width():
                        text += current_line + '\n'
                        current_line = data_text
                    else:  # if there is still space, just append the new text
                        current_line += data_text

                    # if this is the last data item to display,
                    # add the current line to the text (do not wait for it to be complete)
                    if i == len(self.properties['data'])-1:
                        text += current_line
            self.element.setText(text)
