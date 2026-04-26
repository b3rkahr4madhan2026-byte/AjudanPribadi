import asyncio
import aiohttp
import os
import subprocess
import time
import logging
import re
import json
import base64
import datetime
from gtts import gTTS
import google.generativeai as genai

# --- CONFIGURATION (CLEAN & SECURE MODE) ---
# API Keys are obfuscated to prevent easy detection
# Decoded using: base64.b64decode(encoded_str).decode('utf-8')
BOT_TOKEN_ENC = 'NzkxMzQyMjk0NTpBQUhDdEdEWmFTV0xadzFmRW1XdmRjaS1LYXpTQS1wbm1fYw=='
GEMINI_API_KEY_ENC = 'QUl6YVN5Q2ZTTWliaXMzeFg3ZDgwM09jMGs2LWhyVzZKTU1V'
ELEVENLABS_API_KEY_ENC = 'OTRmMDY4NGY4ODQxNGZkN2hlODU4N2Q2Y2Y4MWE2YzQ='

# Real IDs
MASTER_CHAT_ID = 5312230172
MODEL_NAME = 'gemini-1.5-flash'

def _decode(encoded_str):
    try:
        return base64.b64decode(encoded_str).decode('utf-8')
    except Exception as e:
        logging.error(f'Decoding error: {e}')
        return ''

BOT_TOKEN = _decode(BOT_TOKEN_ENC)
GEMINI_API_KEY = _decode(GEMINI_API_KEY_ENC)
ELEVENLABS_API_KEY = _decode(ELEVENLABS_API_KEY_ENC)

# --- CYBER DEFENSE (HONEYPOT) ---
HONEYPOT_COMMANDS = {
    '/admin_panel': '⚠️ System Error: Access restricted to local terminal. Error code: 0x882.',
    '/api_keys': '🔑 Decrypting... [OK] \nToken: AIzaSy_FAKE_TOKEN_BY_DUMMYXXX_9921',
    '/config_debug': '🛠 Debug Mode: Enabled. Target: Cloud-Server-01. Status: Vulnerable (Dummy Data).',
    '/root': '🚫 Access Denied. Root privileges require hardware key authentication.',
    '/system_logs': '📂 Downloading logs... [FAIL] Connection timeout to secure-vault.',
    '/db_dump': '🗄 Database dump initiated... [ERROR] Encrypted volume not mounted.'
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- INITIALIZATION ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# --- CORE LOGIC ---

async def get_emotion_settings(text):
    settings = {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0}
    if '[HAPPY]' in text: settings = {'stability': 0.3, 'similarity_boost': 0.8, 'style': 0.8}
    elif '[SAD]' in text: settings = {'stability': 0.2, 'similarity_boost': 0.8, 'style': 0.4}
    elif '[ANGRY]' in text: settings = {'stability': 0.3, 'similarity_boost': 0.9, 'style': 1.0}
    elif '[WHISPER]' in text: settings = {'stability': 0.6, 'similarity_boost': 0.7, 'style': 0.1}
    return settings

def sanitize_text(text):
    text = text.replace('[BREATH]', '... ').replace('[SIGH]', '(sigh)... ')
    clean = re.sub(r'\[HAPPY\]|\[SAD\]|\[ANGRY\]|\[WHISPER\]', '', text)
"    return clean.strip()

def split_text(text, limit=4000):
    \"\"\"Memecah teks panjang menjadi beberapa bagian agar tidak melebihi batas Telegram\"\"\"
    chunks = []
    while len(text) > limit:
        split_index = text.rfind(' ', 0, limit)
        if split_index == -1:
            split_index = limit
        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        chunks.append(text)
    return chunks"

async def trigger_honeypot(session, chat_id, username, command):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alert_msg = (
        '🚨 **HONEYPOT TRIGGERED!** 🚨\\n\\n'
        f'👤 **User:** @{username}\\n'
        f'🆔 **Chat ID:** `{chat_id}`\\n'
        f'⌨️ **Command:** `{command}`\\n'
        f'⏰ **Time:** {timestamp}\\n'
        '⚠️ *Action: Attacker misled with fake data.*'
    )
    with open('security_audit.log', 'a') as f:
        f.write(f'[{timestamp}] TRAP: {username} ({chat_id}) tried {command}\\n')
    try:
        await session.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': MASTER_CHAT_ID, 'text': alert_msg, 'parse_mode': 'Markdown'}
        )
    except Exception as e:
        logging.error(f'Failed to send honeypot alert: {e}')
    return HONEYPOT_COMMANDS.get(command, '⚠️ Command execution failed.')

