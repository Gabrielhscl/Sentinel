from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QButtonGroup, 
                             QLineEdit, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from app.core.monitor_controller import MonitorController
from app.ui.monitor_tab import MonitorTab
from app.ui.history_tab import HistoryTab

class MainWindow(QMainWindow):
    def __init__(self, controller: MonitorController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("EvoHaus Security - Painel de Controle")
        self.resize(1400, 900)
        
        # Carregamos o estilo global
        self._apply_theme()
        self.init_ui()

    def _apply_theme(self):
        # Cores baseadas na imagem de referência
        self.setStyleSheet("""
            QMainWindow { background-color: #121214; }
            
            /* TOP BAR */
            QFrame#TopBar { 
                background-color: transparent; 
                margin: 10px;
            }
            
            QLabel#LogoLabel {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
            }
            
            /* Navegação Central */
            QFrame#NavContainer {
                background-color: #1C1C1F;
                border-radius: 25px;
                padding: 5px;
            }
            
            QPushButton#TabBtn {
                background: transparent;
                color: #8A8A8E;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            
            /* Quando passa o mouse E NÃO está selecionado */
            QPushButton#TabBtn:hover:!checked {
                color: #FFFFFF;
                background-color: #2A2A2D;
                border-radius: 20px;
            }

            /* Quando ESTÁ selecionado */
            QPushButton#TabBtn:checked {
                background-color: #FFFFFF;
                color: #121214;
                border-radius: 20px;
            }
            
            /* Quando ESTÁ selecionado E passa o mouse por cima */
            QPushButton#TabBtn:checked:hover {
                background-color: #E5E5E5; /* Um branco levemente escurecido */
                color: #121214;
                border-radius: 20px;
            }
            /* Barra de Pesquisa Estilo Sentinel */
            QLineEdit#SearchBar {
                background-color: #1C1C1F;
                border-radius: 20px;
                padding: 10px 20px;
                color: #FFFFFF;
                font-size: 13px;
                min-width: 250px;
                border: none;
            }

            /* Cards de Conteúdo */
            QFrame#Panel { 
                background-color: #1C1C1F; 
                border-radius: 24px;
                border: none;
            }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(10)

        # --- CONSTRUÇÃO DA TOP BAR ---
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Logo (Esquerda)
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("⚡") # Substituir por QIcon se tiver
        logo_icon.setStyleSheet("color: #FF5722; font-size: 24px;")
        logo_text = QLabel("Sentinel")
        logo_text.setObjectName("LogoLabel")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        top_bar_layout.addLayout(logo_layout)
        
        top_bar_layout.addStretch()

        # 2. Navegação e Busca (Centro)
        # Barra de Busca
        search_bar = QLineEdit()
        search_bar.setObjectName("SearchBar")
        search_bar.setPlaceholderText("🔍 Search here...")
        top_bar_layout.addWidget(search_bar)
        
        top_bar_layout.addSpacing(20)

        # Container de Botões (O "Neumorfismo" central)
        nav_container = QFrame()
        nav_container.setObjectName("NavContainer")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)

        self.btn_monitor = QPushButton("📹 Cameras")
        self.btn_monitor.setObjectName("TabBtn")
        self.btn_monitor.setCheckable(True)
        self.btn_monitor.setChecked(True)

        self.btn_history = QPushButton("📋 History")
        self.btn_history.setObjectName("TabBtn")
        self.btn_history.setCheckable(True)

        self.btn_lock = QPushButton("🔒 Security")
        self.btn_lock.setObjectName("TabBtn")
        self.btn_lock.setCheckable(True)

        self.tab_group = QButtonGroup(self)
        self.tab_group.addButton(self.btn_monitor, 0)
        self.tab_group.addButton(self.btn_history, 1)
        self.tab_group.addButton(self.btn_lock, 2)

        nav_layout.addWidget(self.btn_monitor)
        nav_layout.addWidget(self.btn_history)
        nav_layout.addWidget(self.btn_lock)
        top_bar_layout.addWidget(nav_container)

        top_bar_layout.addStretch()

        # 3. Perfil e Sistema (Direita)
        actions_layout = QHBoxLayout()
        btn_theme = QPushButton("🌙")
        btn_theme.setFixedSize(40, 40)
        btn_theme.setStyleSheet("background: #1C1C1F; border-radius: 20px; border: none; color: white;")
        
        btn_user = QPushButton("GH") # Iniciais do Gabriel Henrique
        btn_user.setFixedSize(40, 40)
        btn_user.setStyleSheet("background: #2A2A2D; border: 2px solid #FF5722; border-radius: 20px; color: white; font-weight: bold;")
        
        actions_layout.addWidget(btn_theme)
        actions_layout.addWidget(btn_user)
        top_bar_layout.addLayout(actions_layout)

        main_layout.addWidget(top_bar)

        # --- ÁREA DE CONTEÚDO (STACKED WIDGET) ---
        self.stack = QStackedWidget()
        self.tab_monitor = MonitorTab(self.controller)
        self.tab_history = HistoryTab(self.controller)
        
        self.stack.addWidget(self.tab_monitor)
        self.stack.addWidget(self.tab_history)
        # Adicionar aba de segurança se houver
        
        main_layout.addWidget(self.stack)

        # Conectar navegação
        self.tab_group.idClicked.connect(self.stack.setCurrentIndex)