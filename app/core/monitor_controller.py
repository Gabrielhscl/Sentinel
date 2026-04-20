import time
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from app.models.event_model import SecurityEvent
from app.models.database_models import LogEntryDB
from app.services.database_service import DatabaseService
from app.services.door_service import DoorService
from app.services.telegram_service import TelegramService

class MonitorController(QObject):
    event_created_signal = pyqtSignal(SecurityEvent)
    blink_ui_signal = pyqtSignal(bool)
    
    # Sinal de Sucesso: Avisa que um novo log foi persistido no DB
    log_entry_added_signal = pyqtSignal(bool) 
    
    # ---------------------------------------------------------
    # NOVO SINAL: Controla o estado de desenho na interface
    # (is_drawing_mode: bool, camera_slot_id: int)
    # ---------------------------------------------------------
    drawing_mode_changed_signal = pyqtSignal(bool, int) 

    def __init__(self, db_service: DatabaseService, door_service: DoorService, telegram_service: TelegramService):
        super().__init__()
        self.db_service = db_service
        self.door_service = door_service
        self.telegram_service = telegram_service
        self.door_states = {104: False, 109: False}
        self.door_status_changed_signal = door_service.door_status_changed_signal
        self.last_alarm_time = {}
        
        # ---------------------------------------------------------
        # NOVO ESTADO: Rastreador do Modo de Desenho
        # ---------------------------------------------------------
        self.active_drawing_camera_id = None 

    # =========================================================
    # LÓGICA DE CONTROLO DE DESENHO
    # =========================================================
    def toggle_drawing_mode(self, camera_id: int):
        """Ativa ou desativa o modo de desenho para uma câmara específica."""
        if self.active_drawing_camera_id == camera_id:
            # Desliga se já estava ativa
            self.active_drawing_camera_id = None
            self.drawing_mode_changed_signal.emit(False, camera_id)
        else:
            # Desliga a anterior (se houver) e ativa a nova
            if self.active_drawing_camera_id is not None:
                self.drawing_mode_changed_signal.emit(False, self.active_drawing_camera_id)
            
            self.active_drawing_camera_id = camera_id
            self.drawing_mode_changed_signal.emit(True, camera_id)

    # =========================================================
    # LÓGICA DO DIÁRIO DE TURNO
    # =========================================================
    def salvar_log_do_turno(self, texto, categoria):
        log = self.db_service.salvar_nota_log(texto, categoria)
        if log:
            self.log_entry_added_signal.emit(True)
        return log
        
    def editar_log_do_turno(self, log_id: int, nova_mensagem: str, nova_categoria: str):
        if self.db_service.editar_nota_log(log_id, nova_mensagem, nova_categoria):
            self.log_entry_added_signal.emit(True)

    def apagar_log_do_turno(self, log_id: int):
        if self.db_service.apagar_nota_log(log_id):
            self.log_entry_added_signal.emit(True)

    # =========================================================
    # LÓGICA DE ALARMES E CÂMARAS
    # =========================================================
    def request_door_open(self, slot_id: int, ip: str, name: str, color: str):
        self.door_service.acionar_rele(slot_id, ip)
        event = SecurityEvent(
            tag='SISTEMA', color=color,
            msg=f'Botoeira Virtual: Portão de {name} Aberto',
            date=datetime.now().strftime('%d/%m/%Y'),
            time=datetime.now().strftime('%H:%M:%S')
        )
        self._process_new_event(event)
        self.telegram_service.send_alert(f"🚪 Portão de {name} Aberto", silent=True)

    def process_alarm(self, slot_id, frame, labels_detectadas):
        current_time = time.time()
        
        if slot_id in self.last_alarm_time:
            if current_time - self.last_alarm_time[slot_id] < 15:
                return 
                
        self.last_alarm_time[slot_id] = current_time
        
        if labels_detectadas:
            if len(labels_detectadas) > 1:
                alvo = "Múltiplos alvos detectados"
            else:
                alvo = f"{labels_detectadas[0]} detectada" if labels_detectadas[0] == "Pessoa" else f"{labels_detectadas[0]} detectado"
        else:
            alvo = "Movimento não identificado"

        evento = self.db_service.registrar_evento(slot_id, alvo, frame)
        
        if evento and evento.caminho_foto:
            chat_id = "SEU_CHAT_ID" 
            mensagem = (
                f"🛡️ *SENTINEL - AVISO REAL* 🛡️\n"
                f"📍 Local: Canal {slot_id}\n"
                f"🔍 Status: {alvo}\n"
                f"🕒 {evento.timestamp.strftime('%H:%M:%S')}"
            )
            
            threading.Thread(
                target=self.telegram_service.send_photo_sync,
                args=(chat_id, evento.caminho_foto, mensagem),
                daemon=True
            ).start()

    def handle_motion_detected(self, camera_name: str, img, is_silent: bool):
        event = SecurityEvent(
            tag='ALERTA', color='#ff4757',
            msg=f'Movimento detectado: {camera_name}',
            date=datetime.now().strftime('%d/%m/%Y'),
            time=datetime.now().strftime('%H:%M:%S'),
            image=img
        )
        self._process_new_event(event)
        self.telegram_service.send_alert(f"📸 Foto: {camera_name}", image=img, silent=is_silent)
        self.blink_ui_signal.emit(True)

    def _process_new_event(self, event: SecurityEvent):
        try:
            saved_event = self.db_service.save_event(event)
            self.event_created_signal.emit(saved_event)
        except AttributeError:
            pass