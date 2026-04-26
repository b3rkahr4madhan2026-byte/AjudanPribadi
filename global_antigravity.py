import paramiko
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GlobalAgent(FileSystemEventHandler):
    def __init__(self, target_server, user, key_path):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(target_server, username=user, key_filename=key_path)

    def on_modified(self, event):
        # Setiap file di perangkat DELL berubah, Agent akan otomatis sinkronisasi ke server
        if not event.is_directory:
            print(f"[GLOBAL_SYNC] Mengirim perubahan dari {event.src_path} ke Server...")
            self.ssh.exec_command(f"echo 'Updated file: {event.src_path}' >> /var/log/antigravity.log")

# Inisialisasi Agent
def start_global_grid(server_ip, user, pem_path):
    observer = Observer()
    handler = GlobalAgent(server_ip, user, pem_path)
    observer.schedule(handler, path=r"C:\Users\DELL\Proyek", recursive=True)
    observer.start()
    print("[!] ANTIGRAVITY GLOBAL ACTIVE: Menghubungkan seluruh server ke node lokal.")

if __name__ == "__main__":
    # Masukkan detail server target Anda
    start_global_grid("192.168.1.100", "root", "C:\\Users\\DELL\\.ssh\\id_rsa")