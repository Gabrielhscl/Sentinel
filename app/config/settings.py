import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Licença
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    LICENSE_FILE = "licenca.key"

    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Intelbras Default
    INTELBRAS_USER = os.getenv("INTELBRAS_USER", "admin")
    INTELBRAS_PASS = os.getenv("INTELBRAS_PASS", "Admin#123")
    
    # Banco de Dados
    DB_PATH = "seguranca_historico.db"