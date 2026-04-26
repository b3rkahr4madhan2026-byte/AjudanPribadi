"import logging
import aiohttp
import os
from src.config import Config

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.base_url = f\"https://api.telegram.org/bot{self.token}\"

    async def send_message(self, session: aiohttp.ClientSession, chat_id: int, text: str, parse_mode: str = None):
        url = f\"{self.base_url}/sendMessage\"
        payload = {\"chat_id\": chat_id, \"text\": text}
        if parse_mode:
            payload[\"parse_mode\"] = parse_mode
        try:
            async with session.post(url, json=payload, proxy=Config.PROXY_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f\"Telegram send_message Error ({response.status}): {error_text}\")
                    return {}
        except Exception as e:
            logger.error(f\"Telegram send_message Exception: {e}\")
            return {}

    async def edit_message(self, session: aiohttp.ClientSession, chat_id: int, message_id: int, text: str):
        url = f\"{self.base_url}/editMessageText\"
        payload = {\"chat_id\": chat_id, \"message_id\": message_id, \"text\": text}
        try:
            async with session.post(url, json=payload, proxy=Config.PROXY_URL) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f\"Telegram edit_message Error ({response.status}): {error_text}\")
        except Exception as e:
            logger.error(f\"Telegram edit_message Exception: {e}\")

    async def send_voice(self, session: aiohttp.ClientSession, chat_id: int, file_path: str, caption: str = None):
        url = f\"{self.base_url}/sendVoice\"
        try:
            data = {\"chat_id\": chat_id}
            if caption:
                data[\"caption\"] = caption
            
            with open(file_path, 'rb') as voice_file:
                files = {\"voice\": (os.path.basename(file_path), voice_file, 'audio/mpeg')}
                async with session.post(url, data=data, files=files, proxy=Config.PROXY_URL) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f\"Telegram send_voice Error ({response.status}): {error_text}\")
        except Exception as e:
            logger.error(f\"Telegram send_voice Exception: {e}\")

    async def send_chat_action(self, session: aiohttp.ClientSession, chat_id: int, action: str = \"typing\"):
        url = f\"{self.base_url}/sendChatAction\"
        payload = {\"chat_id\": chat_id, \"action\": action}
        try:
            await session.post(url, json=payload, proxy=Config.PROXY_URL)
        except Exception as e:
            logger.error(f\"Telegram send_chat_action Exception: {e}\")

    async def get_updates(self, session: aiohttp.ClientSession, offset: int, timeout: int = 30) -> dict:
        url = f\"{self.base_url}/getUpdates\"
        params = {\"offset\": offset, \"timeout\": timeout}
        try:
            async with session.get(url, params=params, proxy=Config.PROXY_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f\"Telegram get_updates Error ({response.status}): {error_text}\")
                    return {}
        except Exception as e:
            logger.error(f\"Telegram get_updates Exception: {e}\")
            return {}
"
