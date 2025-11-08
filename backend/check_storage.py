from agent_logic.tools import get_storage, STORAGE_FILE
import json
import os

print(f"Storage file location: {os.path.abspath(STORAGE_FILE)}")
print(f"Storage file exists: {os.path.exists(STORAGE_FILE)}")
print()

storage = get_storage()
print("Current storage:")
print(json.dumps(storage, indent=2))