"import os
from pathlib import Path
from dotenv import load_dotenv

# Menentukan root directory proyek
BASE_DIR = Path(__file__).resolve().parent.parent

# Mencoba memuat .env dari root directory
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    \"\"\"
    Class untuk mengelola semua konfigurasi aplikasi.
    Semua nilai diambil dari environment variables.
    \"\"\"
    
    # Telegram Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    PROXY_URL = os.getenv('PROXY_URL', 'http://proxy.server:3128')
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-2.5-flash')
    
    # Voice Configuration (ElevenLabs)
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    VOICE_ID = os.getenv('VOICE_ID')
    
    # Application Settings
    TEMP_DIR = os.getenv('TEMP_DIR', '/app/temp_ajudan')

    @classmethod
    def validate(cls):
        \"\"\"
        Memeriksa apakah semua kunci API yang wajib ada telah terisi.
        \"\"\"
        missing_keys = []
        required_keys = [
            'BOT_TOKEN', 
            'GEMINI_API_KEY', 
            'ELEVENLABS_API_KEY', 
            'VOICE_ID'
        ]
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(
                f\"❌ ERROR: Konfigurasi tidak lengkap! Missing keys: {', '.join(missing_keys)}. \"
                f\"Silakan buat file '.env' di root direktori dan isi kunci tersebut.\"
            )
        
        # Pastikan folder temp ada
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        print(\"✅ Configuration validated successfully.\")
"