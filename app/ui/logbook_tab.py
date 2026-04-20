from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QFrame, QLabel, QPushButton, QTextEdit, QComboBox, 
                             QSizePolicy, QApplication, QDialog, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
from datetime import datetime

# =========================================================
# WIDGET EXTRA: Pop-up de Edição
# =========================================================
class EditLogDialog(QDialog):
    def __init__(self, log, parent=None):
        super().__init__(parent, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setWindowTitle("✏️ Editar Registro")
        self.setFixedSize(450, 260)
        self.setStyleSheet("""
            QDialog { background-color: #1C1C1F; }
            QLabel { color: #F2F2F2; font-weight: bold; font-size: 13px; }
            QTextEdit { background-color: #121214; color: #F2F2F2; border: 1px solid #3A3A3D; border-radius: 8px; padding: 8px; font-size: 14px; }
            QComboBox { background-color: #2A2A2D; color: #F2F2F2; border-radius: 6px; padding: 5px 10px; font-size: 13px; font-weight: bold;}
            QPushButton { background-color: #FF5722; color: white; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 13px; }
            QPushButton:hover { background-color: #E64A19; }
        """)
        
        layout = QVBoxLayout(self)
        
        self.txt_msg = QTextEdit()
        self.txt_msg.setPlainText(log.mensagem)
        
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(["Geral", "Troca de Turno", "Incidente", "Manutenção"])
        self.combo_cat.setCurrentText(log.categoria)
        
        btn_save = QPushButton("Salvar Alterações")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.accept)
        
        layout.addWidget(QLabel("Mensagem do Diário:"))
        layout.addWidget(self.txt_msg)
        layout.addWidget(QLabel("Categoria:"))
        layout.addWidget(self.combo_cat)
        layout.addSpacing(10)
        layout.addWidget(btn_save)

    def get_data(self):
        return self.txt_msg.toPlainText().strip(), self.combo_cat.currentText()

