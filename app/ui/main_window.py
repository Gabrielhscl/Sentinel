from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QButtonGroup, 
                             QLineEdit, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

# Importação dos componentes internos
from app.core.monitor_controller import MonitorController
from app.ui.monitor_tab import MonitorTab
from app.ui.history_tab import HistoryTab
from app.ui.logbook_tab import LogbookTab

# Importação do Menu Flutuante
from app.ui.components.profile_menu import ProfileMenu

class MainWindow(QMainWindow):
    def __init__(self, controller: MonitorController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Sentinel Security - Painel de Controle")
        self.resize(1400, 900)
        
        # Carregamos o estilo global
        self._apply_theme()
        self.init_ui()

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121214; }
            
            /* TOP BAR */
            QFrame#TopBar { background-color: transparent; margin: 10px; }
            QLabel#LogoLabel { color: #FFFFFF; font-size: 22px; font-weight: bold; }
            
            /* Navegação Central */
            QFrame#NavContainer { background-color: #1C1C1F; border-radius: 25px; padding: 5px; }
            
            QPushButton#TabBtn {
                background: transparent; color: #8A8A8E; padding: 10px 20px;
                border-radius: 20px; font-weight: bold; font-size: 14px; border: none;
            }
            QPushButton#TabBtn:hover:!checked { color: #FFFFFF; background-color: #2A2A2D; }
            QPushButton#TabBtn:checked { background-color: #FFFFFF; color: #121214; }
            QPushButton#TabBtn:checked:hover { background-color: #E5E5E5; color: #121214; }
            
            /* Barra de Pesquisa */
            QLineEdit#SearchBar {
                background-color: #1C1C1F; border-radius: 20px; padding: 10px 20px;
                color: #FFFFFF; font-size: 13px; min-width: 250px; border: none;
            }

            /* Cards de Conteúdo */
            QFrame#Panel { background-color: #1C1C1F; border-radius: 24px; border: none; }
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
        logo_icon = QLabel("⚡")
        logo_icon.setStyleSheet("color: #FF5722; font-size: 24px;")
        logo_text = QLabel("Sentinel")
        logo_text.setObjectName("LogoLabel")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        top_bar_layout.addLayout(logo_layout)
        
        top_bar_layout.addStretch()

        # 2. Navegação e Busca (Centro)
        search_bar = QLineEdit()
        search_bar.setObjectName("SearchBar")
        search_bar.setPlaceholderText("🔍 Procurar...")
        top_bar_layout.addWidget(search_bar)
        
        top_bar_layout.addSpacing(20)

        nav_container = QFrame()
        nav_container.setObjectName("NavContainer")
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)

        self.btn_monitor = QPushButton("📹 Câmeras")
        self.btn_monitor.setObjectName("TabBtn")
        self.btn_monitor.setCheckable(True)
        self.btn_monitor.setChecked(True)

        self.btn_history = QPushButton("📋 Histórico")
        self.btn_history.setObjectName("TabBtn")
        self.btn_history.setCheckable(True)

        self.btn_lock = QPushButton("🔒 Segurança")
        self.btn_lock.setObjectName("TabBtn")
        self.btn_lock.setCheckable(True)

        self.btn_logbook = QPushButton("📖 Diário")
        self.btn_logbook.setObjectName("TabBtn")
        self.btn_logbook.setCheckable(True)

        self.tab_group = QButtonGroup(self)
        self.tab_group.addButton(self.btn_monitor, 0)
        self.tab_group.addButton(self.btn_history, 1)
        self.tab_group.addButton(self.btn_lock, 2)
        self.tab_group.addButton(self.btn_logbook, 3)
        
        nav_layout.addWidget(self.btn_monitor)
        nav_layout.addWidget(self.btn_history)
        nav_layout.addWidget(self.btn_lock)
        nav_layout.addWidget(self.btn_logbook)
        top_bar_layout.addWidget(nav_container)

        top_bar_layout.addStretch()

        # 3. Perfil e Sistema (Direita)
        actions_layout = QHBoxLayout()
        btn_theme = QPushButton("🌙")
        btn_theme.setFixedSize(40, 40)
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.setStyleSheet("background: #1C1C1F; border-radius: 20px; border: none; color: white;")
        
        self.btn_user = QPushButton("GH") 
        self.btn_user.setFixedSize(40, 40)
        self.btn_user.setCursor(Qt.PointingHandCursor)
        self.btn_user.setStyleSheet("""
            QPushButton {
                background: #2A2A2D; border: 2px solid #FF5722; border-radius: 20px; color: white; font-weight: bold;
            }
            QPushButton:hover { background: #FF5722; }
        """)
        self.btn_user.clicked.connect(self._mostrar_menu_perfil)
        
        actions_layout.addWidget(btn_theme)
        actions_layout.addWidget(self.btn_user)
        top_bar_layout.addLayout(actions_layout)

        main_layout.addWidget(top_bar)

        # --- ÁREA DE CONTEÚDO (STACKED WIDGET) ---
        self.stack = QStackedWidget()
        
        self.tab_monitor = MonitorTab(self.controller)
        self.tab_history = HistoryTab(self.controller)
        self.tab_logbook = LogbookTab(self.controller)
        
        # A ordem aqui define o Index de cada aba
        self.stack.addWidget(self.tab_monitor)  # Index 0
        self.stack.addWidget(self.tab_history)  # Index 1
        self.stack.addWidget(QWidget())         # Index 2 (Espaço reservado para a aba "Segurança" no futuro)
        self.stack.addWidget(self.tab_logbook)  # Index 3
        
        main_layout.addWidget(self.stack)

        # Conectar navegação
        self.tab_group.idClicked.connect(self.stack.setCurrentIndex)

    # ==============================================================================
    # LÓGICA DO MENU DE PERFIL FLUTUANTE
    # ==============================================================================
    def _mostrar_menu_perfil(self):
        self.profile_menu = ProfileMenu(self)
        
        # Mapeia a posição exata da bolinha 'GH' na tela inteira do computador
        pos_bolinha = self.btn_user.mapToGlobal(self.btn_user.rect().bottomRight())
        
        # Calcula a posição X e Y para abrir o menu certinho embaixo e alinhado à direita
        x = pos_bolinha.x() - self.profile_menu.width()
        y = pos_bolinha.y() + 10 # Dá 10px de margem visual abaixo da bolinha
        
        self.profile_menu.move(x, y)
        self.profile_menu.action_clicked.connect(self._processar_acao_menu)
        self.profile_menu.show()

    def _processar_acao_menu(self, acao):
        if acao == "logout":
            print("👋 Encerrando o sistema Sentinel...")
            self.close() 
        elif acao == "logbook":
            # Muda a interface visualmente para a aba de Diário
            self.btn_logbook.setChecked(True)
            self.stack.setCurrentIndex(3)
        elif acao == "lock":
            print("🔒 Tela bloqueada por segurança.")
        elif acao == "profile":
            print("👤 Abrindo configurações de usuário.")
        elif acao == "settings":
            print("⚙️ Abrindo painel de ajustes.")