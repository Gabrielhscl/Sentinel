import os
import requests
from datetime import datetime
from app.config.settings import Settings

class LicenseService:
    def validate_local_license(self) -> tuple[bool, str, str]:
        """Tenta ler a licença local e validar no Supabase"""
        if not os.path.exists(Settings.LICENSE_FILE):
            return False, "ARQUIVO_FALTANDO", "Nenhum arquivo de licença encontrado."
            
        with open(Settings.LICENSE_FILE, "r") as f:
            chave = f.read().strip()
            
        return self.check_license_online(chave)

    def check_license_online(self, chave: str) -> tuple[bool, str, str]:
        url_api = f"{Settings.SUPABASE_URL}/rest/v1/licencas?chave=eq.{chave}&select=*"
        headers = {
            "apikey": Settings.SUPABASE_KEY,
            "Authorization": f"Bearer {Settings.SUPABASE_KEY}",
            "Content-Profile": "public"
        }
        try:
            resposta = requests.get(url_api, headers=headers, timeout=5)
            dados = resposta.json()
            
            if not dados:
                return False, "INVALIDA", "Chave inválida ou não encontrada."
                
            licenca = dados[0]
            if not licenca.get("ativa"):
                return False, "DESATIVADA", "Licença desativada pelo administrador."
                
            data_exp = datetime.strptime(licenca.get("data_expiracao"), "%Y-%m-%d")
            if datetime.now() > data_exp:
                return False, "EXPIRADA", f"Licença expirou em {data_exp.strftime('%d/%m/%Y')}."
                
            return True, "OK", "Licença válida."
            
        except requests.exceptions.RequestException:
            print("[LicenseService] Offline - Permitindo acesso temporário.")
            return True, "OFFLINE", "Validação Offline"

    def save_license(self, chave: str):
        with open(Settings.LICENSE_FILE, "w") as f:
            f.write(chave.strip())