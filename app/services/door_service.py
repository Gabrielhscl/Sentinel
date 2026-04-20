import requests
from requests.auth import HTTPDigestAuth
from app.config.settings import Settings

class DoorService:
    def __init__(self):
        self.auth = HTTPDigestAuth(Settings.INTELBRAS_USER, Settings.INTELBRAS_PASS)

    def open_door(self, ip: str) -> bool:
        url = f"http://{ip}/cgi-bin/accessControl.cgi?action=openDoor&channel=1&door=1"
        try:
            resp = requests.get(url, auth=self.auth, timeout=3)
            return resp.status_code == 200
        except Exception as e:
            print(f"[DoorService] Erro de conexão com portão {ip}: {e}")
            return False