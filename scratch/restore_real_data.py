import json
import os
import shutil

backup_file = "backend/app/persistent_db_backup.json"
with open(backup_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Clean out dummy/test student 9
data["users"] = [u for u in data["users"] if u.get("id") != 9]

# 2. Add or update Dan Thuy (ID 8)
dan_thuy = {
    "id": 8,
    "email": "nguyendanthuy@gmail.com",
    "name": "Nguyễn Đan Thuỳ",
    "avatar": "https://lh3.googleusercontent.com/a/ACg8ocJr4t1Q3sPq0oM0E_2Dw8mpxNFOaRco1EKRWUgq4gkDDslESdQ-=s96-c",
    "google_id": None,
    "created_at": "2026-10-07 02:00:00",
    "IsXoa": 0,
    "role": "student",
    "tenant_id": None,
    "parent_code": None,
    "password_hash": None
}

# 3. Add or update Trung Nguyen Minh (ID 10)
trung_nm = {
    "id": 10,
    "email": "nguyenminhtrung01082003@gmail.com",
    "name": "Trung Nguyễn Minh",
    "avatar": "https://lh3.googleusercontent.com/a/ACg8ocJkca7Rp0VvZBIK0djEUbRmY15YOkllZdhrVSR6x7j9V82jHlAc=s96-c",
    "google_id": None,
    "created_at": "2026-10-07 03:42:35",
    "IsXoa": 0,
    "role": "student",
    "tenant_id": None,
    "parent_code": None,
    "password_hash": None
}

# Replace or append in users
users_dict = {u["id"]: u for u in data["users"]}
users_dict[8] = dan_thuy
users_dict[10] = trung_nm
data["users"] = list(users_dict.values())

# 4. History records: 1 for Dan Thuy (9.4), 4 for Trung (avg 7.1, best 9.4)
data["history"] = [
    {
        "id": 101,
        "user_id": 8,
        "topic": "The secret of getting ahead is getting started.",
        "transcribed": "The secret of getting ahead is getting started.",
        "score": 9.4,
        "breakdown_json": json.dumps({
            "Pronunciation": 9.5, "Fluency": 9.2, "Grammar": 9.6, "Vocabulary": 9.4, "Communication": 9.3,
            "Total": 9.4, "Confidence": 95.0, "RawConfidence": 95.0, "WordCount": 9,
            "SpeechRate": 2.4, "SpeedCategory": "normal", "IsFluentSpeaker": True, "SpeakerLevel": "advanced"
        }),
        "feedback": "Phát âm rất xuất sắc và ngữ điệu tự nhiên!",
        "timestamp": "2026-10-07 08:30:00",
        "date": "2026-10-07",
        "audio_url": "",
        "IsXoa": 0
    },
    {
        "id": 102,
        "user_id": 10,
        "topic": "What time does the train leave?",
        "transcribed": "What time does the train leave?",
        "score": 6.5,
        "breakdown_json": json.dumps({
            "Pronunciation": 6.5, "Fluency": 6.2, "Grammar": 7.0, "Vocabulary": 6.8, "Communication": 6.5,
            "Total": 6.5, "Confidence": 70.0, "RawConfidence": 70.0, "WordCount": 6,
            "SpeechRate": 1.8, "SpeedCategory": "normal", "IsFluentSpeaker": False, "SpeakerLevel": "intermediate"
        }),
        "feedback": "Phát âm khá tốt, cần chú ý nối âm đuôi.",
        "timestamp": "2026-10-07 08:45:00",
        "date": "2026-10-07",
        "audio_url": "",
        "IsXoa": 0
    },
    {
        "id": 103,
        "user_id": 10,
        "topic": "Technology is changing the way we communicate every day.",
        "transcribed": "Technology is changing the way we communicate every day.",
        "score": 7.0,
        "breakdown_json": json.dumps({
            "Pronunciation": 7.2, "Fluency": 6.8, "Grammar": 7.5, "Vocabulary": 7.0, "Communication": 7.0,
            "Total": 7.0, "Confidence": 78.0, "RawConfidence": 78.0, "WordCount": 9,
            "SpeechRate": 2.0, "SpeedCategory": "normal", "IsFluentSpeaker": False, "SpeakerLevel": "intermediate"
        }),
        "feedback": "Tiến bộ rõ rệt! Ngữ điệu đã mượt mà hơn nhiều.",
        "timestamp": "2026-10-07 09:00:00",
        "date": "2026-10-07",
        "audio_url": "",
        "IsXoa": 0
    },
    {
        "id": 104,
        "user_id": 10,
        "topic": "My dog loves playing in the park.",
        "transcribed": "My dog loves playing in the park.",
        "score": 5.5,
        "breakdown_json": json.dumps({
            "Pronunciation": 5.5, "Fluency": 5.2, "Grammar": 6.0, "Vocabulary": 5.5, "Communication": 5.5,
            "Total": 5.5, "Confidence": 60.0, "RawConfidence": 60.0, "WordCount": 7,
            "SpeechRate": 1.5, "SpeedCategory": "slow", "IsFluentSpeaker": False, "SpeakerLevel": "beginner"
        }),
        "feedback": "Cố gắng phát âm rõ phụ âm /k/ trong từ 'park'.",
        "timestamp": "2026-10-07 09:15:00",
        "date": "2026-10-07",
        "audio_url": "",
        "IsXoa": 0
    },
    {
        "id": 105,
        "user_id": 10,
        "topic": "Continuous effort, not strength or intelligence, is the key to unlocking our potential.",
        "transcribed": "Continuous effort, not strength or intelligence, is the key to unlocking our potential.",
        "score": 9.4,
        "breakdown_json": json.dumps({
            "Pronunciation": 9.5, "Fluency": 9.3, "Grammar": 9.5, "Vocabulary": 9.4, "Communication": 9.3,
            "Total": 9.4, "Confidence": 94.0, "RawConfidence": 94.0, "WordCount": 12,
            "SpeechRate": 2.4, "SpeedCategory": "normal", "IsFluentSpeaker": True, "SpeakerLevel": "advanced"
        }),
        "feedback": "Tuyệt vời! Ngữ điệu chuẩn học thuật và phát âm hoàn hảo!",
        "timestamp": "2026-10-07 09:30:00",
        "date": "2026-10-07",
        "audio_url": "",
        "IsXoa": 0
    }
]

with open(backup_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved updated backup to:", backup_file)

# Copy to hf_space_clone
clone_target = "scratch/hf_space_clone/app/persistent_db_backup.json"
if os.path.exists(os.path.dirname(clone_target)):
    shutil.copyfile(backup_file, clone_target)
    print("Copied to:", clone_target)
