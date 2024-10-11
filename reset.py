import sys
from pathlib import Path

lock_file = Path("app.lock")

if lock_file.exists():
    print("Application already running.")
    lock_file.unlink()

print("exit")
lock_file.unlink()
sys.exit()