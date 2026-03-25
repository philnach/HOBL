"""
Class for toolbar buttons that prevents spacebar from tigerring them
"""

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QEvent, Qt

class FilteredButton(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

    def event(self, event):
        if (event.type() == QEvent.Type.KeyPress) and (event.key() == Qt.Key.Key_Space):
            print("Got a space")
            return True
        return True