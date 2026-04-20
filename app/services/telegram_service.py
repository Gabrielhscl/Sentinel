import threading
import requests
import time
import os
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from app.config.settings import Settings

class TelegramService:
    def __init__(self, chat_id: str = "5252363828"):
        self.token = Settings.TELEGRAM_TOKEN
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def set_chat_id(self, new_chat_id: str):
        self.chat_id = new_chat_id

    def send_alert(self, msg: str, image=None, silent: bool = False):
        threading.Thread(target=self._send_async, args=(msg, image, silent), daemon=True).start()

    def _send_async(self, msg: str, image, silent: bool):
        try:
            if image:
                ba = QByteArray()
                buff = QBuffer(ba)
                buff.open(QIODevice.WriteOnly)
                image.save(buff, "JPEG")
                img_bytes = ba.data()

                files = {'photo': ('alert.jpg', img_bytes, 'image/jpeg')}
                data = {
                    'chat_id': self.chat_id, 'caption': f"🚨 <b>ALERTA</b>\n{msg}", 
                    'parse_mode': 'HTML', 'disable_notification': silent
                }
                requests.post(self.base_url + "sendPhoto", data=data, files=files)
            else:
                data = {
                    'chat_id': self.chat_id, 'text': f"🚨 <b>ALERTA</b>\n{msg}", 
                    'parse_mode': 'HTML', 'disable_notification': silent
                }
                requests.post(self.base_url + "sendMessage", data=data)
        except Exception as e:
            print(f"[TelegramService] Erro ao enviar mensagem: {e}")