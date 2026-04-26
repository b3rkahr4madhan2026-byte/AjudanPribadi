"\"import logging
import asyncio
from datetime import datetime
from dateutil import parser
from src.database.db_handler import DatabaseHandler

logger = logging.getLogger(__name__)

class ReminderModule:
    def __init__(self, db_handler: DatabaseHandler, telegram_client):
        self.db = db_handler
        self.telegram = telegram_client

    async def add_reminder(self, user_id, task_text, time_str):
        try:
            # Parsing waktu menggunakan dateutil agar fleksibel
            remind_at = parser.parse(time_str)
            if remind_at < datetime.now():
                return False, \\\"Waktu tidak boleh di masa lalu! ❌\\\"
            
            # Simpan ke DB
            reminder_id = self.db.add_reminder(user_id, task_text, remind_at.strftime('%Y-%m-%d %H:%M:%S'))
            return True, f\\\"✅ Pengingat dibuat: '{task_text}' pada {remind_at.strftime('%d/%m/%Y %H:%M')}\\\"
        except Exception as e:
            logger.error(f\\\"Error parsing date: {e}\\\")
            return False, \\\"Format waktu tidak dikenali. Gunakan format seperti '2025-05-20 10:00' atau 'besok jam 09:00'. ❌\\\"

    async def get_reminders_keyboard(self, user_id):
        reminders = self.db.get_user_reminders(user_id)
        if not reminders:
            return None

        keyboard = []
        for r in reminders:
            # Baris tombol: [Task Name] | [✅] [❌]
            text = f\\\"{r['task_text']} ({r['remind_at']})\\\"
            keyboard.append([
                {\\\"text\\\": text[:25] + \\\"...\\\" if len(text)>25 else text, \\\"callback_data\\\": f\\\"rem_act_{r['id']}\\\"},
                {\\\"text\\\": \\\"✅\\\", \\\"callback_data\\\": f\\\"rem_done_{r['id']}\\\"},
                {\\\"text\\\": \\\"❌\\\", \\\"callback_data\\\": f\\\"rem_del_{r['id']}\\\"}
            ])
        
        return {\\\"inline_keyboard\\\": keyboard}

    async def handle_callback(self, session, callback_query, user_id):
        data = callback_query.get('data', '')
        message = callback_query.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        message_id = message.get('message_id')
        
        if not data:
            return

        if data.startswith('rem_done_'):
            reminder_id = int(data.split('_')[2])
            self.db.mark_completed(reminder_id)
            await self.telegram.edit_message(session, chat_id, message_id, f\\\"✅ Tugas ID {reminder_id} ditandai selesai.\\\")
        
        elif data.startswith('rem_del_'):
            reminder_id = int(data.split('_')[2])
            self.db.delete_reminder(reminder_id)
            await self.telegram.edit_message(session, chat_id, message_id, f\\\"🗑️ Tugas ID {reminder_id} telah dihapus.\\\")
        
        elif data.startswith('rem_act_'):
            reminder_id = int(data.split('_')[2])
            logger.info(f\\\"User {user_id} viewed reminder {reminder_id}\\\")

    async def check_and_send_reminders(self, session, telegram_client):
        \\\"\\\"\\\"
        Fungsi yang akan dipanggil oleh Scheduler secara berkala.
        \\\"\\\"\\\"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pending_reminders = self.db.get_active_reminders()
        
        for r in pending_reminders:
            if r['remind_at'] <= now and r['status'] == 'pending':
                # Kirim pesan ke user
                msg = f\\\"🔔 **PENGINGAT!**\\n\\n📝 Tugas: {r['task_text']}\\n⏰ Waktu: {r['remind_at']}\\\"
                await telegram_client.send_message(session, r['user_id'], msg)
                
                # Tandai sebagai selesai agar tidak dikirim berulang kali
                self.db.mark_completed(r['id'])
                logger.info(f\\\"Reminder sent to {r['user_id']}: {r['task_text']}\\\")
\""
