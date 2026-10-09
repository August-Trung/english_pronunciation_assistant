"""
Backup live database from HuggingFace Space to persistent_db_backup.json
Ensures that all newly registered accounts and student practice history
are permanently preserved before any new code deployments.
"""
import requests
import json
import os
import shutil

LIVE_URL = "https://agrse-fluent-english-backend.hf.space/api/admin/debug-db"
BACKUP_PATH = "backend/app/persistent_db_backup.json"
HF_CLONE_BACKUP = "scratch/hf_space_clone/app/persistent_db_backup.json"

print(f"Connecting to live backend: {LIVE_URL} ...")
try:
    res = requests.get(LIVE_URL, timeout=15)
    if res.status_code != 200:
        print(f"Failed to fetch live DB. Status: {res.status_code}")
        exit(1)
        
    data = res.json()
    users_raw = data.get("users", [])
    history_raw = data.get("history", [])
    print(f"Found {len(users_raw)} users and {len(history_raw)} history sessions on cloud.")
    
    # Read existing backup to preserve schema/defaults
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        backup = json.load(f)
        
    # Map raw SQLite tuples to dicts
    # Users columns: [id, email, name, avatar, google_id, created_at, IsXoa, role, tenant_id, parent_code, password_hash]
    user_keys = ["id", "email", "name", "avatar", "google_id", "created_at", "IsXoa", "role", "tenant_id", "parent_code", "password_hash"]
    new_users = []
    for u in users_raw:
        if isinstance(u, list):
            new_users.append(dict(zip(user_keys, u)))
        elif isinstance(u, dict):
            new_users.append(u)
    
    # History columns: [id, user_id, topic, transcribed, score, breakdown_json, feedback, timestamp, date, IsXoa, audio_url]
    hist_keys = ["id", "user_id", "topic", "transcribed", "score", "breakdown_json", "feedback", "timestamp", "date", "IsXoa", "audio_url"]
    new_history = []
    for h in history_raw:
        if isinstance(h, list):
            # match length
            keys = hist_keys[:len(h)]
            new_history.append(dict(zip(keys, h)))
        elif isinstance(h, dict):
            new_history.append(h)
            
    if new_users:
        backup["users"] = new_users
    if new_history:
        backup["history"] = new_history
        
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    print(f"[OK] Successfully saved {len(new_users)} users & {len(new_history)} history to {BACKUP_PATH}")
    
    if os.path.exists(os.path.dirname(HF_CLONE_BACKUP)):
        shutil.copyfile(BACKUP_PATH, HF_CLONE_BACKUP)
        print(f"[OK] Synced to HuggingFace Git Clone: {HF_CLONE_BACKUP}")
        
    print("\nAll live student data is now safely locked in Git repository!")
except Exception as e:
    print(f"Error during backup: {e}")
