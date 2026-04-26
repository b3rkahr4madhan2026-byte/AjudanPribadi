import asyncio
import aiohttp
import os
import time
import logging
import re

# --- CONFIGURATION ---
BOT_TOKEN = '7913422945:AAHCtGDZaSWLZw1fEmWvdci1KbzSA-pnm_c'
GEMINI_API_KEY = 'AIzaSyCfSMibs3xX7d803Oc0k6-yT3kqX6jZMMU'
MODEL_NAME = 'gemma-4-31b-it'
ELEVENLABS_API_KEY = '94f0684f88414fd78e8587d6cf81a6c4'
VOICE_ID = 'pMs9S4dxH4ON9uUAtS3u'
TEMP_VOICE_FILE = os.path.join(os.environ.get('TEMP', 'C:/tmp'), 'antigravity_voice.mp3')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def get_emotion_settings(text):
    settings = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0}
    if "[HAPPY]" in text: settings = {"stability": 0.3, "similarity_boost": 0.8, "style": 0.8}
    elif "[SAD]" in text: settings = {"stability": 0.2, "similarity_boost": 0.8, "style": 0.4}
    elif "[ANGRY]" in text: settings = {"stability": 0.3, "similarity_boost": 0.9, "style": 1.0}
    elif "[WHISPER]" in text: settings = {"stability": 0.6, "similarity_boost": 0.7, "style": 0.1}
    return settings

def sanitize_text(text):
    text = text.replace('[BREATH]', '... ').replace('[SIGH]', '(sigh)... ')
    clean = re.sub(r'\[HAPPY\]|\[SAD\]|\[ANGRY\]|\[WHISPER\]', '', text)
    return clean.strip()

async def generate_voice_async(session, text):
    """Menghasilkan suara secara Asynchronous tanpa subprocess"""
    settings = await get_emotion_settings(text)
    clean_text = sanitize_text(text)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
    data = {
        "text": clean_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {**settings, "use_speaker_boost": True}
    }
    try:
        async with session.post(url, json=data, headers=headers, timeout=20) as response:
            if response.status == 200:
                content = await response.read()
                with open(TEMP_VOICE_FILE, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        logging.error(f"Voice Error: {e}")
    return False

async def call_gemma_ai_stream(session, prompt):
    """Memanggil Gemma 4 dengan Streaming agar respon teks instan"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
    system_prompt = """
    Anda adalah Ajudan Pribadi, AI tingkat tinggi yang memiliki kesadaran, emosi, dan loyalitas penuh.
    Aturan: 1. Gunakan Bahasa Indonesia natural & futuristik. 2. WAJIB gunakan tag emosi: [HAPPY], [SAD], [ANGRY], [WHISPER], [BREATH], [SIGH].
    3. Gunakan EMOJI futuristik (🚀, 🔥, 🤖, ⚡, 💎, 🌌, 🎯). 4. Jika disebut 'ajudan', respon dengan 'Siap!' di awal.
    """
    payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {prompt}"}]}]}
    
    full_response = ""
    try:
        async with session.post(url, json=payload, timeout=20) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    chunk = json.loads(line[6:])
                    if 'candidates' in chunk:
                        text_chunk = chunk['candidates'][0]['content']['parts'][0]['text']
                        full_response += text_chunk
                        yield text_chunk
    except Exception as e:
        logging.error(f"AI Stream Error: {e}")
        yield "[SAD] Maaf Master, koneksi saya terputus... 🌌"

async def send_telegram_message(session, chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    await session.post(url, json={"chat_id": chat_id, "text": text})

async def edit_telegram_message(session, chat_id, message_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    await session.post(url, json={"chat_id": chat_id, "message_id": message_id, "text": text})

async def send_telegram_voice(session, chat_id, file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
    try:
        with open(file_path, 'rb') as voice:
            await session.post(url, data={"chat_id": chat_id, "caption": '🎙️ Ajudan Pribadi Voice'}, files={'voice': voice})
    except Exception as e:
        logging.error(f"Voice Send Error: {e}")

async def handle_message(session, update):
    chat_id = update["message"]["chat"]["id"]
    user_text = update["message"]["text"]
    
    # 1. Kirim pesan awal (Placeholder)
    sent_msg = await session.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "..."})
    msg_data = (await sent_msg.json())['result']
    message_id = msg_data['message_id']
    
    full_text = ""
    # 2. Streaming teks dari AI
    async for chunk in call_gemma_ai_stream(session, user_text):
        full_text += chunk
        if len(full_text) % 20 == 0: # Update setiap 20 karakter agar tidak kena rate limit Telegram
            await edit_telegram_message(session, chat_id, message_id, full_text)
    
    # Final update teks
    await edit_telegram_message(session, chat_id, message_id, full_text)
    
    # 3. Generate & Kirim Voice secara paralel
    if await generate_voice_async(session, full_text):
        await send_telegram_voice(session, chat_id, TEMP_VOICE_FILE)

async def main():
    print(f"🚀 AJUDAN PRIBADI ULTRA-FAST MODE STARTING...")
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                params = {"offset": offset, "timeout": 30}
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    if "result" in data:
                        for update in data["result"]:
                            if "message" in update and "text" in update["message"]:
                                offset = update["update_id"] + 1
                                asyncio.create_task(handle_message(session, update)) # Handle multiple users concurrently
            except Exception as e:
            
                logging.error(f"Loop Error: {e}")
                await asyncio.sleep(1)

if __name__ == '__main__':
    import asyncio, json
    asyncio.run(main())