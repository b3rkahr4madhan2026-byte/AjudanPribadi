"import logging
import aiohttp
from src.config import Config
from src.utils.helpers import sanitize_text, get_emotion_settings, generate_unique_voice_path

logger = logging.getLogger(__name__)

class VoiceClient:
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.voice_id = Config.VOICE_ID
        self.url = f\"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream\"
        self.headers = {
            \"Accept\": \"audio/mpeg\",
            \"Content-Type\": \"application/json\",
            \"xi-api-key\": self.api_key
        }

    async def generate_voice_async(self, session: aiohttp.ClientSession, text: str) -> str:
        \"\"\"
        Menghasilkan suara dari teks menggunakan ElevenLabs.
        Mengembalikan path file audio jika berhasil, atau None jika gagal.
        \"\"\"
        settings = get_emotion_settings(text)
        clean_text = sanitize_text(text)
        file_path = generate_unique_voice_path()
        
        payload = {
            \"text\": clean_text,
            \"model_id\": \"eleven_multilingual_v2\",
            \"voice_settings\": {
                **settings,
                \"use_speaker_boost\": True
            }
        }

        try:
            async with session.post(self.url, json=payload, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f\"Voice generated successfully: {file_path}\")
                    return file_path
                else:
                    error_text = await response.text()
                    logger.error(f\"ElevenLabs API Error ({response.status}): {error_text}\")
                    return None
        except Exception as e:
            logger.error(f\"Voice Generation Error: {e}\")
            return None
"