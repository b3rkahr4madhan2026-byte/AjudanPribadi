"import logging
import aiohttp
from src.bot.telegram_client import TelegramClient
from src.ai.gemini_client import GeminiClient
from src.ai.voice_client import VoiceClient
from src.modules.reminder import ReminderModule
from src.database.db_handler import DatabaseHandler

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, telegram_client: TelegramClient, gemini_client: GeminiClient, 
                 voice_client: VoiceClient, reminder_module: ReminderModule, db_handler: DatabaseHandler):
        self.telegram = telegram_client
        self.gemini = gemini_client
        self.voice = voice_client
        self.reminder = reminder_module
        self.db = db_handler

    async def handle_message(self, session: aiohttp.ClientSession, update: dict):
        if \"callback_query\" in update:
            callback_query = update[\"callback_query\"]
            await self.reminder.handle_callback(session, callback_query, callback_query[\"from\"][\"id\"])
            return

        if \"message\" in update and \"text\" in update[\"message\"]:
            message = update[\"message\"]
            chat_id = message[\"chat\"][\"id\"]
            user_text = message[\"text\"]
            user_id = message[\"from\"][\"id\"]

            if user_text.startswith(\"/reminder\"):
                parts = user_text.split(maxsplit=2)
                if len(parts) < 3:
                    await self.telegram.send_message(session, chat_id, \"❌ Format salah!\nContoh: `/reminder Beli susu jam 14:00`\", parse_mode=\"Markdown\")
                else:
                    task_text = parts[1]
                    time_str = parts[2]
                    success, response_msg = await self.reminder.add_reminder(user_id, task_text, time_str)
                    await self.telegram.send_message(session, chat_id, response_msg)
                return

            if user_text == \"/reminders\":
                keyboard = await self.reminder.get_reminders_keyboard(user_id)
                if not keyboard:
                    await self.telegram.send_message(session, chat_id, \"📭 Anda tidak memiliki pengingat aktif.\")
                else:
                    await self.telegram.send_message(session, chat_id, \"📝 **Daftar Pengingat Anda:**\", parse_mode=\"Markdown\", reply_markup=keyboard)
                return

            await self.telegram.send_chat_action(session, chat_id, \"typing\")
            sent_msg = await self.telegram.send_message(session, chat_id, \"...\")
            if not sent_msg or \"result\" not in sent_msg:
                return
            message_id = sent_msg[\"result\"][\"message_id\"]
            
            full_text = \"\"
            async for chunk in self.gemini.stream_response(session, user_text):
                full_text += chunk
                if len(full_text) % 25 == 0:
                    await self.telegram.edit_message(session, chat_id, message_id, full_text)
            
            await self.telegram.edit_message(session, chat_id, message_id, full_text)
            
            voice_path = await self.voice.generate_voice_async(session, full_text)
            if voice_path:
                await self.telegram.send_voice(session, chat_id, voice_path)
"
