import cv2
import numpy as np
import time
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from datetime import datetime

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

class VideoWorker(QThread):
    change_pixmap_signal = pyqtSignal(QImage, int)
    status_signal = pyqtSignal(int, str)

    def __init__(self, slot_id: int, url: str):
        super().__init__()
        self.slot_id = slot_id
        self.url = url
        self._run_flag = True
        self.last_status = ""

    def run(self):
        self.status_signal.emit(self.slot_id, "CONECTANDO...")
        
        # --- MODO DE TESTE OU PRODUÇÃO ---
        if self.url == "celular":
            # ⚠️ ATENÇÃO: COLOQUE AQUI O IP DO SEU CELULAR NO APP IP WEBCAM
            alvo = "http://192.168.1.12:8080/video" 
        else:
            alvo = self.url

        cap = cv2.VideoCapture(alvo)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while self._run_flag:
            ret, frame = cap.read()
            if ret and frame is not None:
                if self.last_status != "ONLINE":
                    self.status_signal.emit(self.slot_id, "ONLINE")
                    self.last_status = "ONLINE"

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                qt_img = QImage(rgb_image.data.tobytes(), w, h, w * ch, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(qt_img.copy(), self.slot_id)
            else:
                self.status_signal.emit(self.slot_id, "SEM SINAL")
                self.last_status = "SEM SINAL"
                time.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(alvo)
        
        cap.release()

    def stop(self): 
        self._run_flag = False
        self.wait()