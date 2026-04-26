import subprocess
import sys

def execute_global_command(cmd_type):
    # Mapping perintah dari Continue ke Engine Global kita
    commands = {
        "audit": "python src/global_antigravity.py --action scan --deep",
        "sync": "python src/global_antigravity.py --action push --all",
        "patch": "python src/global_antigravity.py --action inject --security"
    }
    
    cmd = commands.get(cmd_type)
    if cmd:
        print(f"[ANTIGRAVITY_BRIDGE] Executing: {cmd}")
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "audit"
    execute_global_command(action)