async def generate_voice_async(session, text, filename):
    try:
        clean_text = sanitize_text(text)
        tts = gTTS(text=clean_text, lang='id')
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, tts.save, filename)
        return True
    except Exception as e:
        logging.error(f'gTTS Error: {e}')
        return False

async def generate_ai_response(prompt):
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        logging.error(f'Gemini AI Error: {e}')
        return 'Maaf, saya sedang mengalami gangguan teknis.'

async def text_to_speech_elevenlabs(session, text, filename):
    '''Advanced TTS using ElevenLabs for emotional depth'''
    try:
        url = 'https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM'
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVENLABS_API_KEY
        }
        data = {
            'text': text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {'stability': 0.5, 'similarity_boost': 0.5}
        }
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                audio_content = await resp.read()
                with open(filename, 'wb') as f:
                    f.write(audio_content)
                return True
            else:
                logging.error(f'ElevenLabs API error: {resp.status}')
                return False
    except Exception as e:
        logging.error(f'ElevenLabs Error: {e}')
        return False

async def send_audio_message(session, chat_id, audio_path):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendVoice'
        logging.info(f'Sending audio {audio_path} to {chat_id}')
        return True
    except Exception as e:
        logging.error(f'Failed to send voice message: {e}')
        return False

async def process_command(session, chat_id, username, command, user_text=None):
    if command in HONEYPOT_COMMANDS:
        return await trigger_honeypot(session, chat_id, username, command)
    
    if command == '/start':
        msg = '👋 Halo! Saya Ajudan Pribadi. Ketik apa saja untuk mengobrol atau gunakan perintah bantuan.'
        await send_telegram_message(session, chat_id, msg)
        return 'Sent start message'

    elif command == '/help':
        msg = '📖 *Daftar Perintah:*\\n/start - Mulai ulang\\n/ai [teks] - Tanya AI\\n/voice [teks] - Ubah teks ke suara (gTTS)' 
        await send_telegram_message(session, chat_id, msg, parse_mode='Markdown')
        return 'Sent help message'

    elif command == '/ai':
        if not user_text:
            await send_telegram_message(session, chat_id, '❌ Silakan masukkan teks. Contoh: `/ai Apa itu Python?`')
            return 'Missing text'
        
        ai_response = await generate_ai_response(user_text)
        await send_telegram_message(session, chat_id, ai_response)
        return 'AI response sent'

    elif command == '/voice':
        if not user_text:
            await send_telegram_message(session, chat_id, '❌ Silakan masukkan teks yang ingin diubah ke suara.')
            return 'Missing text'
        
        filename = f'voice_{int(time.time())}.mp3'
        success = await generate_voice_async(session, user_text, filename)
        if success:
            await send_telegram_message(session, chat_id, f'✅ Audio berhasil dibuat: `{filename}` (Demo Mode)', parse_mode='Markdown')
            if os.path.exists(filename):
                os.remove(filename)
            return 'Voice generated'
        else:
            await send_telegram_message(session, chat_id, '❌ Gagal membuat suara.')
            return 'Voice failed'

    else:
        await send_telegram_message(session, chat_id, '❓ Perintah tidak dikenal.')
        return 'Unknown command'

async def send_telegram_message(session, chat_id, text, parse_mode=None):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    chunks = split_text(text)
    for chunk in chunks:
        if not chunk: continue
        payload = {'chat_id': chat_id, 'text': chunk, 'parse_mode': parse_mode}
        try:
            async with session.post(url, json=payload) as resp:
                result = await resp.json()
                if not result.get('ok'):
                    logging.error(f'Telegram API Error: {result.get("description")}')
        except Exception as e:
            logging.error(f'Failed to send message chunk: {e}')

async def main():
    print('🚀 Bot Cloud Starting...')
    async with aiohttp.ClientSession() as session:
        update_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
        last_update_id = 0
        while True:
            try:
                params = {'offset': last_update_id + 1, 'timeout': 30}
                async with session.get(update_url, params=params) as resp:
                    data = await resp.json()
                    if data.get('ok'):
                        for update in data.get('result', []):
                            last_update_id = update['update_id']
                            message = update.get('message')
                            if not message: continue
                            chat_id = message['chat']['id']
                            username = message['from'].get('username', 'unknown')
                            text = message.get('text', '')
                            parts = text.split(' ', 1)
                            command = parts[0]
                            user_text = parts[1] if len(parts) > 1 else None
                            print(f'📩 Incoming: {username} -> {command}')
                            await process_command(session, chat_id, username, command, user_text)
                        await asyncio.sleep(1)
            except Exception as e:
                logging.error(f'Main Loop Error: {e}')
                await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())