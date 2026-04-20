from dataclasses import dataclass

@dataclass
class CameraConfig:
    slot_id: int
    sensibilidade: int = 600
    alerta_silencioso: bool = True
    horario_inicio: str = "00:00"
    horario_fim: str = "23:59"
    atraso_foto_ms: int = 1500
    atraso_video_ms: int = 0  
    modo_evidencia: int = 0  
    tempo_video_s: int = 5