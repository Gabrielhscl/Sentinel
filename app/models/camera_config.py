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
    modo_evidencia: str = "Apenas Foto" # "Apenas Foto", "Apenas Vídeo", "Foto + Vídeo" 
    tempo_video_s: int = 5
    alerta_critico: bool = False # Se True, toca mesmo no silencioso do Telegram
    # --- NOVAS CONFIGURAÇÕES DO YOLO ---
    yolo_alvos: str = "Pessoas e Veículos" # Opções: "Apenas Pessoas", "Apenas Veículos", "Pessoas e Veículos"
    yolo_confianca: int = 50 # Porcentagem de certeza (0 a 100)
    yolo_modo: str = "Rápido (Baixo Consumo CPU)" # Opções: "Rápido", "Preciso"