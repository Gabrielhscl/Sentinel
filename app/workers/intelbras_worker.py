import time
import requests
from datetime import datetime
from requests.auth import HTTPDigestAuth
from PyQt5.QtCore import QThread, pyqtSignal
from app.config.settings import Settings

class IntelbrasWorker(QThread):
    status_signal = pyqtSignal(int, object) # slot_id, is_open
    log_signal = pyqtSignal(dict)           # Dados brutos do evento

    def __init__(self, slot_id: int, ip: str, nome_portaria: str):
        super().__init__()
        self.slot_id = slot_id
        self.ip = ip
        self.nome_portaria = nome_portaria
        self._run_flag = True
        self.last_log_time = datetime.now() 

    def run(self):
        auth = HTTPDigestAuth(Settings.INTELBRAS_USER, Settings.INTELBRAS_PASS)
        status_url = f"http://{self.ip}/cgi-bin/accessControl.cgi?action=getDoorStatus&channel=1&door=1"
        log_url = f"http://{self.ip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCardRec&count=1"

        while self._run_flag:
            # 1. Checa Status da Porta
            try:
                resp = requests.get(status_url, auth=auth, timeout=2)
                if resp.status_code == 200:
                    text = resp.text.lower()
                    is_open = "status=1" in text or "status=open" in text or "state=1" in text
                    self.status_signal.emit(self.slot_id, is_open)
                else:
                    self.status_signal.emit(self.slot_id, None) 
            except Exception:
                self.status_signal.emit(self.slot_id, None)

            # 2. Checa Logs de Acesso (Tag/Biometria)
            try:
                resp_log = requests.get(log_url, auth=auth, timeout=2)
                if resp_log.status_code == 200:
                    self._parse_log(resp_log.text)
            except Exception:
                pass

            time.sleep(2.0) 
            
    def _parse_log(self, text: str):
        if "records[0].CreateTime" not in text:
            return
            
        linhas = text.split('\n')
        log_time_str = None
        user_id = "Desconhecido"
        method = "Tag/Biometria/App"
        
        for linha in linhas:
            if "CreateTime=" in linha:
                log_time_str = linha.split("=")[1].strip()
            elif "UserID=" in linha or "CardName=" in linha:
                user_id = linha.split("=")[1].strip()
            elif "Method=" in linha:
                val = linha.split("=")[1].strip()
                metodos = {"1": "Senha", "2": "Cartão/Tag", "3": "Biometria", "4": "Facial"}
                method = metodos.get(val, method)
        
        if log_time_str:
            try:
                log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S")
                if log_time > self.last_log_time:
                    self.last_log_time = log_time
                    evento = {
                        'date': log_time.strftime('%d/%m/%Y'),
                        'time': log_time.strftime('%H:%M:%S'),
                        'tag': 'EXTERNO', 'color': '#a855f7',
                        'msg': f'Entrada ({self.nome_portaria}): {user_id} via {method}',
                        'image': None
                    }
                    self.log_signal.emit(evento)
            except ValueError:
                pass

    def stop(self):
        self._run_flag = False