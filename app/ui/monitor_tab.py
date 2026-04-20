import subprocess
import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QFrame, QLabel, QPushButton, QScrollArea, QSizePolicy, 
                             QButtonGroup, QComboBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from app.core.monitor_controller import MonitorController
from app.ui.components.cam_display import CamDisplay
from app.workers.video_worker import VideoWorker
from app.models.camera_config import CameraConfig
from app.ui.components.camera_config_dialog import CameraConfigDialog

class HoverComboBox(QComboBox):
    popupClosed = pyqtSignal()
    def hidePopup(self):
        super().hidePopup()
        self.popupClosed.emit()

class CameraCell(QFrame):
    config_clicked_signal = pyqtSignal(int)
    yolo_toggled_signal = pyqtSignal(int, bool)
    drawing_toggled_signal = pyqtSignal(int) # SINAL NOVO

    def __init__(self, slot_id, parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.setObjectName("CamCell")
        
        # VARIÁVEL DE ESTADO DA PRÓPRIA CÂMARA
        self.is_drawing_mode = False 
        
        self.setStyleSheet("""
            QFrame#CamCell { background-color: #2A2A2D; border-radius: 24px; border: 2px solid transparent; }
            QFrame#CamCell:hover { border: 2px solid #FF5722; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.display = CamDisplay(slot_id)
        self.display.setMinimumSize(350, 250)
        self.display.setStyleSheet("border-radius: 22px; background: #2A2A2D;")
        layout.addWidget(self.display)

        # --- BOTÃO FLUTUANTE DE CONCLUIR DESENHO ---
        self.btn_finish_draw = QPushButton("💾 Concluir Desenho", self)
        self.btn_finish_draw.setCursor(Qt.PointingHandCursor)
        self.btn_finish_draw.setStyleSheet("""
            QPushButton { 
                background-color: #2ecc71; color: white; font-weight: bold; 
                border-radius: 8px; padding: 5px; font-size: 13px; border: 1px solid #27ae60;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_finish_draw.hide() # Começa invisível
        self.btn_finish_draw.clicked.connect(lambda: self.drawing_toggled_signal.emit(self.slot_id))

        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("""
            QFrame { background-color: rgba(18, 18, 20, 0.90); border-bottom-left-radius: 22px; border-bottom-right-radius: 22px; }
        """)
        
        overlay_layout = QHBoxLayout(self.overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)
        overlay_layout.setContentsMargins(15, 12, 15, 12) 
        overlay_layout.setSpacing(10) 
        
        self.combo_ch = HoverComboBox()
        self.combo_ch.addItems(["DESLIGADA", "📱 CELULAR"] + [f"CANAL {c:02d}" for c in range(1, 17)])
        self.combo_qld = HoverComboBox()
        self.combo_qld.addItems(["SD", "HD"]) 
        self.combo_fps = HoverComboBox()
        self.combo_fps.addItems(["10 FPS", "15 FPS", "30 FPS"]) 
        self.combo_fps.setCurrentIndex(1) 

        self.btn_yolo = QPushButton("IA")
        self.btn_yolo.setCheckable(True) 
        self.btn_yolo.setCursor(Qt.PointingHandCursor)
        self.btn_yolo.setToolTip("Ativar Inteligência Artificial (YOLO)")

        self.btn_draw = QPushButton("✏️")
        self.btn_draw.setCursor(Qt.PointingHandCursor)
        self.btn_draw.setToolTip("Desenhar Área de Detecção")

        self.btn_config = QPushButton("⚙️")
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.setToolTip("Configurações da Câmara")

        combo_style = """
            QComboBox {
                background-color: #1C1C1F; color: #F2F2F2; border-radius: 8px; 
                padding: 8px 10px; font-weight: bold; font-size: 12px; border: 1px solid #3A3A3D; min-height: 26px; 
            }
            QComboBox:hover { border: 1px solid #FF5722; color: #FF5722; }
            QComboBox::drop-down { border: none; }
        """
        self.combo_ch.setStyleSheet(combo_style + "QComboBox { min-width: 120px; }")
        self.combo_qld.setStyleSheet(combo_style)
        self.combo_fps.setStyleSheet(combo_style)
        
        self.btn_yolo.setStyleSheet("""
            QPushButton {
                background-color: #1C1C1F; color: #8A8A8E; border-radius: 8px; 
                font-size: 12px; font-weight: bold; padding: 6px 12px; border: 1px solid #3A3A3D; min-height: 26px;
            }
            QPushButton:hover { border: 1px solid #FF5722; color: #FF5722; }
            QPushButton:checked { background-color: #FF5722; color: #FFFFFF; border: 1px solid #FF5722; }
        """)

        icon_btn_style = """
            QPushButton {
                background-color: #1C1C1F; border-radius: 8px; font-size: 16px; padding: 4px 10px; border: 1px solid #3A3A3D; min-height: 26px;
            }
            QPushButton:hover { background-color: #2A2A2D; border: 1px solid #FF5722; }
        """
        self.btn_config.setStyleSheet(icon_btn_style)
        self.btn_draw.setStyleSheet(icon_btn_style)

        overlay_layout.addWidget(self.combo_ch, stretch=3)
        overlay_layout.addWidget(self.combo_qld, stretch=1)
        overlay_layout.addWidget(self.combo_fps, stretch=1)
        overlay_layout.addWidget(self.btn_yolo, stretch=0) 
        overlay_layout.addWidget(self.btn_draw, stretch=0)
        overlay_layout.addWidget(self.btn_config, stretch=0)
        
        self.overlay.hide()
        
        self.combo_ch.popupClosed.connect(self._check_hide_overlay)
        self.combo_qld.popupClosed.connect(self._check_hide_overlay)
        self.combo_fps.popupClosed.connect(self._check_hide_overlay)
        
        self.btn_config.clicked.connect(lambda: self.config_clicked_signal.emit(self.slot_id))
        self.btn_yolo.toggled.connect(lambda checked: self.yolo_toggled_signal.emit(self.slot_id, checked))
        self.btn_draw.clicked.connect(lambda: self.drawing_toggled_signal.emit(self.slot_id))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        altura_barra = 65 
        # Menu escuro embaixo
        self.overlay.setGeometry(0, self.height() - altura_barra, self.width(), altura_barra)
        # Botão verde de concluir no topo
        btn_w = 160
        btn_h = 35
        self.btn_finish_draw.setGeometry((self.width() - btn_w) // 2, 20, btn_w, btn_h)

    def enterEvent(self, event):
        # Apenas mostra o hover se NÃO estiver em modo de desenho
        if not self.is_drawing_mode:
            self.overlay.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not (self.combo_ch.view().isVisible() or self.combo_qld.view().isVisible() or self.combo_fps.view().isVisible()):
            self.overlay.hide()
        super().leaveEvent(event)

    def _check_hide_overlay(self):
        if not self.underMouse():
            self.overlay.hide()


class MonitorTab(QWidget):
    def __init__(self, controller: MonitorController):
        super().__init__()
        self.controller = controller
        self.active_workers = {}
        self.camera_configs = {} 
        self.init_ui()
        self._connect_signals()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #121214; }
            QFrame#Panel { background-color: #1C1C1F; border-radius: 24px; }
            QFrame#PortariaCard { background-color: #202024; border-radius: 24px; border: 1px solid transparent; }
            QFrame#PortariaCard:hover { background-color: #252529; border: 1px solid #3A3A3D; }
            QLabel { color: #F2F2F2; font-weight: bold; }
            
            QPushButton#BtnAction { 
                background-color: #2A2A2D; color: #F2F2F2; border-radius: 12px; padding: 12px; font-weight: bold; border: 1px solid #3A3A3D;
            }
            QPushButton#BtnAction:hover { background-color: #3A3A3D; border: 1px solid #FF5722; }
            
            QPushButton#BtnInterfone { 
                background-color: transparent; color: #8A8A8E; border-radius: 12px; padding: 10px; font-weight: bold; border: 1px solid #3A3A3D;
            }
            QPushButton#BtnInterfone:hover { background-color: #2A2A2D; color: #F2F2F2; border: 1px solid #8A8A8E; }

            QScrollBar:vertical { border: none; background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #2A2A2D; border-radius: 4px; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(20)

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
            QFrame#ToggleContainer { background-color: #121214; border-radius: 12px; padding: 4px; }
            QPushButton#ToggleBtn {
                background-color: transparent; color: #8A8A8E; border-radius: 8px; padding: 8px; font-weight: bold; font-size: 12px; border: none;
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

        self.card_veiculos, self.btn_abrir_veiculos, self.lbl_status_veiculos, self.btn_falar_veiculos = self._create_portaria_card("Veículos", "🚗")
        right_vbox.addWidget(self.card_veiculos)

        self.card_pedestres, self.btn_abrir_pedestres, self.lbl_status_pedestres, self.btn_falar_pedestres = self._create_portaria_card("Pedestres", "🚶")
        right_vbox.addWidget(self.card_pedestres)
        
        right_vbox.addStretch()
        self.right_scroll.setWidget(self.right_panel)
        layout.addWidget(self.right_scroll, 3)

    def _create_portaria_card(self, title, icon):
        card = QFrame()
        card.setObjectName("PortariaCard")
        vbox_card = QVBoxLayout(card)
        vbox_card.setContentsMargins(15, 15, 15, 15)
        vbox_card.setSpacing(10)
        
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

        btn_falar = QPushButton("📞 INTERFONE")
        btn_falar.setObjectName("BtnInterfone")
        btn_falar.setCursor(Qt.PointingHandCursor)
        vbox_card.addWidget(btn_falar)
        
        return card, btn_abrir, lbl_status, btn_falar

    def _connect_signals(self):
        self.btn_abrir_veiculos.clicked.connect(lambda: threading.Thread(
            target=self.controller.request_door_open, 
            args=(104, "192.168.0.104", "Veículos", "#4ade80"), 
            daemon=True).start()
        )
        
        self.btn_abrir_pedestres.clicked.connect(lambda: threading.Thread(
            target=self.controller.request_door_open, 
            args=(109, "192.168.0.109", "Pedestres", "#38bdf8"), 
            daemon=True).start()
        )
        self.btn_falar_veiculos.clicked.connect(lambda: self.acionar_interfone("8001@192.168.0.104"))
        self.btn_falar_pedestres.clicked.connect(lambda: self.acionar_interfone("8001@192.168.0.109"))

        self.cam_toggle_group.idClicked.connect(self._handle_porteiro_change)
        
        for i, cell in self.camera_cells.items():
            cell.combo_ch.currentIndexChanged.connect(self._make_handler(i, cell))
            cell.combo_qld.currentIndexChanged.connect(self._make_handler(i, cell))
            cell.combo_fps.currentIndexChanged.connect(self._make_handler(i, cell))
            
            cell.config_clicked_signal.connect(self._open_camera_config)
            cell.yolo_toggled_signal.connect(self._handle_yolo_toggle)
            
            # Conexão do Botão de Desenho com o Controller
            cell.drawing_toggled_signal.connect(self.controller.toggle_drawing_mode)
            
            cell.display.clicked_pos_signal.connect(self._handle_cam_click)
            cell.display.double_clicked_signal.connect(self._handle_cam_double_click)
            
        self.controller.door_status_changed_signal.connect(self.update_door_status)
        
        # Conexão: Escuta o Controller para alterar o estado visual
        self.controller.drawing_mode_changed_signal.connect(self._handle_drawing_mode_change)

    # =========================================================
    # RECEPTOR DO MODO DE DESENHO E ATUALIZAÇÃO VISUAL
    # =========================================================
    def _handle_drawing_mode_change(self, is_drawing, camera_id):
        """Atualiza a interface da célula quando o modo de desenho muda"""
        if camera_id in self.camera_cells:
            cell = self.camera_cells[camera_id]
            cell.is_drawing_mode = is_drawing
            
            if is_drawing:
                cell.overlay.hide()
                cell.btn_finish_draw.show() # Mostra o botão flutuante verde
                cell.setCursor(Qt.CrossCursor)
                cell.setStyleSheet("""
                    QFrame#CamCell { background-color: #2A2A2D; border-radius: 24px; border: 2px dashed #FF5722; }
                """) # Borda tracejada para indicar edição
            else:
                cell.btn_finish_draw.hide() # Esconde o botão flutuante
                cell.setCursor(Qt.ArrowCursor)
                cell.setStyleSheet("""
                    QFrame#CamCell { background-color: #2A2A2D; border-radius: 24px; border: 2px solid transparent; }
                    QFrame#CamCell:hover { border: 2px solid #FF5722; }
                """) # Volta ao normal

    def _open_camera_config(self, slot_id):
        if slot_id not in self.camera_configs:
            self.camera_configs[slot_id] = CameraConfig(slot_id=slot_id)
            
        config = self.camera_configs[slot_id]
        dialog = CameraConfigDialog(config)
        
        if dialog.exec_() == QDialog.Accepted:
            print(f"✅ Configurações da Câmara {slot_id} salvas com sucesso!")
            if slot_id in self.active_workers:
                worker = self.active_workers[slot_id]
                worker.sensitivity = int(config.sensibilidade)
                worker.yolo_conf_threshold = config.yolo_confianca / 100.0 
                worker.yolo_img_size = 320 if "Rápido" in config.yolo_modo else 640
                
                if config.yolo_alvos == "Apenas Pessoas":
                    worker.yolo_classes = [0]
                elif config.yolo_alvos == "Apenas Veículos":
                    worker.yolo_classes = [2, 3, 5, 7] 
                else:
                    worker.yolo_classes = [0, 2, 3, 5, 7] 
                
        dialog.deleteLater()

    def _handle_yolo_toggle(self, slot_id, is_active):
        if slot_id in self.active_workers:
            self.active_workers[slot_id].yolo_enabled = is_active
            status = "ATIVADO" if is_active else "DESATIVADO"
            print(f"🤖 YOLO {status} no Canal {slot_id}")

    def _handle_cam_click(self, slot_id, pos, btn):
        # TRAVA DE SEGURANÇA: Só desenha se a câmara estiver no modo de desenho ativo
        if not self.camera_cells[slot_id].is_drawing_mode:
            return
            
        if slot_id in self.active_workers:
            worker = self.active_workers[slot_id]
            display = self.displays[slot_id]
            
            if worker.actual_w == 0 or worker.actual_h == 0 or display.width() == 0 or display.height() == 0:
                return
                
            x_ratio = worker.actual_w / display.width()
            y_ratio = worker.actual_h / display.height()
            
            real_x = int(pos.x() * x_ratio)
            real_y = int(pos.y() * y_ratio)

            if btn == 1: 
                worker.polygon_pts.append([real_x, real_y])
            elif btn == 2 and len(worker.polygon_pts) > 0: 
                worker.polygon_pts.pop()

    def _handle_cam_double_click(self, slot_id):
        # Limpa o polígono apenas se o modo de desenho estiver ativo
        if self.camera_cells[slot_id].is_drawing_mode and slot_id in self.active_workers:
            self.active_workers[slot_id].polygon_pts.clear()

    def _make_handler(self, slot_id, cell):
        return lambda _: self._handle_camera_channel_change(slot_id, cell)

    def _handle_camera_channel_change(self, slot_id, cell):
        combo_idx = cell.combo_ch.currentIndex()
        subtype = 1 if cell.combo_qld.currentIndex() == 0 else 0
        fps_text = cell.combo_fps.currentText()
        target_fps = int(fps_text.split(" ")[0]) 

        if slot_id in self.active_workers:
            self.active_workers[slot_id].stop()
            del self.active_workers[slot_id]

        if combo_idx == 0:
            self.displays[slot_id].clear()
            self.displays[slot_id].setText("CÂMARA DESLIGADA")
            return

        if combo_idx == 1:
            url = "celular" 
        else:
            url = f"rtsp://recepcao:casablanca7040@192.168.0.47:554/cam/realmonitor?channel={combo_idx - 2}&subtype={subtype}"

        worker = VideoWorker(slot_id, url, target_fps)
        
        if slot_id in self.camera_configs:
            worker.sensitivity = self.camera_configs[slot_id].sensibilidade
            
        worker.yolo_enabled = cell.btn_yolo.isChecked()

        worker.change_pixmap_signal.connect(self._update_display_slot)
        worker.status_signal.connect(self._update_status_label)
        
        worker.presence_signal.connect(self._handle_worker_alarm)
        
        self.active_workers[slot_id] = worker
        worker.start()
        
    def _handle_worker_alarm(self, status, slot_id, frame, labels):
        if status: 
            self.controller.process_alarm(slot_id, frame, labels)

    def _update_display_slot(self, qimg, slot_id):
        if slot_id in self.displays:
            self.displays[slot_id].setPixmap(QPixmap.fromImage(qimg))

    def _update_status_label(self, slot_id, status):
        print(f"Slot {slot_id}: {status}")
        if status == "CONECTANDO...":
            self.displays[slot_id].setText("🔄 CONECTANDO...")

    def _handle_porteiro_change(self, btn_id):
        pass

    def acionar_interfone(self, sip_address):
        print(f"📞 Chamando {sip_address} via MicroSIP...")
        try:
            caminho_microsip = r"C:\Users\portaria\AppData\Local\MicroSIP\MicroSIP.exe" 
            subprocess.Popen([caminho_microsip, sip_address])
        except Exception as e:
            print(f"❌ Erro ao abrir o MicroSIP: {e}")

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