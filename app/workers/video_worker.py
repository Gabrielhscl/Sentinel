import cv2
import numpy as np
import time
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

# Tenta importar o YOLO de forma segura
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

class VideoWorker(QThread):
    change_pixmap_signal = pyqtSignal(QImage, int)
    status_signal = pyqtSignal(int, str)
    
    # O sinal agora exige 4 parâmetros (Status, Slot, Frame, Lista de Labels)
    presence_signal = pyqtSignal(bool, int, object, list) 

    def __init__(self, slot_id: int, url: str, target_fps: int = 15):
        super().__init__()
        self.slot_id = slot_id
        self.url = url
        self._run_flag = True
        self.last_status = ""
        
        self.target_fps = target_fps
        self.frame_time = 1.0 / self.target_fps if self.target_fps > 0 else 0
        
        self.polygon_pts = [] 
        self.background_model = None 
        self.last_poly_pts = [] 
        self.last_state = False
        self.actual_w = 0
        self.actual_h = 0
        self.sensitivity = 600
        
        # --- VARIÁVEIS DA IA (YOLO) ---
        self.yolo_enabled = False
        self.yolo_model = None
        self.last_yolo_time = 0
        self.yolo_boxes = [] 
        self.yolo_classes = [0, 2, 3, 5, 7] # 0=Pessoa, Resto=Veículos
        self.yolo_conf_threshold = 0.5 
        self.yolo_img_size = 320 

    def run(self):
        self.status_signal.emit(self.slot_id, "CONECTANDO...")
        
        if self.url == "celular":
            alvo = "http://192.168.1.12:8080/video" 
            if "OPENCV_FFMPEG_CAPTURE_OPTIONS" in os.environ:
                del os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]
        else:
            alvo = self.url
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

        cap = cv2.VideoCapture(alvo)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        last_process_time = 0 
        
        while self._run_flag:
            ret, frame = cap.read()
            current_time = time.time()
            
            if ret and frame is not None:
                if self.last_status != "ONLINE":
                    self.status_signal.emit(self.slot_id, "ONLINE")
                    self.last_status = "ONLINE"

                if current_time - last_process_time < self.frame_time:
                    continue
                last_process_time = current_time

                self.actual_h, self.actual_w = frame.shape[:2]
                current_pts = list(self.polygon_pts)
                
                has_polygon = len(current_pts) >= 3
                pixel_motion = False
                yolo_motion = False
                
                # CORREÇÃO: Inicializamos a lista vazia a cada frame
                labels_detectadas = [] 

                # Desenha os pontos do polígono (se existirem)
                if len(current_pts) > 0:
                    for p in current_pts:
                        cv2.circle(frame, tuple(p), 4, (0, 0, 255), -1)
                    if len(current_pts) >= 2:
                        pts = np.array(current_pts, np.int32).reshape((-1, 1, 2))
                        cv2.polylines(frame, [pts], True, (0, 255, 255), 2)

                # =======================================================
                # NÍVEL 1: PIXEL (Se YOLO ativo, ele não desenha caixas verdes)
                # =======================================================
                if has_polygon:
                    frame, pixel_motion = self.process_motion_tracking(frame, current_pts, draw_boxes=not self.yolo_enabled)
                else:
                    pixel_motion = True

                # =======================================================
                # NÍVEL 2: INTELIGÊNCIA ARTIFICIAL (YOLO)
                # =======================================================
                if self.yolo_enabled:
                    if not YOLO_AVAILABLE:
                        print("⚠️ Instale o ultralytics para usar a IA: pip install ultralytics")
                        self.yolo_enabled = False
                    else:
                        if self.yolo_model is None:
                            print(f"Slot {self.slot_id}: Carregando YOLO11n na CPU...")
                            self.yolo_model = YOLO("yolo11n.pt") 
                        
                        if current_time - self.last_yolo_time > 0.5:
                            if pixel_motion:
                                self.last_yolo_time = current_time
                                results = self.yolo_model.predict(
                                    frame, 
                                    imgsz=self.yolo_img_size, 
                                    conf=self.yolo_conf_threshold, 
                                    classes=self.yolo_classes, 
                                    verbose=False
                                )
                                self.yolo_boxes = results[0].boxes
                            elif has_polygon:
                                self.yolo_boxes = []

                    # Avalia as caixas da IA e preenche a lista de labels
                    if len(self.yolo_boxes) > 0:
                        yolo_motion = True
                        for box in self.yolo_boxes:
                            cls_id = int(box.cls[0])
                            label = "Pessoa" if cls_id == 0 else "Veículo"
                            
                            if label not in labels_detectadas:
                                labels_detectadas.append(label)
                            
                            # Desenha as caixas laranjas Sentinel
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (34, 87, 255), 2) 
                            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (34, 87, 255), 2)
                else:
                    self.yolo_boxes = []

                # =======================================================
                # O JUIZ FINAL (Controle do Sinal de Alarme)
                # =======================================================
                final_presence = yolo_motion if self.yolo_enabled else pixel_motion

                if final_presence != self.last_state:
                    if final_presence:
                        # CORREÇÃO: Emitindo os 4 argumentos perfeitamente (Status, Slot, Frame, Lista de Nomes)
                        self.presence_signal.emit(True, self.slot_id, frame.copy(), labels_detectadas)
                    
                    self.last_state = final_presence

                # Renderiza na Tela
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

    def process_motion_tracking(self, frame, current_pts, draw_boxes=True):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (25, 25), 0)
        mask = np.zeros(frame.shape[:2], dtype="uint8")
        
        cv2.fillPoly(mask, [np.array(current_pts, np.int32)], 255)
        gray_zone = cv2.bitwise_and(gray, gray, mask=mask)

        if self.background_model is None or self.background_model.shape != gray.shape or current_pts != self.last_poly_pts:
            self.background_model = gray_zone.copy()
            self.last_poly_pts = list(current_pts) 
            return frame, False

        diff = cv2.absdiff(self.background_model, gray_zone)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion = False
        for c in cnts:
            if cv2.contourArea(c) >= self.sensitivity:
                motion = True
                if draw_boxes:
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        return frame, motion

    def stop(self): 
        self._run_flag = False
        self.wait()