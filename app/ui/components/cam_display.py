from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, QPoint

class CamDisplay(QLabel):
    clicked_pos_signal = pyqtSignal(int, QPoint, int)
    double_clicked_signal = pyqtSignal(int) 

    def __init__(self, slot_id):
        super().__init__()
        self.slot_id = slot_id
        self.setStyleSheet("border-radius: 12px; background: #202020; margin: 4px;")
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        self.clicked_pos_signal.emit(self.slot_id, event.pos(), event.button())

    def mouseDoubleClickEvent(self, event):
        self.double_clicked_signal.emit(self.slot_id)