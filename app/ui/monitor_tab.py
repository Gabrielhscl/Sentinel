from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QFrame, QLabel, QPushButton, QScrollArea, QSizePolicy, QButtonGroup, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from app.core.monitor_controller import MonitorController
from app.ui.components.cam_display import CamDisplay
from app.workers.video_worker import VideoWorker

# ==============================================================================
# ComboBox Customizado (Avisa a câmera quando fecha a lista)
# ==============================================================================
class HoverComboBox(QComboBox):
    popupClosed = pyqtSignal()
    
    def hidePopup(self):
        super().hidePopup()
        self.popupClosed.emit()

# ==============================================================================
# Célula da Câmera (Fundo 24px + Overlay 22px)
# ==============================================================================
class CameraCell(QFrame):
    def __init__(self, slot_id, parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.setObjectName("CamCell")
        
        self.setStyleSheet("""
            QFrame#CamCell {
                background-color: #2A2A2D;
                border-radius: 24px;
                border: 2px solid transparent;
            }
            QFrame#CamCell:hover {
                border: 2px solid #FF5722; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.display = CamDisplay(slot_id)
        self.display.setMinimumSize(350, 250)
        self.display.setStyleSheet("border-radius: 22px; background: #2A2A2D;")
        layout.addWidget(self.display)

        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 18, 20, 0.9); 
                border-radius: 22px;
            }
        """)
        
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)
        overlay_layout.setSpacing(12)
        
        lbl_title = QLabel("SELECIONAR CÂMERA")
        lbl_title.setStyleSheet("color: #8A8A8E; font-size: 11px; font-weight: bold; background: transparent; letter-spacing: 1px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        self.combo_ch = HoverComboBox()
        self.combo_ch.addItems(["DESLIGADA", "📱 CELULAR (TESTE)"] + [f"CANAL {c:02d}" for c in range(1, 17)])
        self.combo_ch.setCursor(Qt.PointingHandCursor)
        self.combo_ch.setStyleSheet("""
            QComboBox {
                background-color: #121214; color: #F2F2F2;
                border-radius: 12px; padding: 12px;
                font-weight: bold; min-width: 180px; border: 1px solid #2A2A2D;
            }
            QComboBox:hover { border: 1px solid #FF5722; color: #FF5722; }
            QComboBox::drop-down { border: none; }
        """)
        
        overlay_layout.addWidget(lbl_title)
        overlay_layout.addWidget(self.combo_ch)
        
        self.overlay.hide()
        self.combo_ch.popupClosed.connect(self._check_hide_overlay)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())

    def enterEvent(self, event):
        self.overlay.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.combo_ch.view().isVisible():
            self.overlay.hide()
        super().leaveEvent(event)

    def _check_hide_overlay(self):
        if not self.underMouse():
            self.overlay.hide()

