import sys
import os

def fast_read(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\n--- CONTENT OF {path} ---\n")
            print(content)
            print("\n--- END OF CONTENT ---\n")
        else:
            print(f"ERROR: File {path} not found.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fast_read(sys.argv[1])
    else:
        print("Usage: python fast_access.py <file_path>")
