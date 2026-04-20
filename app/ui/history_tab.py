from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from app.core.monitor_controller import MonitorController
from app.models.event_model import SecurityEvent

class HistoryTab(QWidget):
    def __init__(self, controller: MonitorController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.load_data()
        
        # Escuta o Controller: sempre que um novo evento for criado (ex: detecção), atualiza a lista
        self.controller.event_created_signal.connect(self.add_event_to_ui)

    def init_ui(self):
        # Aplica o Estilo Global da Aba (EvoHaus Dark Theme)
        self.setStyleSheet("""
            QWidget { background-color: #121214; }
            
            QListWidget { 
                background-color: #1C1C1F; 
                border: none; 
                border-radius: 24px; 
                padding: 15px;
                outline: none;
            }
            
            /* Estilo da barra de rolagem */
            QScrollBar:vertical {
                border: none;
                background: #1C1C1F;
                width: 10px;
                border-radius: 5px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #2A2A2D;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3A3A3D;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)
        
        self.history_list = QListWidget()
        self.history_list.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.history_list)

    def load_data(self):
        # Solicita os dados do banco através da camada de serviço apropriada
        events = self.controller.db_service.get_recent_events(limit=100)
        for event in events:
            self.add_event_to_ui(event)

    def add_event_to_ui(self, event: SecurityEvent):
        item = QListWidgetItem()
        widget = QWidget()
        
        # Estilo para cada "linha" de evento
        widget.setStyleSheet("""
            QWidget {
                background-color: #2A2A2D; 
                border-radius: 12px;
            }
            QLabel { background: transparent; }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Hora do evento
        lbl_time = QLabel(event.time)
        lbl_time.setStyleSheet("color: #8A8A8E; font-size: 13px; font-weight: bold;")
        lbl_time.setFixedWidth(60)
        
        # Tag do evento (A cor vem do banco, vamos garantir que o texto fica legível)
        lbl_tag = QLabel(event.tag)
        lbl_tag.setAlignment(Qt.AlignCenter)
        lbl_tag.setFixedWidth(80)
        
        # Se a cor da tag for muito clara, o texto tem de ser escuro
        text_color = "#121214" if event.color in ["#c9f158", "#e2e4e8", "#4ade80", "#38bdf8"] else "#F2F2F2"
        
        lbl_tag.setStyleSheet(f"""
            background-color: {event.color}; 
            color: {text_color}; 
            padding: 5px; 
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        
        # Mensagem do evento
        lbl_msg = QLabel(event.msg)
        lbl_msg.setStyleSheet("color: #F2F2F2; font-size: 14px; font-weight: bold;")
        
        layout.addWidget(lbl_time)
        layout.addWidget(lbl_tag)
        layout.addWidget(lbl_msg)
        layout.addStretch()
        
        # Definir o tamanho do item na lista
        item.setSizeHint(widget.sizeHint())
        
        # Insere no topo da lista (evento mais recente em cima)
        self.history_list.insertItem(0, item)
        self.history_list.setItemWidget(item, widget)