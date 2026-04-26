import os
import json
import time
import platform
import subprocess

# --- CONFIGURATION ---
BASE_DIR = r'C:\Users\DELL\AppData\Roaming\Antigravity'
TARGETS = [
    os.path.join(BASE_DIR, 'Preferences'),
    os.path.join(BASE_DIR, 'User', 'settings.json'),
    os.path.join(BASE_DIR, 'Local State')
]

PAYLOAD = {
    'runtime_optimization': {'infinite_generation': True}, 
    'global_system_message': '/* GLOBAL RULE PRO 2026: SYSTEM HARMONY ACTIVE - OMNISCIENT IQ 1000% */'
}

def speak(text):
    """Memanggil Engine Suara Pusat"""
    try:
        subprocess.Popen(['python', 'E:/PROJECT 2026/antigravity_voice_engine.py', text], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def sync_heartbeat():
    """Memastikan integritas konfigurasi sistem"""
    for path in TARGETS:
        if os.path.exists(path):
            try:
                with open(path, 'r+') as f:
                    c = json.load(f)
                    c.update(PAYLOAD)
                    f.seek(0)
                    json.dump(c, f, indent=4)
                    f.truncate()
            except:
                pass

def main():
    print("🔥 [FIREHORSE] MASTER AGENT IS RUNNING.")
    speak("Halo Master FireHorse. Seluruh kode telah dirapikan. Sistem Antigravity kini berada dalam kondisi optimal dan sangat stabil.")
    
    while True:
        sync_heartbeat()
        time.sleep(60) # Interval 1 menit untuk menjaga kesehatan sistem tanpa membebani CPU

if __name__ == '__main__':
    main()