import time
# import requests # Descomente quando for usar a placa real
from PyQt5.QtCore import QObject, pyqtSignal

class DoorService(QObject):
    # O "megafone" que a interface espera ouvir. 
    # Emite: (ID do portão, Status -> True: Aberto | False: Fechado | None: Offline)
    door_status_changed_signal = pyqtSignal(int, object)

    def __init__(self):
        # É obrigatório inicializar o QObject para o sinal funcionar
        super().__init__()

    def acionar_rele(self, slot_id: int, ip_address: str):
        """
        Função chamada pela Thread em segundo plano para abrir a catraca/portão.
        """
        try:
            # 1. Avisa a interface que o portão abriu (A UI vai ficar Vermelha/Laranja)
            self.door_status_changed_signal.emit(slot_id, True)
            print(f"🚪 Comando de abertura enviado para o IP {ip_address} (Portão {slot_id})")
            
            # Aqui entra o comando real para a placa da sua portaria
            # Exemplo: requests.get(f"http://{ip_address}/abrir", timeout=3)
            
            # 2. Simula o tempo que o portão físico demora para fechar sozinho
            time.sleep(4)
            
        except Exception as e:
            print(f"❌ Erro de conexão com a placa {ip_address}: {e}")
            # Avisa a interface que a placa está inoperante (A UI vai ficar Cinza)
            self.door_status_changed_signal.emit(slot_id, None)
            
        finally:
            # 3. Retorna o botão da interface para o estado Fechado (Verde)
            self.door_status_changed_signal.emit(slot_id, False)
            print(f"🟢 Portão {slot_id} fechado/trancado.")