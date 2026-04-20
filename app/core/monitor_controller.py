from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from app.models.event_model import SecurityEvent
from app.services.database_service import DatabaseService
from app.services.door_service import DoorService
from app.services.telegram_service import TelegramService

class MonitorController(QObject):
    # Sinais que a UI vai escutar para se atualizar
    event_created_signal = pyqtSignal(SecurityEvent)
    door_status_changed_signal = pyqtSignal(int, bool) # slot_id, success
    blink_ui_signal = pyqtSignal(bool)

    def __init__(self, db_service: DatabaseService, door_service: DoorService, telegram_service: TelegramService):
        super().__init__()
        self.db_service = db_service
        self.door_service = door_service
        self.telegram_service = telegram_service
        
        # Estado interno
        self.door_states = {104: False, 109: False}

    # --- Regras de Negócio: Portões ---
    def request_door_open(self, slot_id: int, ip: str, name: str, color: str):
        success = self.door_service.open_door(ip)
        self.door_status_changed_signal.emit(slot_id, success)
        
        if success:
            event = SecurityEvent(
                tag='SISTEMA', color=color,
                msg=f'Botoeira Virtual: Portão de {name} Aberto',
                date=datetime.now().strftime('%d/%m/%Y'),
                time=datetime.now().strftime('%H:%M:%S')
            )
            self._process_new_event(event)
            self.telegram_service.send_alert(f"🚪 Portão de {name} Aberto", silent=True)

    # --- Regras de Negócio: Movimento ---
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

    # Função central para persistir e notificar UI
    def _process_new_event(self, event: SecurityEvent):
        saved_event = self.db_service.save_event(event)
        self.event_created_signal.emit(saved_event)