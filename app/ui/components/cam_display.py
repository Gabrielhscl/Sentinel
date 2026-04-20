from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap

class CamDisplay(QLabel):
    # Sinais para o desenho do polígono
    clicked_pos_signal = pyqtSignal(int, object, int) 
    double_clicked_signal = pyqtSignal(int)           

    def __init__(self, slot_id, parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #2A2A2D; color: #8A8A8E; font-weight: bold;")
        self.setText(f"CÂMERA DESLIGADA")
        self.setMouseTracking(True)
        
        # Variável para guardar o frame (imagem) atual da câmera
        self._current_pixmap = None

    # Sobrescrevemos o setPixmap para guardar a imagem antes de desenhar
    def setPixmap(self, pixmap):
        self._current_pixmap = pixmap
        self.update() # Pede pro PyQt redesenhar a tela chamando o paintEvent

    def clear(self):
        self._current_pixmap = None
        super().clear()

    # ==============================================================================
    # O SEGREDO DO DESIGN: Máscara de Recorte Arredondada
    # ==============================================================================
    def paintEvent(self, event):
        # Se não tem vídeo rodando, desenha o QLabel normal (o texto "DESLIGADA")
        if self._current_pixmap is None or self._current_pixmap.isNull():
            super().paintEvent(event)
            return

        # Prepara o pintor e ativa o Anti-Aliasing para as bordas ficarem suaves
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Cria a forma de recorte
        path = QPainterPath()
        
        # A MÁGICA AQUI: Converte o QRect (Inteiro) para QRectF (Decimal)
        retangulo_decimal = QRectF(self.rect())
        path.addRoundedRect(retangulo_decimal, 22, 22) 

        # Ativa a máscara de recorte (tudo desenhado fora do path é escondido)
        painter.setClipPath(path)

        # Escala a imagem da câmera para caber no Label
        scaled_pixmap = self._current_pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        
        # Centraliza a imagem no label
        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2

        # Desenha a imagem (ela será cortada pelas bordas arredondadas automaticamente)
        painter.drawPixmap(x, y, scaled_pixmap)
        
        painter.end()

    # ==============================================================================
    # EVENTOS DE MOUSE (Gatilho do YOLO/Polígono)
    # ==============================================================================
    def mousePressEvent(self, event):
        btn = 1 if event.button() == Qt.LeftButton else 2
        self.clicked_pos_signal.emit(self.slot_id, event.pos(), btn)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked_signal.emit(self.slot_id)
        super().mouseDoubleClickEvent(event)