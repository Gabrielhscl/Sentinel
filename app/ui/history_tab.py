import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QFrame, QLabel, QPushButton, QLineEdit, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

# ==============================================================================
# WIDGET EXTRA: Pop-up de Visualização de Evidência
# ==============================================================================
class ImageViewerDialog(QDialog):
    def __init__(self, image_path, title, parent=None):
        super().__init__(parent, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setWindowTitle(f"Evidência - {title}")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #121214;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Mantém a proporção e suaviza a imagem grande
            pixmap = pixmap.scaled(780, 580, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img.setPixmap(pixmap)
        else:
            lbl_img.setText("⚠️ Imagem original não encontrada no disco.")
            lbl_img.setStyleSheet("color: #FF5722; font-size: 16px;")
            
        layout.addWidget(lbl_img)

# ==============================================================================
# ABA PRINCIPAL DE HISTÓRICO
# ==============================================================================
class HistoryTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self._apply_theme()
        self.init_ui()
        self.load_data()
        self.controller.event_created_signal.connect(self._handle_new_event)

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #121214; }
            
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #2A2A2D; border-radius: 4px; }
            
            /* Estilo da Barra de Pesquisa */
            QLineEdit#SearchBar {
                background-color: #1C1C1F; color: #F2F2F2; padding: 12px 18px; 
                border-radius: 10px; border: 1px solid #2A2A2D; font-size: 14px;
            }
            QLineEdit#SearchBar:focus { border: 1px solid #FF5722; }
            
            /* Estilo dos Cards */
            QFrame#HistoryCard {
                background-color: #1C1C1F; border-radius: 12px; border: 1px solid transparent;
            }
            QFrame#HistoryCard:hover { border: 1px solid #3A3A3D; background-color: #202024;}
            
            QLabel#EventTitle { color: #F2F2F2; font-size: 16px; font-weight: bold; }
            QLabel#EventSource { color: #8A8A8E; font-size: 13px; font-weight: bold;}
            
            /* Tags / Badges */
            QLabel#TagTime { background-color: #2A2A2D; color: #F2F2F2; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;}
            QLabel#TagTelegram { background-color: rgba(46, 204, 113, 0.15); color: #2ecc71; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;}
            
            QLabel#ImageDisplay { background-color: #121214; border-radius: 8px; }
            
            QPushButton#BtnView {
                background-color: #FF5722; color: #FFF; font-weight: bold; padding: 8px; border-radius: 6px; border: none;
            }
            QPushButton#BtnView:hover { background-color: #E64A19; }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # -------------------------------------------------------------
        # 1. CABEÇALHO E FILTROS
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 0)
        
        lbl_title = QLabel("📋 HISTÓRICO DE OCORRÊNCIAS")
        lbl_title.setStyleSheet("color: #F2F2F2; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("🔍 Buscar por Câmera, Ocorrência ou Data...")
        self.search_input.setFixedWidth(350)
        self.search_input.textChanged.connect(self._filter_events)
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedSize(110, 42)
        btn_refresh.setStyleSheet("QPushButton { background-color: #2A2A2D; color: #F2F2F2; border-radius: 10px; font-weight: bold;} QPushButton:hover { background-color: #3A3A3D; }")
        btn_refresh.clicked.connect(self.load_data)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(btn_refresh)
        
        main_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # 2. ÁREA DE SCROLL DOS CARDS
        # -------------------------------------------------------------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(15, 5, 15, 20)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

    # ==============================================================================
    # LÓGICA DE DADOS E FILTRAGEM
    # ==============================================================================
    def load_data(self):
        """Busca do banco e recarrega os cards"""
        self.search_input.clear() # Limpa a busca ao atualizar
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        events = self.controller.db_service.get_recent_events(limit=100)
        
        if not events:
            lbl_empty = QLabel("Nenhuma ocorrência registrada no sistema.")
            lbl_empty.setStyleSheet("color: #8A8A8E; font-size: 14px; font-style: italic;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl_empty)
            return

        for event in events:
            self.add_event_to_ui(event)

    def _filter_events(self, text):
        """Esconde ou mostra os cards com base no que foi digitado na barra"""
        search_term = text.lower()
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            # Pega o termo secreto de busca que salvamos dentro de cada card
            if widget and hasattr(widget, "search_data"):
                if search_term in widget.search_data:
                    widget.show()
                else:
                    widget.hide()

    def _handle_new_event(self, event):
        if self.scroll_layout.count() == 1 and isinstance(self.scroll_layout.itemAt(0).widget(), QLabel):
            self.scroll_layout.itemAt(0).widget().setParent(None)
        self.add_event_to_ui(event, add_at_top=True)

    # ==============================================================================
    # CRIAÇÃO DO CARD VISUAL (Enterprise)
    # ==============================================================================
    def add_event_to_ui(self, event, add_at_top=False):
        card = QFrame()
        card.setObjectName("HistoryCard")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(15)

        str_time = event.timestamp.strftime('%H:%M:%S')
        str_date = event.timestamp.strftime('%d/%m/%Y')
        nome_cam = event.camera.nome if event.camera else f"Canal {event.camera_id}"
        
        # Oculta menções antigas a YOLO caso já existam no banco de dados antigo
        tipo_alvo_limpo = event.tipo_alvo.replace("YOLO", "Inteligente").replace("Movimento/Inteligente", "Movimento Detectado")

        # Injeta os dados no Card para facilitar o Filtro de Pesquisa
        card.search_data = f"{nome_cam} {tipo_alvo_limpo} {str_date} {str_time}".lower()

        # 1. BARRA LATERAL COLORIDA (Indicador Visual)
        color_bar = QFrame()
        color_bar.setFixedWidth(4)
        # Vermelho para Humanos/Veículos, Laranja para Movimento simples
        cor = "#FF3B30" if "Humana" in tipo_alvo_limpo or "Veículo" in tipo_alvo_limpo else "#FF9500"
        color_bar.setStyleSheet(f"background-color: {cor}; border-radius: 2px;")
        card_layout.addWidget(color_bar)

        # 2. INFORMAÇÕES CENTRAIS
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        lbl_title = QLabel(f"🚨 {tipo_alvo_limpo.upper()}")
        lbl_title.setObjectName("EventTitle")
        lbl_source = QLabel(f"📹 {nome_cam}")
        lbl_source.setObjectName("EventSource")

        # Layout das "Tags" (Horário e Status)
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel(f"⏰ {str_date} - {str_time}", objectName="TagTime"))
        tags_layout.addWidget(QLabel("✅ Reportado", objectName="TagTelegram"))
        tags_layout.addStretch()

        info_layout.addWidget(lbl_title)
        info_layout.addWidget(lbl_source)
        info_layout.addLayout(tags_layout)
        info_layout.addStretch()

        card_layout.addLayout(info_layout, stretch=3)

        # 3. IMAGEM E BOTÃO DE AÇÃO
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)
        action_layout.setAlignment(Qt.AlignCenter)
        
        lbl_img = QLabel()
        lbl_img.setObjectName("ImageDisplay")
        lbl_img.setFixedSize(140, 90)
        lbl_img.setAlignment(Qt.AlignCenter)
        
        if event.caminho_foto and os.path.exists(event.caminho_foto):
            pixmap = QPixmap(event.caminho_foto)
            pixmap = pixmap.scaled(140, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            lbl_img.setPixmap(pixmap)
            
            # Só mostra o botão se tiver foto
            btn_view = QPushButton("🔍 Ampliar Imagem")
            btn_view.setObjectName("BtnView")
            btn_view.setCursor(Qt.PointingHandCursor)
            # Aciona a função passando o caminho da imagem
            btn_view.clicked.connect(lambda _, path=event.caminho_foto, t=tipo_alvo_limpo: self._open_image_viewer(path, t))
            
            action_layout.addWidget(lbl_img)
            action_layout.addWidget(btn_view)
        else:
            lbl_img.setText("Sem\nRegistro")
            lbl_img.setStyleSheet("color: #8A8A8E; background-color: #2A2A2D; border-radius: 8px;")
            action_layout.addWidget(lbl_img)

        card_layout.addLayout(action_layout, stretch=1)

        # Adiciona na tela
        if add_at_top:
            self.scroll_layout.insertWidget(0, card)
        else:
            self.scroll_layout.addWidget(card)

    def _open_image_viewer(self, image_path, title):
        """Abre o Popup flutuante para ver a foto em alta resolução"""
        dialog = ImageViewerDialog(image_path, title, self)
        dialog.exec_()