# =========================================================
# ABA PRINCIPAL DO DIÁRIO
# =========================================================
class LogbookTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Simulando o usuário autenticado atualmente no sistema
        self.current_user = "Gabriel Henrique" 
        
        self._apply_theme()
        self._init_ui()
        self.load_logs()
        self.controller.log_entry_added_signal.connect(self._refresh_logs_safe)

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #121214; }
            
            /* Filtros de Pesquisa */
            QLineEdit#SearchBar {
                background-color: #1C1C1F; color: #F2F2F2; padding: 10px 15px; 
                border-radius: 8px; border: 1px solid #2A2A2D; font-size: 13px;
            }
            QLineEdit#SearchBar:focus { border: 1px solid #FF5722; }
            QComboBox#FilterCat {
                background-color: #1C1C1F; color: #F2F2F2; border-radius: 8px; 
                border: 1px solid #2A2A2D; font-size: 13px; font-weight: bold; padding: 5px 10px;
            }
            
            /* Área de Digitação */
            QFrame#InputArea { background-color: #1C1C1F; border-radius: 16px; border: 1px solid #3A3A3D; }
            QFrame#InputArea:focus-within { border: 1px solid #FF5722; }
            QTextEdit#LogInput { background-color: transparent; color: #F2F2F2; border: none; font-size: 14px; }
            QComboBox#ComboCat { background-color: #2A2A2D; color: #F2F2F2; border-radius: 8px; border: none; font-size: 13px; font-weight: bold; padding: 5px 10px; }
            QPushButton#BtnSave { background-color: #FF5722; color: #FFFFFF; font-weight: bold; font-size: 14px; border-radius: 8px; border: none; }
            QPushButton#BtnSave:hover { background-color: #E64A19; }
            
            /* Área de Scroll (Feed) */
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #2A2A2D; border-radius: 4px; }
            
            /* Estilo dos Cards */
            QFrame#LogCard { background-color: #1C1C1F; border-radius: 12px; border: 1px solid #2A2A2D; }
            QFrame#LogCard:hover { border: 1px solid #3A3A3D; background-color: #202024; }
            QLabel#LogAuthor { color: #F2F2F2; font-weight: bold; font-size: 15px; }
            QLabel#LogTime { color: #8A8A8E; font-size: 12px; font-weight: bold; }
            QLabel#LogText { color: #D1D1D6; font-size: 14px; }
            QLabel#TagBase { border-radius: 6px; font-size: 11px; font-weight: bold; padding: 4px 8px; }
            
            /* Botões de Ação do Card */
            QPushButton#ActionBtn { background: transparent; border: none; font-size: 14px; }
            QPushButton#ActionBtn:hover { background: #2A2A2D; border-radius: 6px; }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # =========================================================
        # 1. CABEÇALHO COM FILTROS DE PESQUISA
        # =========================================================
        header_layout = QHBoxLayout()
        
        lbl_feed = QLabel("📋 Diário de Turno")
        lbl_feed.setStyleSheet("color: #8A8A8E; font-size: 16px; font-weight: bold; margin-left: 5px;")
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("🔍 Buscar por autor, palavra-chave ou data...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self._filter_logs)
        
        self.filter_cat = QComboBox()
        self.filter_cat.setObjectName("FilterCat")
        self.filter_cat.addItems(["Todas as Categorias", "Geral", "Troca de Turno", "Incidente", "Manutenção"])
        self.filter_cat.setFixedWidth(160)
        self.filter_cat.setFixedHeight(38)
        self.filter_cat.currentTextChanged.connect(self._filter_logs)

        header_layout.addWidget(lbl_feed)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.filter_cat)
        
        main_layout.addLayout(header_layout)

        # =========================================================
        # 2. ÁREA DA LINHA DO TEMPO (SCROLL)
        # =========================================================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.log_list_layout = QVBoxLayout(self.container)
        self.log_list_layout.setContentsMargins(5, 10, 5, 20)
        self.log_list_layout.setSpacing(12)
        self.log_list_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll, stretch=1)

        # =========================================================
        # 3. ÁREA DE INPUT DE NOVA OCORRÊNCIA
        # =========================================================
        input_frame = QFrame()
        input_frame.setObjectName("InputArea")
        input_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum) 
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)
        
        self.txt_input = QTextEdit()
        self.txt_input.setObjectName("LogInput")
        self.txt_input.setPlaceholderText("Escreva os detalhes da ocorrência...")
        self.txt_input.setFixedHeight(50) 
        
        btn_row = QHBoxLayout()
        self.combo_cat = QComboBox()
        self.combo_cat.setObjectName("ComboCat")
        self.combo_cat.addItems(["Geral", "Troca de Turno", "Incidente", "Manutenção"])
        self.combo_cat.setFixedWidth(160)
        self.combo_cat.setFixedHeight(35)
        
        self.btn_save = QPushButton("📝 Registrar")
        self.btn_save.setObjectName("BtnSave")
        self.btn_save.setFixedSize(140, 35)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_log)
        
        btn_row.addWidget(self.combo_cat)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        
        input_layout.addWidget(self.txt_input)
        input_layout.addLayout(btn_row)
        main_layout.addWidget(input_frame)

    # =========================================================
    # LÓGICA DE DADOS, FILTRAGEM E SINCRONIZAÇÃO
    # =========================================================
    def load_logs(self):
        for i in reversed(range(self.log_list_layout.count())):
            widget = self.log_list_layout.itemAt(i).widget()
            if widget: 
                widget.setParent(None)
                widget.deleteLater()
            
        logs = self.controller.db_service.get_all_logs(limit=200) # Aumentei o limite para ter mais histórico
        
        if not logs:
            lbl_empty = QLabel("O Diário de Turno está vazio.")
            lbl_empty.setStyleSheet("color: #8A8A8E; font-size: 14px; font-style: italic; margin-top: 20px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.log_list_layout.addWidget(lbl_empty)
            return

        for log in logs:
            self._add_log_card(log)
            
        # Reaplica os filtros caso a tela seja recarregada enquanto há algo digitado na busca
        self._filter_logs()

    def _filter_logs(self):
        """Esconde ou mostra os cards com base na busca e na categoria selecionada"""
        search_term = self.search_input.text().lower()
        selected_category = self.filter_cat.currentText()
        
        for i in range(self.log_list_layout.count()):
            widget = self.log_list_layout.itemAt(i).widget()
            
            # Verifica se é um card válido (ignora labels de erro/vazio)
            if widget and hasattr(widget, "search_data"):
                match_category = (selected_category == "Todas as Categorias" or widget.log_category == selected_category)
                match_text = (search_term in widget.search_data)
                
                # Só mostra se bater com a busca de texto E com a categoria
                widget.setVisible(match_category and match_text)

    def _save_log(self):
        txt = self.txt_input.toPlainText().strip()
        if not txt: return 
        self.btn_save.setEnabled(False)
        self.controller.salvar_log_do_turno(txt, self.combo_cat.currentText())
        
        # Limpa tudo para mostrar o novo registro recém-criado
        self.txt_input.clear()
        self.search_input.clear()
        self.filter_cat.setCurrentIndex(0) 
        self.btn_save.setEnabled(True)

    def _refresh_logs_safe(self, success):
        if success:
            self.load_logs()
            self.container.adjustSize()
            QApplication.processEvents() 
            self.scroll.verticalScrollBar().setValue(0)

    # =========================================================
    # AÇÕES DO CARD (EDITAR E APAGAR)
    # =========================================================
    def _edit_log(self, log):
        dialog = EditLogDialog(log, self)
        if dialog.exec_() == QDialog.Accepted:
            nova_msg, nova_cat = dialog.get_data()
            if nova_msg and nova_msg != log.mensagem or nova_cat != log.categoria:
                self.controller.editar_log_do_turno(log.id, nova_msg, nova_cat)

    def _delete_log(self, log):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("🗑️ Confirmar Exclusão")
        msg_box.setText(f"Tem certeza que deseja apagar o registro de {log.timestamp.strftime('%H:%M')}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("QMessageBox { background-color: #1C1C1F; color: white; } QLabel { color: white; font-size: 13px; } QPushButton { background-color: #FF5722; color: white; font-weight: bold; padding: 6px 15px; border-radius: 6px; }")
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.controller.apagar_log_do_turno(log.id)

    # =========================================================
    # RENDERIZAÇÃO DO CARD
    # =========================================================
    def _add_log_card(self, log):
        card = QFrame()
        card.setObjectName("LogCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(8)
        
        # INJETANDO OS DADOS PARA O FILTRO MÁGICO FUNCIONAR
        card.log_category = log.categoria
        card.search_data = f"{log.operador} {log.categoria} {log.mensagem} {log.timestamp.strftime('%d/%m/%Y %H:%M')}".lower()
        
        header = QHBoxLayout()
        lbl_user = QLabel(f"👤 {log.operador}")
        lbl_user.setObjectName("LogAuthor")
        
        data_f = log.timestamp.strftime("%d/%m/%Y")
        hora_f = log.timestamp.strftime("%H:%M")
        lbl_time = QLabel(f"⏰ {data_f} às {hora_f}")
        lbl_time.setObjectName("LogTime")
        
        lbl_tag = QLabel(log.categoria)
        lbl_tag.setObjectName("TagBase")
        
        if log.categoria == "Troca de Turno":
            lbl_tag.setStyleSheet("background-color: rgba(255, 87, 34, 0.15); color: #FF5722;")
        elif log.categoria == "Incidente":
            lbl_tag.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #EF4444;")
        elif log.categoria == "Manutenção":
            lbl_tag.setStyleSheet("background-color: rgba(250, 204, 21, 0.15); color: #FACC15;")
        else:
            lbl_tag.setStyleSheet("background-color: rgba(56, 189, 248, 0.15); color: #38BDF8;")
        
        header.addWidget(lbl_user)
        header.addSpacing(10)
        header.addWidget(lbl_tag)
        header.addStretch()
        header.addWidget(lbl_time)
        
        if log.operador == self.current_user:
            header.addSpacing(10)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setObjectName("ActionBtn")
            btn_edit.setFixedSize(28, 28)
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, l=log: self._edit_log(l))
            
            btn_del = QPushButton("🗑️")
            btn_del.setObjectName("ActionBtn")
            btn_del.setFixedSize(28, 28)
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, l=log: self._delete_log(l))
            
            header.addWidget(btn_edit)
            header.addWidget(btn_del)
        
        msg = QLabel(log.mensagem)
        msg.setObjectName("LogText")
        msg.setWordWrap(True) 
        
        card_layout.addLayout(header)
        card_layout.addWidget(msg)
        self.log_list_layout.addWidget(card)
        card.show()