# ==============================================================================
# TAB PRINCIPAL DE MONITORAMENTO
# ==============================================================================
class MonitorTab(QWidget):
    def __init__(self, controller: MonitorController):
        super().__init__()
        self.controller = controller
        self.active_workers = {}
        self.init_ui()
        self._connect_signals()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #121214; }
            QFrame#Panel { background-color: #1C1C1F; border-radius: 24px; }
            QFrame#PortariaCard { 
                background-color: #202024; border-radius: 24px; border: 1px solid transparent;
            }
            QFrame#PortariaCard:hover {
                background-color: #252529; border: 1px solid #3A3A3D;
            }
            QLabel { color: #F2F2F2; font-weight: bold; }
            QPushButton#BtnAction { 
                background-color: #2A2A2D; color: #F2F2F2;
                border-radius: 15px; padding: 12px; font-weight: bold; border: 1px solid #3A3A3D;
            }
            QPushButton#BtnAction:hover { background-color: #3A3A3D; border: 1px solid #FF5722; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #2A2A2D; border-radius: 4px; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(20)

        # --- ESQUERDA: Câmeras ---
        self.grid_container = QFrame()
        self.grid_container.setObjectName("Panel")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        self.grid_layout.setSpacing(15)

        self.displays = {}
        self.camera_cells = {} 

        for i in range(4):
            cell = CameraCell(i)
            self.grid_layout.addWidget(cell, i // 2, i % 2)
            self.camera_cells[i] = cell
            self.displays[i] = cell.display 

        layout.addWidget(self.grid_container, 7)

        # --- DIREITA: Portaria ---
        self.right_scroll = QScrollArea()
        self.right_scroll.setFixedWidth(380)
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setFrameShape(QFrame.NoFrame)
        self.right_scroll.setStyleSheet("background-color: transparent;")

        self.right_panel = QFrame()
        self.right_panel.setObjectName("Panel")
        right_vbox = QVBoxLayout(self.right_panel)
        right_vbox.setContentsMargins(15, 20, 15, 20)
        right_vbox.setSpacing(15)

        lbl_portaria_header = QLabel("📡 CONTROLE DE ACESSO")
        lbl_portaria_header.setAlignment(Qt.AlignCenter)
        lbl_portaria_header.setStyleSheet("color: #8A8A8E; font-size: 13px; letter-spacing: 1px;")
        right_vbox.addWidget(lbl_portaria_header)

        self.toggle_container = QFrame()
        self.toggle_container.setObjectName("ToggleContainer")
        self.toggle_container.setStyleSheet("""
            QFrame#ToggleContainer {
                background-color: #121214; border-radius: 12px; padding: 4px;
            }
            QPushButton#ToggleBtn {
                background-color: transparent; color: #8A8A8E;
                border-radius: 8px; padding: 8px; font-weight: bold; font-size: 12px; border: none;
            }
            QPushButton#ToggleBtn:checked { background-color: #2A2A2D; color: #F2F2F2; }
        """)
        
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_cam_veiculos = QPushButton("🚗 VEÍCULOS")
        self.btn_cam_veiculos.setObjectName("ToggleBtn")
        self.btn_cam_veiculos.setCheckable(True)
        self.btn_cam_veiculos.setChecked(True) 

        self.btn_cam_pedestres = QPushButton("🚶 PEDESTRES")
        self.btn_cam_pedestres.setObjectName("ToggleBtn")
        self.btn_cam_pedestres.setCheckable(True)

        self.cam_toggle_group = QButtonGroup(self)
        self.cam_toggle_group.addButton(self.btn_cam_veiculos, 104) 
        self.cam_toggle_group.addButton(self.btn_cam_pedestres, 109) 

        toggle_layout.addWidget(self.btn_cam_veiculos)
        toggle_layout.addWidget(self.btn_cam_pedestres)
        right_vbox.addWidget(self.toggle_container)
        
        self.disp_porteiro = CamDisplay(104)
        self.disp_porteiro.setMinimumSize(310, 310)
        self.disp_porteiro.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.disp_porteiro.setStyleSheet("QLabel { border-radius: 24px; background: #2A2A2D; border: 2px solid transparent; } QLabel:hover { border: 2px solid #FF5722; }")
        right_vbox.addWidget(self.disp_porteiro, alignment=Qt.AlignCenter)

        self.card_veiculos, self.btn_abrir_veiculos, self.lbl_status_veiculos = self._create_portaria_card("Veículos", "🚗")
        right_vbox.addWidget(self.card_veiculos)

        self.card_pedestres, self.btn_abrir_pedestres, self.lbl_status_pedestres = self._create_portaria_card("Pedestres", "🚶")
        right_vbox.addWidget(self.card_pedestres)
        
        right_vbox.addStretch()
        self.right_scroll.setWidget(self.right_panel)
        layout.addWidget(self.right_scroll, 3)

    def _create_portaria_card(self, title, icon):
        card = QFrame()
        card.setObjectName("PortariaCard")
        vbox_card = QVBoxLayout(card)
        vbox_card.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel(f"{icon} {title.upper()}")
        lbl_title.setStyleSheet("font-size: 14px; color: #F2F2F2;")
        
        lbl_status = QLabel("⚪ Lendo...")
        lbl_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_status.setStyleSheet("color: #8A8A8E; font-size: 12px;")
        
        header_layout.addWidget(lbl_title)
        header_layout.addWidget(lbl_status)
        vbox_card.addLayout(header_layout)
        
        btn_abrir = QPushButton(" ABRIR PORTÃO")
        btn_abrir.setObjectName("BtnAction")
        btn_abrir.setCursor(Qt.PointingHandCursor)
        vbox_card.addWidget(btn_abrir)
        
        return card, btn_abrir, lbl_status

    def _connect_signals(self):
        self.btn_abrir_veiculos.clicked.connect(lambda: self.controller.request_door_open(104, "192.168.0.104", "Veículos", "#4ade80"))
        self.btn_abrir_pedestres.clicked.connect(lambda: self.controller.request_door_open(109, "192.168.0.109", "Pedestres", "#38bdf8"))
        self.cam_toggle_group.idClicked.connect(self._handle_porteiro_change)
        
        for i, cell in self.camera_cells.items():
            cell.combo_ch.currentIndexChanged.connect(self._make_handler(i))
            
        self.controller.door_status_changed_signal.connect(self.update_door_status)

    def _make_handler(self, slot_id):
        return lambda idx: self._handle_camera_channel_change(slot_id, idx)

    def _handle_camera_channel_change(self, slot_id, combo_idx):
        if slot_id in self.active_workers:
            self.active_workers[slot_id].stop()
            del self.active_workers[slot_id]

        if combo_idx == 0:
            self.displays[slot_id].clear()
            self.displays[slot_id].setText("CÂMERA DESLIGADA")
            return

        url = "celular" if combo_idx == 1 else f"rtsp://recepcao:casablanca7040@192.168.0.47:554/cam/realmonitor?channel={combo_idx - 2}&subtype=1"

        worker = VideoWorker(slot_id, url)
        worker.change_pixmap_signal.connect(self._update_display_slot)
        worker.status_signal.connect(self._update_status_label)
        
        self.active_workers[slot_id] = worker
        worker.start()

    def _update_display_slot(self, qimg, slot_id):
        if slot_id in self.displays:
            self.displays[slot_id].setPixmap(QPixmap.fromImage(qimg))

    def _update_status_label(self, slot_id, status):
        print(f"Slot {slot_id}: {status}")
        if status == "CONECTANDO...":
            self.displays[slot_id].setText("🔄 CONECTANDO...")

    def _handle_porteiro_change(self, btn_id):
        pass

    def update_door_status(self, slot_id, is_open):
        lbl = self.lbl_status_veiculos if slot_id == 104 else self.lbl_status_pedestres
        card = self.card_veiculos if slot_id == 104 else self.card_pedestres
        btn = self.btn_abrir_veiculos if slot_id == 104 else self.btn_abrir_pedestres

        if is_open is None:
            lbl.setText("⚪ OFFLINE")
            lbl.setStyleSheet("color: #8A8A8E; font-weight: bold;")
        elif is_open:
            lbl.setText("🔴 ABERTO")
            lbl.setStyleSheet("color: #FF5722; font-weight: bold;") 
            card.setStyleSheet("background-color: #202024; border: 1px solid #FF5722; border-radius: 24px; padding: 10px;")
            btn.setEnabled(False)
            btn.setText(" JÁ ESTÁ ABERTO")
        else:
            lbl.setText("🟢 FECHADO")
            lbl.setStyleSheet("color: #2ecc71; font-weight: bold;")
            card.setStyleSheet("background-color: #202024; border: 1px solid transparent; border-radius: 24px; padding: 10px;")
            btn.setEnabled(True)
            btn.setText(" ABRIR PORTÃO")