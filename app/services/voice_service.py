import pyttsx3
import queue
from PyQt5.QtCore import QThread

class VoiceWorker(QThread):
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self.running = True

    def run(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 180) 
        while self.running:
            try:
                text = self.q.get(timeout=1)
                if text:
                    engine.say(text)
                    engine.runAndWait()
            except queue.Empty:
                pass
                
    def stop(self):
        self.running = False

class VoiceService:
    def __init__(self):
        self.worker = VoiceWorker()
        self.worker.start()

    def say(self, text: str):
        self.worker.q.put(text)
        
    def stop(self):
        self.worker.stop()