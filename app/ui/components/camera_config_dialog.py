from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
                             QPushButton, QSlider, QComboBox, QSpinBox, QDoubleSpinBox, 
                             QCheckBox, QFrame, QSizePolicy, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from app.models.camera_config import CameraConfig

class CameraConfigDialog(QDialog):
    def __init__(self, config: CameraConfig, parent=None):
        super().__init__(parent) # Removido o None rígido
        self.config = config
        self.setWindowTitle(f"Configuração - Canal {config.slot_id}")
        
        # A MÁGICA COMEÇA AQUI: Em vez de FixedSize, usamos limites inteligentes
        self.setMinimumWidth(500)
        self.setMaximumHeight(800) # Se a tela for menor que isso, o Scroll ativa!
        
        self._apply_theme()
        self._init_ui()
        self._load_current_values()

    def _apply_theme(self):
        self.setStyleSheet("""
            QDialog, QWidget { background-color: #121214; }
            QLabel { color: #F2F2F2; }
            QLabel#Title { font-weight: bold; font-size: 14px; color: #FF5722; }
            QLabel#HelperText { color: #8A8A8E; font-size: 11px; font-style: italic; }
            QLabel#SliderLegend { color: #8A8A8E; font-size: 11px; font-weight: bold; }
            QLabel#SliderDirection { color: #FF5722; font-size: 14px; font-weight: bold; }
            
            QFrame#Group { background-color: #1C1C1F; border-radius: 12px; }
            
            QSlider::groove:horizontal { height: 6px; background: #2A2A2D; border-radius: 3px; }
            QSlider::handle:horizontal { background: #FF5722; width: 16px; margin: -5px 0; border-radius: 8px; }
            
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #2A2A2D; color: #F2F2F2; border-radius: 6px; 
                border: 1px solid #3A3A3D; font-size: 13px; font-weight: bold; padding-left: 10px;
            }
            QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #FF5722; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2A2A2D; color: #F2F2F2; selection-background-color: #FF5722; border: 1px solid #3A3A3D;
            }
            
            QCheckBox { color: #F2F2F2; font-weight: bold; font-size: 13px; }
            QCheckBox::indicator { width: 22px; height: 22px; border-radius: 5px; background: #2A2A2D; border: 1px solid #3A3A3D;}
            QCheckBox::indicator:checked { background: #FF5722; border: 1px solid #FF5722; image: url(none); }
            
            QPushButton#BtnSave {
                background-color: #FF5722; color: #FFFFFF; font-weight: bold; font-size: 14px; border-radius: 8px; 
            }
            QPushButton#BtnSave:hover { background-color: #E64A19; }
            
            QPushButton#BtnCancel {
                background-color: transparent; color: #8A8A8E; font-weight: bold; font-size: 14px;
                border-radius: 8px; border: 1px solid #3A3A3D;
            }
            QPushButton#BtnCancel:hover { background-color: #2A2A2D; color: #F2F2F2; }

            /* ESTILO DA BARRA DE SCROLL INVISÍVEL E ELEGANTE */
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #3A3A3D; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #FF5722; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

    def _init_ui(self):
        # Layout Principal da Janela
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Zero margens para o scroll preencher as bordas
        main_layout.setSpacing(0)

        # =========================================================
        # 1. ÁREA DE ROLAGEM (SCROLL AREA) - O Formulário
        # =========================================================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Sem barra para os lados
        
        self.container = QWidget()
        self.layout_form = QVBoxLayout(self.container)
        self.layout_form.setSpacing(15) 
        self.layout_form.setContentsMargins(20, 20, 20, 20)

        # CABEÇALHO (Agora dentro da área de rolagem)
        lbl_header = QLabel(f"AJUSTES DO CANAL {self.config.slot_id}")
        lbl_header.setAlignment(Qt.AlignCenter)
        lbl_header.setStyleSheet("color: #FF5722; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        self.layout_form.addWidget(lbl_header)

        # GRUPO 1: SENSIBILIDADE
        group_det = QFrame()
        group_det.setObjectName("Group")
        lyt_det = QVBoxLayout(group_det)
        lyt_det.setContentsMargins(15, 15, 15, 15)
        
        lyt_det.addWidget(QLabel("🎯 Calibragem de Detecção", objectName="Title"))
        lyt_det.addWidget(QLabel("Ajuste a força necessária para disparar o alarme.", objectName="HelperText"))
        lyt_det.addSpacing(10)
        
        self.slider_sens = QSlider(Qt.Horizontal)
        self.slider_sens.setRange(100, 5000)
        self.slider_sens.setInvertedAppearance(True)
        self.slider_sens.setFixedHeight(30) 
        lyt_det.addWidget(self.slider_sens)
        
        slider_labels = QHBoxLayout()
        slider_labels.setContentsMargins(0, 0, 0, 0)
        
        lyt_min = QVBoxLayout()
        lbl_min_dir = QLabel("⬅️ MENOS SENSÍVEL")
        lbl_min_dir.setObjectName("SliderDirection")
        lbl_min_desc = QLabel("Ignora pequenos movimentos\n(folhas, insetos)")
        lbl_min_desc.setObjectName("SliderLegend")
        lyt_min.addWidget(lbl_min_dir)
        lyt_min.addWidget(lbl_min_desc)
        
        lyt_max = QVBoxLayout()
        lbl_max_dir = QLabel("MAIS SENSÍVEL ➡️")
        lbl_max_dir.setObjectName("SliderDirection")
        lbl_max_dir.setAlignment(Qt.AlignRight)
        lbl_max_desc = QLabel("Detecta qualquer variação\n(sombras, poeira)")
        lbl_max_desc.setObjectName("SliderLegend")
        lbl_max_desc.setAlignment(Qt.AlignRight)
        lyt_max.addWidget(lbl_max_dir)
        lyt_max.addWidget(lbl_max_desc)

        slider_labels.addLayout(lyt_min)
        slider_labels.addStretch()
        slider_labels.addLayout(lyt_max)
        
        lyt_det.addLayout(slider_labels)
        self.layout_form.addWidget(group_det)

        # GRUPO 2: EVIDÊNCIAS
        group_evd = QFrame()
        group_evd.setObjectName("Group")
        lyt_evd = QVBoxLayout(group_evd)
        lyt_evd.setContentsMargins(15, 15, 15, 15)
        lyt_evd.setSpacing(15)
        
        lyt_evd.addWidget(QLabel("📱 Envio de Evidências", objectName="Title"))
        lyt_evd.addWidget(QLabel("O que enviar no Telegram ao detectar algo?", objectName="HelperText"))
        
        self.combo_evidencia = QComboBox()
        self.combo_evidencia.addItems(["Apenas Foto", "Apenas Vídeo", "Foto + Vídeo"])
        self.combo_evidencia.setFixedHeight(35) 
        
        self.spin_tempo_video = QSpinBox()
        self.spin_tempo_video.setSuffix(" segundos")
        self.spin_tempo_video.setRange(3, 30)
        self.spin_tempo_video.setFixedHeight(35) 
        
        row_formato = QHBoxLayout()
        lbl_tipo = QLabel("Formato:")
        lbl_tipo.setFixedWidth(130) 
        row_formato.addWidget(lbl_tipo)
        row_formato.addWidget(self.combo_evidencia)
        lyt_evd.addLayout(row_formato)
        
        row_duracao = QHBoxLayout()
        lbl_tam = QLabel("Duração do Vídeo:")
        lbl_tam.setFixedWidth(130)
        row_duracao.addWidget(lbl_tam)
        row_duracao.addWidget(self.spin_tempo_video)
        lyt_evd.addLayout(row_duracao)

        self.layout_form.addWidget(group_evd)

        # GRUPO 3: ATRASOS
        group_delays = QFrame()
        group_delays.setObjectName("Group")
        lyt_delays = QVBoxLayout(group_delays)
        lyt_delays.setContentsMargins(15, 15, 15, 15)
        lyt_delays.setSpacing(15)
        
        lyt_delays.addWidget(QLabel("⏱️ Temporizadores de Captura", objectName="Title"))
        lyt_delays.addWidget(QLabel("Tempo de espera antes da gravação.", objectName="HelperText"))
        
        self.spin_atraso_foto = QDoubleSpinBox()
        self.spin_atraso_foto.setSuffix(" seg")
        self.spin_atraso_foto.setRange(0.0, 10.0)
        self.spin_atraso_foto.setSingleStep(0.5)
        self.spin_atraso_foto.setFixedHeight(35) 

        self.spin_atraso_video = QDoubleSpinBox()
        self.spin_atraso_video.setSuffix(" seg")
        self.spin_atraso_video.setRange(0.0, 10.0)
        self.spin_atraso_video.setSingleStep(0.5)
        self.spin_atraso_video.setFixedHeight(35) 

        row_foto = QHBoxLayout()
        lbl_foto = QLabel("Atraso da Foto:")
        lbl_foto.setFixedWidth(130)
        row_foto.addWidget(lbl_foto)
        row_foto.addWidget(self.spin_atraso_foto)
        lyt_delays.addLayout(row_foto)

        row_video = QHBoxLayout()
        lbl_video = QLabel("Atraso do Vídeo:")
        lbl_video.setFixedWidth(130)
        row_video.addWidget(lbl_video)
        row_video.addWidget(self.spin_atraso_video)
        lyt_delays.addLayout(row_video)
        
        self.layout_form.addWidget(group_delays)

        # GRUPO 4: ALARME CRÍTICO
        group_alarm = QFrame()
        group_alarm.setObjectName("Group")
        lyt_alarm = QVBoxLayout(group_alarm)
        lyt_alarm.setContentsMargins(15, 15, 15, 15)
        
        self.check_critico = QCheckBox(" 🚨 Alarme Crítico")
        self.check_critico.setFixedHeight(30) 
        lyt_alarm.addWidget(self.check_critico)
        lyt_alarm.addWidget(QLabel("Notificação sonora mesmo se o celular estiver no silencioso.", objectName="HelperText"))
        
        self.layout_form.addWidget(group_alarm)

        # GRUPO 5: INTELIGÊNCIA ARTIFICIAL (YOLO)
        group_ia = QFrame()
        group_ia.setObjectName("Group")
        lyt_ia = QVBoxLayout(group_ia)
        lyt_ia.setContentsMargins(15, 15, 15, 15)
        lyt_ia.setSpacing(15)
        
        lyt_ia.addWidget(QLabel("🤖 Inteligência Artificial (YOLO)", objectName="Title"))
        lyt_ia.addWidget(QLabel("Parâmetros do motor neural quando o YOLO estiver ativado.", objectName="HelperText"))
        
        form_ia = QFormLayout()
        form_ia.setVerticalSpacing(16)
        form_ia.setHorizontalSpacing(15)

        self.combo_alvos = QComboBox()
        self.combo_alvos.addItems(["Apenas Pessoas", "Apenas Veículos", "Pessoas e Veículos"])
        self.combo_alvos.setFixedHeight(35)

        self.spin_confianca = QSpinBox()
        self.spin_confianca.setSuffix("% de certeza")
        self.spin_confianca.setRange(10, 90) 
        self.spin_confianca.setSingleStep(5)
        self.spin_confianca.setFixedHeight(35)

        self.combo_modo_ia = QComboBox()
        self.combo_modo_ia.addItems(["Rápido (Baixo Consumo CPU)", "Preciso (Alta Resolução)"])
        self.combo_modo_ia.setFixedHeight(35)

        lbl_alvo = QLabel("O que detectar?:")
        lbl_alvo.setFixedWidth(130)
        lbl_conf = QLabel("Confiança Mínima:")
        lbl_conf.setFixedWidth(130)
        lbl_modo = QLabel("Processamento:")
        lbl_modo.setFixedWidth(130)

        form_ia.addRow(lbl_alvo, self.combo_alvos)
        form_ia.addRow(lbl_conf, self.spin_confianca)
        form_ia.addRow(lbl_modo, self.combo_modo_ia)
        
        lyt_ia.addLayout(form_ia)
        self.layout_form.addWidget(group_ia) 

        # Adiciona o Scroll para a tela inteira
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        # =========================================================
        # 2. RODAPÉ FIXO COM OS BOTÕES DE AÇÃO
        # =========================================================
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: #1C1C1F; border-top: 1px solid #2A2A2D;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 15, 20, 15)
        bottom_layout.setSpacing(20)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("BtnCancel")
        self.btn_cancel.setFixedHeight(45) 
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Salvar Ajustes")
        self.btn_save.setObjectName("BtnSave")
        self.btn_save.setFixedHeight(45) 
        self.btn_save.clicked.connect(self._save_and_accept)
        
        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addWidget(self.btn_save)
        
        main_layout.addWidget(bottom_frame)

    def _load_current_values(self):
        self.slider_sens.setValue(self.config.sensibilidade)
        self.combo_evidencia.setCurrentText(self.config.modo_evidencia)
        self.spin_tempo_video.setValue(self.config.tempo_video_s)
        self.spin_atraso_foto.setValue(self.config.atraso_foto_ms / 1000.0)
        self.spin_atraso_video.setValue(self.config.atraso_video_ms / 1000.0)
        self.check_critico.setChecked(self.config.alerta_critico)
        
        self.combo_alvos.setCurrentText(self.config.yolo_alvos)
        self.spin_confianca.setValue(self.config.yolo_confianca)
        self.combo_modo_ia.setCurrentText(self.config.yolo_modo)

    def _save_and_accept(self, checked=False):
        self.btn_save.setEnabled(False) 
        try:
            self.config.sensibilidade = int(self.slider_sens.value())
            self.config.modo_evidencia = str(self.combo_evidencia.currentText())
            self.config.tempo_video_s = int(self.spin_tempo_video.value())
            self.config.atraso_foto_ms = int(float(self.spin_atraso_foto.value()) * 1000)
            self.config.atraso_video_ms = int(float(self.spin_atraso_video.value()) * 1000)
            self.config.alerta_critico = bool(self.check_critico.isChecked())
            
            self.config.yolo_alvos = str(self.combo_alvos.currentText())
            self.config.yolo_confianca = int(self.spin_confianca.value())
            self.config.yolo_modo = str(self.combo_modo_ia.currentText())
            
            super().accept()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ ERRO CRÍTICO AO SALVAR DADOS: {e}")
            self.btn_save.setEnabled(True)