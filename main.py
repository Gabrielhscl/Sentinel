import sys
from PyQt5.QtWidgets import QApplication
from app.services.database_service import DatabaseService
from app.services.door_service import DoorService
from app.services.telegram_service import TelegramService
from app.services.license_service import LicenseService
from app.core.monitor_controller import MonitorController
from app.ui.main_window import MainWindow

# Impede o PyQt de "engolir" erros e fechar o aplicativo silenciosamente
def custom_excepthook(type, value, traceback_info):
    import traceback
    traceback.print_exception(type, value, traceback_info)
    print("\n⚠️ O SISTEMA CAPTUROU UM ERRO, MAS IMPEDIU O FECHAMENTO FATAL ⚠️")

sys.excepthook = custom_excepthook

def main():
    app = QApplication(sys.argv)
    
    # 1. Inicia Serviços (Dependency Injection)
    db_service = DatabaseService()
    door_service = DoorService()
    telegram_service = TelegramService()
    
    # 2. Inicia Controller passando os serviços
    controller = MonitorController(db_service, door_service, telegram_service)
    
    # 3. Verificação de Licença
    license_service = LicenseService()
    if not license_service.validate_local_license():
        # Lógica de input de licença aqui...
        sys.exit()

    # 4. Inicia Interface
    window = MainWindow(controller)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()