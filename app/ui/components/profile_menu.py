from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class ProfileMenu(QWidget):
    # Sinais para avisar a janela principal qual ação foi escolhida
    action_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        # A flag Qt.Popup é o segredo: faz o widget flutuar e sumir ao clicar fora!
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setFixedSize(260, 340)
        self._init_ui()

    def _init_ui(self):
        # O Fundo do Card (Transparente na base para permitir a sombra/arredondamento)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # O Container Visual (Onde aplicamos o CSS)
        container = QFrame()
        container.setObjectName("MenuContainer")
        container.setStyleSheet("""
            QFrame#MenuContainer {
                background-color: #1C1C1F;
                border: 1px solid #3A3A3D;
                border-radius: 16px;
            }
            QLabel#NameLabel { color: #F2F2F2; font-weight: bold; font-size: 16px; }
            QLabel#RoleLabel { color: #8A8A8E; font-size: 12px; font-weight: bold; }
            QFrame#Divider { background-color: #2A2A2D; max-height: 1px; }
            
            /* Estilo dos Botões do Menu */
            QPushButton.MenuBtn {
                background-color: transparent; color: #F2F2F2; font-size: 14px; font-weight: bold;
                text-align: left; padding: 12px 15px; border-radius: 8px; border: none;
            }
            QPushButton.MenuBtn:hover { background-color: #2A2A2D; color: #FF5722; }
            
            /* Botão de Logout tem destaque visual */
            QPushButton#LogoutBtn {
                background-color: transparent; color: #FF5722; font-size: 14px; font-weight: bold;
                text-align: left; padding: 12px 15px; border-radius: 8px; border: none;
            }
            QPushButton#LogoutBtn:hover { background-color: rgba(255, 87, 34, 0.1); }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)

        # -------------------------------------------------------------
        # CABEÇALHO DO PERFIL (Avatar, Nome e Função)
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Avatar Circular (Bolinha laranja com iniciais)
        avatar = QLabel("GH")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(46, 46)
        avatar.setStyleSheet("background-color: #FF5722; color: white; border-radius: 23px; font-weight: bold; font-size: 18px;")
        
        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        lbl_name = QLabel("Gabriel Henrique", objectName="NameLabel")
        lbl_role = QLabel("Recepção / Operador", objectName="RoleLabel")
        text_layout.addWidget(lbl_name)
        text_layout.addWidget(lbl_role)
        text_layout.addStretch()
        
        header_layout.addWidget(avatar)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(5)

        # Linha Divisória
        divider1 = QFrame(objectName="Divider")
        layout.addWidget(divider1)
        layout.addSpacing(5)

        # -------------------------------------------------------------
        # BOTÕES DE AÇÃO
        # -------------------------------------------------------------
        btn_profile = self._create_btn("👤 Meu Perfil", "profile")
        btn_logbook = self._create_btn("📝 Diário de Turno", "logbook")
        btn_settings = self._create_btn("⚙️ Ajustes do Sistema", "settings")
        btn_lock = self._create_btn("🔒 Bloquear Tela", "lock")
        
        layout.addWidget(btn_profile)
        layout.addWidget(btn_logbook)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_lock)

        layout.addSpacing(5)
        divider2 = QFrame(objectName="Divider")
        layout.addWidget(divider2)
        layout.addSpacing(5)

        # Botão Sair
        btn_logout = QPushButton("🚪 Sair do Sistema")
        btn_logout.setObjectName("LogoutBtn")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(lambda: self.action_clicked.emit("logout"))
        layout.addWidget(btn_logout)
        

        main_layout.addWidget(container)

    def _create_btn(self, text, action_code):
        btn = QPushButton(text)
        btn.setProperty("class", "MenuBtn")
        btn.setCursor(Qt.PointingHandCursor)
        # Emite o sinal com o código da ação para a tela principal capturar
        btn.clicked.connect(lambda: self.action_clicked.emit(action_code))
        # Fecha o menu automaticamente após clicar em qualquer opção
        btn.clicked.connect(self.close)
        return btn