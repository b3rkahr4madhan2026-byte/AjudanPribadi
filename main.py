"import asyncio
import logging
import aiohttp
from src.config import Config
from src.bot.telegram_client import TelegramClient
from src.ai.gemini_client import GeminiClient
from src.ai.voice_client import VoiceClient
from src.bot.handlers import MessageHandler
from src.database.db_handler import DatabaseHandler
from src.modules.reminder import ReminderModule

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(\"AjudanPribadi\")

async def main():
    logger.info(\"🚀 MEMULAI SISTEM AJUDAN PRIBADI...\")

    # 1. Validasi Konfigurasi
    try:
        Config.validate()
    except ValueError as e:
        logger.error(e)
        return

    # 2. Inisialisasi Semua Komponen
    telegram_client = TelegramClient()
    gemini_client = GeminiClient()
    voice_client = VoiceClient()
    
    db_handler = DatabaseHandler()
    reminder_module = ReminderModule(db_handler, telegram_client)
    
    handler = MessageHandler(
        telegram_client=telegram_client,
        gemini_client=gemini_client,
        voice_client=voice_client,
        reminder_module=reminder_module,
        db_handler=db_handler
    )

    # 3. Jalankan Loop Utama
    logger.info(\"✅ SISTEM SIAP. Menunggu pesan...\")
    offset = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Ambil update dari Telegram
                updates_data = await telegram_client.get_updates(session, offset, timeout=30)
                
                if \"result\" in updates_data:
                    for update in updates_data[\"result\"]:
                        # Update offset agar tidak mengambil pesan yang sama
                        offset = update[\"update_id\"] + 1
                        
                        # Jalankan handler sebagai task di background agar tidak memblokir loop
                        asyncio.create_task(handler.handle_message(session, update))
                
                # Beri jeda sangat singkat untuk mencegah penggunaan CPU berlebih
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f\"Loop Error: {e}\")
                await asyncio.sleep(5) # Tunggu sebentar jika terjadi error jaringan

if __name__ == \"__main__\":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(\"🛑 Sistem dihentikan oleh pengguna.\")
    except Exception as e:
        logger.critical(f\"💥 Kegagalan Sistem Fatal: {e}\")"
