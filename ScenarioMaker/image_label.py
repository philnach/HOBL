"""
Overrides image label widget to be able to handle paint event.
"""

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap, QWheelEvent

class ImageLabel(QtWidgets.QWidget):
    x = 0
    y = 0
    r = 1.0
    draw_select = False

    mouse_wheel_signal = pyqtSignal(QtGui.QWheelEvent)
    mouse_move_signal = pyqtSignal(QtGui.QMouseEvent)
    mouse_lpress_signal = pyqtSignal(QtGui.QMouseEvent)
    mouse_rpress_signal = pyqtSignal(QtGui.QMouseEvent)
    mouse_lrelease_signal = pyqtSignal(QtGui.QMouseEvent)
    mouse_rrelease_signal = pyqtSignal(QtGui.QMouseEvent)

    def __init__(self, parent = None):
        super().__init__(parent)
        self._image = None

    def setImage(self, image):
        self._image = image
        self.update()

    def image(self):
        return self._image
    
    def drawSelect(self, x, y, w, h, cx_frac=0.5, cy_frac=0.5):
        self.draw_select = True
        self.select_x = x
        self.select_y = y
        self.select_w = w
        self.select_h = h
        self.select_cx = int(x + (w * cx_frac))
        self.select_cy = int(y + (h * cy_frac))
        self.update()

    def clearSelect(self):
        self.draw_select = False
        self.update()

    def paintEvent(self, event):
        if self._image is None:
            return
        self._image.setDevicePixelRatio(self.screen().devicePixelRatio())
        painter = QtGui.QPainter(self)
        width = self.width() #* self.screen().devicePixelRatio()
        height = self.height() #* self.screen().devicePixelRatio()
        imageWidth = self._image.width() / self.screen().devicePixelRatio()
        imageHeight = self._image.height() / self.screen().devicePixelRatio()
        r1 = width / imageWidth
        r2 = height / imageHeight
        self.r = min(r1, r2)
        self.x = int(((width - imageWidth * self.r) / 2))
        self.y = int(((height - imageHeight * self.r) / 2))
        pixmap = QPixmap.fromImage(self._image)
        pixmap_scaled = pixmap.scaled(pixmap.size() * self.r, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(self.x, self.y, pixmap_scaled)

        if self.draw_select:
            # print(f"select_w drawn at {self.select_w}")
            painter_overlay = QtGui.QPainter(self)
            painter_overlay.setPen(QtGui.QPen(QtGui.QColor(0xff, 0x00, 0x00), 2, Qt.PenStyle.SolidLine))
            painter_overlay.drawRect(self.select_x, self.select_y, self.select_w, self.select_h)
            painter_overlay.drawRect(self.select_cx - 1, self.select_cy - 1, 2, 2)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.mouse_move_signal.emit(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_lpress_signal.emit(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.mouse_rpress_signal.emit(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_lrelease_signal.emit(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.mouse_rrelease_signal.emit(event)

    def wheelEvent(self, event: QWheelEvent):
        self.mouse_wheel_signal.emit(event)


