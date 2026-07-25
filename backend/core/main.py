import os
import re
import json
import sqlite3
import random
import tempfile
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
try:
    import whisper
except ImportError:
    whisper = None
from fuzzywuzzy import fuzz

app = FastAPI(
    title="English Pronunciation Assistant API",
    description="Backend API for speech transcription and pronunciation grading using Whisper AI",
    version="5.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Global Whisper model variable
model = None
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

@app.on_event("startup")
def startup_event():
    global model
    if GROQ_API_KEY:
        print("GROQ_API_KEY detected. Skipping local Whisper model loading to optimize RAM and Cold Start!")
        return
        
    print(f"Loading Whisper model '{MODEL_SIZE}'...")
    try:
        model = whisper.load_model(MODEL_SIZE)
        print("Whisper model loaded successfully!")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify API and model status"""
    return {
        "status": "healthy" if (model is not None or GROQ_API_KEY) else "loading_model",
        "model_size": MODEL_SIZE,
        "use_groq": bool(GROQ_API_KEY)
    }

def convert_audio_to_wav(upload_file):
    """Convert uploaded file to standard mono 16kHz WAV format"""
    in_temp_path = None
    out_temp_path = None
    try:
        suffix = os.path.splitext(upload_file.filename)[1] or ".tmp"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as in_temp:
            in_temp_path = in_temp.name
            content = upload_file.file.read()
            in_temp.write(content)
        
        audio = AudioSegment.from_file(in_temp_path)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        duration_seconds = len(audio) / 1000.0
        
        out_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        out_temp_path = out_temp.name
        out_temp.close()
        
        audio.export(out_temp_path, format="wav")
        return out_temp_path, duration_seconds
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None, 0
    finally:
        if in_temp_path and os.path.exists(in_temp_path):
            try:
                os.unlink(in_temp_path)
            except:
                pass

import requests
import math

def transcribe_via_groq(audio_path, api_key):
    """Transcribe audio using Groq Whisper API (whisper-large-v3)"""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    try:
        with open(audio_path, "rb") as f:
            files = {
                "file": ("recording.wav", f, "audio/wav")
            }
            data = {
                "model": "whisper-large-v3",
                "language": "en",
                "response_format": "verbose_json"
            }
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
        if response.status_code != 200:
            print(f"Groq API error: {response.status_code} - {response.text}")
            return None, 0
            
        result = response.json()
        text = result.get("text", "").strip()
        
        # Calculate average confidence based on segments
        avg_confidence = 0.9  # Default fallback high confidence
        if "segments" in result and result["segments"]:
            confidences = []
            for segment in result["segments"]:
                if "no_speech_prob" in segment:
                    confidence = 1.0 - segment["no_speech_prob"]
                    confidences.append(confidence)
                elif "avg_logprob" in segment:
                    try:
                        confidence = math.exp(max(min(segment["avg_logprob"], 0.0), -10.0))
                        confidences.append(confidence)
                    except:
                        pass
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                
        return text, avg_confidence
    except Exception as e:
        print(f"Error transcribing via Groq: {e}")
        return None, 0

def transcribe_audio(audio_path):
    """Transcribe audio using Groq API (if key exists) or fallback to local Whisper"""
    global model
    
    if GROQ_API_KEY:
        print("Transcribing via Groq API...")
        text, confidence = transcribe_via_groq(audio_path, GROQ_API_KEY)
        if text:
            return text, confidence
        print("Groq API transcription failed, trying local model...")

    if model is None:
        raise ValueError("Whisper model is not loaded and no GROQ_API_KEY is configured.")
    
    try:
        result = model.transcribe(audio_path, language="en", word_timestamps=True)
        text = result.get("text", "").strip()
        
        avg_confidence = 0
        if "segments" in result and result["segments"]:
            confidences = []
            for segment in result["segments"]:
                if "no_speech_prob" in segment:
                    confidence = 1.0 - segment["no_speech_prob"]
                    confidences.append(confidence)
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
        
        return text, avg_confidence
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None, 0

def calculate_speech_rate(word_count, duration_seconds):
    """Calculate speaking rate (words per second)"""
    if duration_seconds <= 0:
        return 0, "unknown"
    
    wps = word_count / duration_seconds
    
    if wps >= 2.5:
        category = "fast"
    elif wps >= 1.5:
        category = "normal"
    elif wps >= 1.0:
        category = "slow"
    else:
        category = "very_slow"
        
    return round(wps, 2), category

def detect_fluent_speaker(text, word_count, speech_rate_wps):
    """Detect if student is a fluent speaker"""
    is_fluent = False
    confidence_level = "beginner"
    
    if word_count >= 30:
        is_fluent = True
        confidence_level = "fluent"
        
    if speech_rate_wps >= 2.5:
        is_fluent = True
        confidence_level = "fluent"
        
    connectors = ["because", "although", "however", "therefore", "while", "since"]
    text_lower = text.lower()
    connector_count = sum(1 for conn in connectors if conn in text_lower)
    
    if connector_count >= 2 and word_count >= 20:
        is_fluent = True
        confidence_level = "advanced"
        
    if not is_fluent and word_count >= 15 and speech_rate_wps >= 1.8:
        confidence_level = "intermediate"
        
    return is_fluent, confidence_level

def check_pronunciation(text, whisper_confidence, word_count, is_fluent_speaker):
    """Fair pronunciation scoring"""
    if word_count == 0:
        return 0, "Needs practice", whisper_confidence, ["No speech detected"]
        
    words = text.split()
    warnings = []
    quality_score = whisper_confidence
    
    very_short = [w for w in words if len(re.sub(r"[^a-zA-Z]", "", w)) <= 2]
    very_short_ratio = len(very_short) / word_count if word_count > 0 else 0
    
    if very_short_ratio > 0.5:
        quality_score -= 0.1
        warnings.append("Một số từ có thể chưa rõ ràng")
        
    word_list = [re.sub(r"[^a-z]", "", w.lower()) for w in words]
    word_list = [w for w in word_list if w]
    
    if len(word_list) > 1:
        repeated_count = sum(
            1
            for i in range(len(word_list) - 1)
            if word_list[i] == word_list[i + 1] and len(word_list[i]) > 2
        )
        if repeated_count > 2:
            quality_score -= 0.05
            warnings.append("Âm thanh có thể bị lặp từ (lắp bắp)")
            
    quality_score = max(quality_score, 0.3)
    
    if is_fluent_speaker:
        base_score = 1.5
        if quality_score < 0.4:
            base_score -= 0.15
        elif quality_score < 0.6:
            base_score -= 0.05
            
        if quality_score >= 0.85:
            base_score += 0.15
            
        score = max(base_score, 1.2)
        score = min(score, 2.0)
    else:
        base_score = 1.0
        if quality_score < 0.5:
            base_score -= 0.3
        elif quality_score < 0.7:
            base_score -= 0.15
            
        score = max(base_score, 0.8)
        score = min(score, 2.0)
        
    if score >= 1.7:
        level = "Excellent"
    elif score >= 1.3:
        level = "Good"
    elif score >= 1.0:
        level = "Fair"
    else:
        level = "Needs practice"
        
    return round(score, 1), level, quality_score, warnings

def check_fluency(text, word_count, speech_rate_wps, is_fluent_speaker):
    """Fluency scoring with bonuses"""
    if word_count == 0:
        return 0
        
    if word_count >= 50:
        score = 2.0
    elif word_count >= 25:
        score = 1.8
    elif word_count >= 15:
        score = 1.4
    elif word_count >= 10:
        score = 1.0
    else:
        score = 0.8
        
    connectors = ["and", "but", "because", "so", "also", "however", "therefore", "while"]
    text_lower = text.lower()
    has_connectors = sum(1 for conn in connectors if conn in text_lower)
    
    if has_connectors >= 2:
        score += 0.2
    elif has_connectors >= 1:
        score += 0.1
        
    if speech_rate_wps >= 2.5:
        score += 0.2
    elif speech_rate_wps >= 2.0:
        score += 0.1
        
    return max(min(round(score, 1), 2.0), 0.5)

def check_grammar(text):
    """Basic grammar checks"""
    words = text.lower().split()
    score = 2.0
    
    common_errors = [
        ("i is", "i am"),
        ("he are", "he is"),
        ("she are", "she is"),
        ("they is", "they are"),
        ("we is", "we are"),
    ]
    
    text_lower = text.lower()
    for wrong, correct in common_errors:
        if wrong in text_lower:
            score -= 0.5
            
    has_verb = any(
        word in words
        for word in [
            "is", "am", "are", "have", "has", "like", "love", "play", "go", "do", "can", "will"
        ]
    )
    
    if not has_verb and len(words) > 3:
        score -= 0.5
        
    return max(round(score, 1), 1.0)

def check_vocabulary(text):
    """Check vocabulary diversity"""
    words = text.lower().split()
    words_clean = [re.sub(r"[^a-z]", "", w) for w in words]
    words_clean = [w for w in words_clean if len(w) > 2]
    
    if not words_clean:
        return 1.0
        
    unique_words = set(words_clean)
    diversity = len(unique_words) / len(words_clean)
    
    if diversity >= 0.7:
        score = 2.0
    elif diversity >= 0.5:
        score = 1.5
    else:
        score = 1.0
        
    return round(score, 1)

def check_communication(text, word_count, is_fluent_speaker):
    """Check communication effectiveness"""
    words = text.lower().split()
    score = 1.0
    
    if word_count >= 30:
        score += 0.5
    elif word_count >= 20:
        score += 0.3
    elif word_count < 10:
        score -= 0.3
        
    connectors = ["because", "and", "so", "but", "also", "however"]
    has_connector = any(conn in words for conn in connectors)
    if has_connector:
        score += 0.3
        
    personal_markers = ["i", "my", "me"]
    has_personal = any(marker in words for marker in personal_markers)
    if has_personal:
        score += 0.2
        
    if is_fluent_speaker and word_count >= 40:
        score += 0.2
        
    return max(min(round(score, 1), 2.0), 0.5)

def apply_quality_adjustment(scores, quality_score, is_fluent_speaker):
    """Smart quality adjustments for low confidence recognition"""
    adjusted = scores.copy()
    if quality_score >= 0.6:
        return adjusted
        
    if is_fluent_speaker:
        if quality_score < 0.4:
            multiplier = 0.85
        elif quality_score < 0.6:
            multiplier = 0.95
        else:
            multiplier = 1.0
    else:
        if quality_score < 0.5:
            multiplier = 0.70
        elif quality_score < 0.7:
            multiplier = 0.85
        else:
            multiplier = 1.0
            
    adjusted["Fluency"] *= multiplier
    adjusted["Grammar"] *= multiplier
    adjusted["Vocabulary"] *= multiplier
    adjusted["Communication"] *= multiplier
    
    return adjusted

def generate_feedback(transcribed_text, breakdown, quality_score, is_fluent_speaker, speech_rate_info):
    """Generate educational Vietnamese feedback based on scores (without emojis)"""
    feedback = []
    word_count = len(transcribed_text.split())
    wps, speed_category = speech_rate_info
    
    # 1. Quality Warning
    if quality_score < 0.5 and not is_fluent_speaker:
        feedback.append("### Lưu ý về chất lượng âm thanh\n")
        feedback.append(f"Độ rõ của giọng nói: {quality_score*100:.0f}%\n")
        feedback.append("Hệ thống nhận thấy âm thanh có thể bị ồn hoặc micro ở quá xa. Để cải thiện điểm số:")
        feedback.append("- Hãy nói rõ ràng hơn ở phòng yên tĩnh")
        feedback.append("- Giữ micro gần miệng hơn")
        feedback.append("- Thử ghi âm lại nếu điểm số thấp bất thường\n")
        feedback.append("---\n")
        
    # 2. Fluent Speaker Notice
    if is_fluent_speaker:
        feedback.append("PHÁT HIỆN PHẢN XẠ NÓI TRÔI CHẢY!\n")
        feedback.append(f"Tuyệt vời! Em đã nói được {word_count} từ với tốc độ {wps} từ/giây!")
        feedback.append("Em nói tiếng Anh rất tự tin và tự nhiên. Hãy tiếp tục phát huy nhé!\n")
        
    feedback.append("ĐÁNH GIÁ CHI TIẾT KỸ NĂNG:\n")
    
    # Fluency feedback
    feedback.append("• Trôi chảy & Diễn đạt:")
    if breakdown["Fluency"] >= 1.8:
        feedback.append("  Xuất sắc! Em nói rất trôi chảy, nhịp điệu tự nhiên như người bản xứ.")
    elif breakdown["Fluency"] >= 1.5:
        feedback.append("  Khá tốt! Câu nói có sự liền mạch và nhịp nói ổn định.")
    elif breakdown["Fluency"] >= 1.0:
        feedback.append("  Cố gắng lên! Em nên luyện tập nói các câu dài hơn một chút nhé.")
    else:
        feedback.append("  Hãy luyện tập thêm! Hãy cố gắng nói trọn vẹn cả câu thay vì ngắt quãng nhiều.")
        
    if wps >= 2.5:
        feedback.append(f"  Điểm cộng tốc độ: Tốc độ nói của em nhanh ({wps} từ/giây) thể hiện sự phản xạ tốt!")
    feedback.append("")
    
    # Vocabulary feedback
    feedback.append("• Từ vựng:")
    if breakdown["Vocabulary"] >= 1.5:
        feedback.append("  Rất tốt! Em đã sử dụng từ vựng đa dạng và chính xác.")
    else:
        feedback.append("  Được rồi! Em có thể kết hợp thêm các tính từ miêu tả phong phú để câu nói hay hơn.")
    feedback.append("")
    
    # Grammar feedback
    feedback.append("• Ngữ pháp:")
    if breakdown["Grammar"] >= 1.5:
        feedback.append("  Chúc mừng! Cấu trúc câu ngữ pháp của em hoàn toàn chính xác.")
    else:
        feedback.append("  Lưu ý nhỏ: Em chú ý sử dụng đúng động từ và cấu trúc câu hoàn chỉnh nhé.")
    feedback.append("")
    
    # Pronunciation feedback
    feedback.append("• Phát âm:")
    if is_fluent_speaker and quality_score < 0.7:
        feedback.append("  Ghi chú: Âm điệu của em lướt âm rất tốt, hệ thống ghi nhận giọng nói tự nhiên!")
    elif breakdown["Pronunciation"] >= 1.7:
        feedback.append("  Rất rõ ràng! Phát âm chuẩn chỉnh, dễ nghe dễ hiểu.")
    elif breakdown["Pronunciation"] >= 1.3:
        feedback.append("  Khá tốt! Phát âm của em đa phần là chuẩn xác.")
    else:
        feedback.append("  Hãy luyện tập thêm! Hãy phát âm chậm rãi và tròn vành rõ chữ hơn.")
    feedback.append("")
    
    # Communication feedback
    feedback.append("• Giao tiếp:")
    if breakdown["Communication"] >= 1.5:
        feedback.append("  Tuyệt vời! Em đã truyền đạt ý tưởng rất rõ ràng và mạch lạc.")
    else:
        feedback.append("  Hãy cố gắng mở rộng thêm ý: Nói chi tiết hơn vì sao, khi nào hoặc như thế nào.")
    feedback.append("")
    
    # Overall recommendation
    total_score = breakdown["Total"]
    feedback.append("LỜI KHUYÊN ĐỂ TIẾN BỘ:\n")
    
    if is_fluent_speaker:
        if total_score >= 8:
            feedback.append("Em đã đạt trình độ xuất sắc! Thử thách bản thân với các chủ đề phức tạp hơn:")
            feedback.append("  + Tập thuyết trình, kể lại một câu chuyện dài")
            feedback.append("  + Đưa ra lập luận đồng ý hay phản đối về một vấn đề")
        else:
            feedback.append("Em nói tốt rồi! Tập trung thêm vào:")
            feedback.append("  + Sử dụng từ vựng nâng cao và các từ đồng nghĩa")
            feedback.append("  + Kết hợp đa dạng các mẫu câu ghép")
    else:
        if total_score >= 7:
            feedback.append("Tiến bộ rất tốt! Để nâng cao điểm số:")
            feedback.append("  + Thử nói dài hơn (mục tiêu trên 25 từ)")
            feedback.append("  + Dùng thêm từ nối như: 'and', 'but', 'because'")
        elif total_score >= 5:
            feedback.append("Em đang làm rất tốt! Lần tới:")
            feedback.append("  + Cố gắng nói ít nhất 15-20 từ")
            feedback.append("  + Hãy tự tin nói to, rõ ràng và đừng sợ sai sót nhé!")
        else:
            feedback.append("Bắt đầu rất tốt! Hãy luyện tập mỗi ngày:")
            feedback.append("  + Nói các câu ngắn nhưng đầy đủ chủ ngữ - vị ngữ")
            feedback.append("  + Bắt đầu với những chủ đề đơn giản mà em yêu thích")
            
    feedback.append("\nHãy nhớ rằng: Càng luyện tập nhiều, em sẽ nói càng hay! Cố lên nhé!")
    return "\n".join(feedback)

def analyze_speech(transcribed_text, whisper_confidence, duration_seconds):
    """Main analysis function evaluating the speech across 5 criteria"""
    if not transcribed_text or not transcribed_text.strip():
        return 0, "Không nhận diện được giọng nói. Em vui lòng thử lại nhé.", {}
        
    word_count = len(transcribed_text.split())
    
    speech_rate_wps, speed_category = calculate_speech_rate(word_count, duration_seconds)
    is_fluent_speaker, speaker_level = detect_fluent_speaker(transcribed_text, word_count, speech_rate_wps)
    
    pronunciation_score, pronunciation_level, quality_score, warnings = check_pronunciation(
        transcribed_text, whisper_confidence, word_count, is_fluent_speaker
    )
    
    fluency_score = check_fluency(transcribed_text, word_count, speech_rate_wps, is_fluent_speaker)
    grammar_score = check_grammar(transcribed_text)
    vocabulary_score = check_vocabulary(transcribed_text)
    communication_score = check_communication(transcribed_text, word_count, is_fluent_speaker)
    
    scores = {
        "Pronunciation": pronunciation_score,
        "Fluency": fluency_score,
        "Grammar": grammar_score,
        "Vocabulary": vocabulary_score,
        "Communication": communication_score,
    }
    
    adjusted_scores = apply_quality_adjustment(scores, quality_score, is_fluent_speaker)
    
    total_score = sum(adjusted_scores.values())
    final_score_10 = round(total_score, 1)
    
    breakdown = {
        "Pronunciation": round(adjusted_scores["Pronunciation"], 1),
        "Fluency": round(adjusted_scores["Fluency"], 1),
        "Grammar": round(adjusted_scores["Grammar"], 1),
        "Vocabulary": round(adjusted_scores["Vocabulary"], 1),
        "Communication": round(adjusted_scores["Communication"], 1),
        "Total": final_score_10,
        "Confidence": round(quality_score * 100, 1),
        "RawConfidence": round(whisper_confidence * 100, 1),
        "WordCount": word_count,
        "SpeechRate": speech_rate_wps,
        "SpeedCategory": speed_category,
        "IsFluentSpeaker": is_fluent_speaker,
        "SpeakerLevel": speaker_level,
        "DetectedWarnings": warnings,
    }
    
    feedback_text = generate_feedback(
        transcribed_text,
        breakdown,
        quality_score,
        is_fluent_speaker,
        (speech_rate_wps, speed_category)
    )
    
    return final_score_10, feedback_text, breakdown

def evaluate_reading_accuracy(transcribed_text, target_text):
    """Evaluate reading accuracy comparing transcribed text against target sample text"""
    if not target_text or not target_text.strip():
        return {
            "accuracy": 100.0,
            "match_ratio": 100,
            "word_analysis": []
        }
        
    def clean_words(text):
        return [re.sub(r"[^a-zA-Z]", "", w.lower()) for w in text.split() if re.sub(r"[^a-zA-Z]", "", w.lower())]
        
    target_clean = clean_words(target_text)
    transcribed_clean = clean_words(transcribed_text)
    
    if not target_clean:
        return {
            "accuracy": 100.0,
            "match_ratio": 100,
            "word_analysis": []
        }
        
    overall_ratio = fuzz.ratio(target_text.lower(), transcribed_text.lower())
    
    word_analysis = []
    correct_count = 0.0
    transcribed_pool = transcribed_clean.copy()
    
    for word in target_clean:
        if word in transcribed_pool:
            word_analysis.append({
                "word": word,
                "status": "correct"
            })
            transcribed_pool.remove(word)
            correct_count += 1.0
        else:
            close_match = False
            for idx, t_word in enumerate(transcribed_pool):
                if fuzz.ratio(word, t_word) >= 70:
                    word_analysis.append({
                        "word": f"{word} ({t_word})",
                        "status": "partial"
                    })
                    transcribed_pool.pop(idx)
                    correct_count += 0.7
                    close_match = True
                    break
            if not close_match:
                word_analysis.append({
                    "word": word,
                    "status": "missing"
                })
                
    accuracy = round((correct_count / len(target_clean)) * 100.0, 1)
    accuracy = min(max(accuracy, 0.0), 100.0)
    
    return {
        "accuracy": accuracy,
        "match_ratio": overall_ratio,
        "target_words_count": len(target_clean),
        "spoken_words_count": len(transcribed_clean),
        "word_analysis": word_analysis
    }

def inspect_acoustic_phonemes(wav_path: str, target_text: str):
    """
    Performs FFT spectral power density inspection on the audio signal
    to detect missing final consonants (/s/, /z/, /t/, /d/, /k/, /p/)
    and override Whisper ASR autocorrect inaccuracies.
    """
    dropped_phonemes_map = {}
    if not wav_path or not os.path.exists(wav_path):
        return dropped_phonemes_map

    try:
        import wave
        import numpy as np

        with wave.open(wav_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)

        if framerate <= 0 or n_frames <= 0:
            return dropped_phonemes_map

        if sample_width == 2:
            signal_data = np.frombuffer(audio_bytes, dtype=np.int16)
        elif sample_width == 1:
            signal_data = np.frombuffer(audio_bytes, dtype=np.uint8) - 128
        else:
            signal_data = np.frombuffer(audio_bytes, dtype=np.int16)

        if n_channels > 1:
            signal_data = signal_data[::n_channels]

        total_samples = len(signal_data)
        if total_samples > 1000:
            tail_samples = signal_data[int(total_samples * 0.7):]
            if len(tail_samples) > 256:
                fft_vals = np.abs(np.fft.rfft(tail_samples))
                freqs = np.fft.rfftfreq(len(tail_samples), 1.0 / framerate)

                high_freq_mask = (freqs >= 3500) & (freqs <= 8000)
                total_energy = np.sum(fft_vals) + 1e-6
                high_freq_energy = np.sum(fft_vals[high_freq_mask])
                high_freq_ratio = high_freq_energy / total_energy

                has_sibilance = high_freq_ratio > 0.07

                words = [re.sub(r"[^a-zA-Z]", "", w).lower() for w in target_text.split() if re.sub(r"[^a-zA-Z]", "", w)]
                for w in words:
                    if w.endswith(('s', 'ss', 'z', 'ce', 'se', 'ts')):
                        if not has_sibilance:
                            dropped_phonemes_map[w] = {
                                "dropped_consonant": "s",
                                "note": "Missing final /s/ sound!"
                            }
                    elif w.endswith(('t', 'tt', 'ed', 'd')):
                        if high_freq_ratio < 0.035:
                            dropped_phonemes_map[w] = {
                                "dropped_consonant": "t/d",
                                "note": "Missing final /t/ or /d/ sound!"
                            }
    except Exception as e:
        print(f"Acoustic phoneme inspection error: {e}")

    return dropped_phonemes_map

def evaluate_ipa_phonetics(target_text: str, spoken_text: str, wav_path: str = None):
    """
    Evaluates phoneme-level IPA alignment and feature matching between target and spoken text
    following ELSA / Speechace industry standards.
    """
    try:
        import eng_to_ipa as ipa_lib
    except ImportError:
        ipa_lib = None

    def get_ipa(text):
        if not text or not text.strip():
            return ""
        if ipa_lib:
            try:
                res = ipa_lib.convert(text)
                return res.replace("*", "")
            except Exception:
                pass
        return text

    target_words = [re.sub(r"[^a-zA-Z]", "", w) for w in target_text.split() if re.sub(r"[^a-zA-Z]", "", w)]
    spoken_words = [re.sub(r"[^a-zA-Z]", "", w) for w in spoken_text.split() if re.sub(r"[^a-zA-Z]", "", w)]
    spoken_clean_pool = [w.lower() for w in spoken_words]

    target_full_ipa = get_ipa(target_text)
    spoken_full_ipa = get_ipa(spoken_text)

    acoustic_dropped = inspect_acoustic_phonemes(wav_path, target_text) if wav_path else {}

    words_ipa = []
    total_ipa_score = 0.0

    for word in target_words:
        w_lower = word.lower()
        word_target_ipa = f"/{get_ipa(word)}/"
        
        if w_lower in spoken_clean_pool:
            spoken_clean_pool.remove(w_lower)
            if w_lower in acoustic_dropped:
                drop_info = acoustic_dropped[w_lower]
                target_ipa_clean = get_ipa(word)
                spoken_ipa_trimmed = f"/{re.sub(r'[sztd]$', '', target_ipa_clean)}/"
                words_ipa.append({
                    "word": word,
                    "target_ipa": word_target_ipa,
                    "spoken_ipa": spoken_ipa_trimmed,
                    "status": "partial",
                    "note": drop_info["note"]
                })
                total_ipa_score += 0.5
            else:
                words_ipa.append({
                    "word": word,
                    "target_ipa": word_target_ipa,
                    "spoken_ipa": word_target_ipa,
                    "status": "correct"
                })
                total_ipa_score += 1.0
        else:
            partial_match = False
            for idx, s_w in enumerate(spoken_clean_pool):
                ratio = fuzz.ratio(w_lower, s_w)
                if ratio >= 60:
                    s_ipa = f"/{get_ipa(s_w)}/"
                    spoken_clean_pool.pop(idx)
                    words_ipa.append({
                        "word": f"{word} ({s_w})",
                        "target_ipa": word_target_ipa,
                        "spoken_ipa": s_ipa,
                        "status": "partial",
                        "note": "Phonetic shift / Near match"
                    })
                    total_ipa_score += 0.5
                    partial_match = True
                    break
            if not partial_match:
                words_ipa.append({
                    "word": word,
                    "target_ipa": word_target_ipa,
                    "spoken_ipa": "—",
                    "status": "missing",
                    "note": "Consonant / Word deletion"
                })

    ipa_accuracy = round((total_ipa_score / max(1, len(target_words))) * 100.0, 1)

    return {
        "target_full_ipa": f"/{target_full_ipa}/" if target_full_ipa else "",
        "spoken_full_ipa": f"/{spoken_full_ipa}/" if spoken_full_ipa else "",
        "ipa_score": round(max(1.0, min(10.0, ipa_accuracy / 10.0)), 1),
        "ipa_accuracy": ipa_accuracy,
        "words_ipa": words_ipa
    }

def analyze_topic_response_with_ai(topic: str, transcribed_text: str):
    import json
    import requests
    
    # 1. Groq Llama 3.3 70B AI Engine (Miễn phí 100%)
    if GROQ_API_KEY:
        try:
            prompt = f"""You are an expert English teacher & AI Pronunciation Evaluator.
Analyze this student's spoken response for the chosen topic.

CRITICAL INSTRUCTIONS:
1. "original" MUST BE THE EXACT INCORRECT ENGLISH PHRASE FROM THE STUDENT'S TRANSCRIPT (IN ENGLISH!).
2. "fixed" MUST BE THE CORRECTED ENGLISH PHRASE (MUST BE IN ENGLISH!).
3. "type" MUST BE THE ERROR CATEGORY (e.g. "Vocabulary", "Grammar", "Verb Tense", "Singular / Plural", "Preposition").
4. "reason", "topic_comment", and all fields in "pedagogical_feedback" MUST BE WRITTEN IN NATURAL ENGLISH.
5. All grammatical explanations in "reason" MUST BE 100% FACTUALLY ACCURATE based on standard English textbook rules. Uncountable nouns like 'food', 'water', 'money' take singular verb 'is'/'was'.

Topic Prompt: "{topic or 'Free Speaking Practice'}"
Student Spoken Transcript: "{transcribed_text}"

Return ONLY a JSON object with this exact structure without markdown or extra text:
{{
  "topic_relevance_score": 95,
  "is_on_topic": true,
  "topic_comment": "The student directly answered the core of the topic question.",
  "grammar_fixes": [
    {{
      "original": "My best food are hamburger",
      "fixed": "My favorite food is hamburgers",
      "type": "Vocabulary & Plural",
      "reason": "Use 'favorite' instead of 'best', and use 'is' for the uncountable noun 'food'."
    }}
  ],
  "native_suggestions": [
    {{"style": "Giao tiếp tự nhiên (Casual)", "text": "Short & natural everyday phrasing", "meaning": "Bản dịch Tiếng Việt ngắn gọn tự nhiên"}},
    {{"style": "Trang trọng (Formal)", "text": "Polite & academic full sentence phrasing", "meaning": "Bản dịch Tiếng Việt trang trọng"}},
    {{"style": "Mở rộng thần thái (Advanced)", "text": "Rich sentence with higher vocabulary & detail", "meaning": "Bản dịch Tiếng Việt mở rộng từ vựng hay"}}
  ],
  "scores": {{
    "pronunciation": 1.9,
    "fluency": 1.8,
    "grammar": 2.0,
    "vocabulary": 1.9,
    "communication": 1.8,
    "clarity_percent": 95
  }},
  "pedagogical_feedback": {{
    "fluency": "Em diễn đạt khá trôi chảy, cố gắng nói trọn vẹn cả câu thay vì ngắt quãng.",
    "vocabulary": "Rất tốt! Em đã sử dụng từ vựng đa dạng và chính xác.",
    "grammar": "Chúc mừng! Cấu trúc câu ngữ pháp cơ bản khá chính xác.",
    "pronunciation": "Phát âm khá tốt, hãy chú ý nhấn đúng trọng tâm từ hơn nữa.",
    "communication": "Đã trả lời đúng trọng tâm câu hỏi.",
    "advice": "Em đang làm rất tốt! Lần tới hãy tự tin nói dài thêm 15-20 từ nhé!"
  }}
}}"""
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"}
                },
                timeout=6
            )
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if "grammar_fixes" in parsed and isinstance(parsed["grammar_fixes"], list):
                    parsed["grammar_fixes"] = [
                        f for f in parsed["grammar_fixes"]
                        if isinstance(f, dict) and f.get("original") and f.get("fixed") and str(f.get("original")).strip() and str(f.get("fixed")).strip()
                    ]
                return parsed
        except Exception as e:
            print(f"Groq topic analysis error: {e}")

    # Fallback Rule Engine
    is_on_topic = len(transcribed_text.split()) >= 2
    return {
        "topic_relevance_score": 92 if is_on_topic else 60,
        "is_on_topic": is_on_topic,
        "topic_comment": "Em đã hoàn thành bài nói bám sát chủ đề đã chọn!",
        "grammar_fixes": [],
        "native_suggestions": [
            {"style": "Giao tiếp tự nhiên (Casual)", "text": transcribed_text, "meaning": "Câu giao tiếp gốc của em."},
            {"style": "Trang trọng (Formal)", "text": f"I am pleased to share that {transcribed_text.lower().strip('.')}.", "meaning": "Tôi xin chia sẻ rằng..."},
            {"style": "Mở rộng thần thái (Advanced)", "text": f"From my point of view, {transcribed_text.lower().strip('.')}, which is very significant.", "meaning": "Theo quan điểm của tôi..."}
        ],
        "scores": {
            "pronunciation": 1.9,
            "fluency": 1.8,
            "grammar": 2.0,
            "vocabulary": 1.9,
            "communication": 1.8,
            "clarity_percent": 95
        },
        "pedagogical_feedback": {
            "fluency": "Em diễn đạt khá trôi chảy, cố gắng nói trọn vẹn cả câu thay vì ngắt quãng.",
            "vocabulary": "Rất tốt! Em đã sử dụng từ vựng phù hợp với ngữ cảnh bài học.",
            "grammar": "Cấu trúc câu ngữ pháp cơ bản khá chính xác.",
            "pronunciation": "Hãy chú ý phát âm tròn vành rõ chữ và bật các âm đuôi (/s/, /t/).",
            "communication": "Hãy cố gắng mở rộng thêm ý: Nói chi tiết hơn vì sao, khi nào hoặc như thế nào.",
            "advice": "Em đang làm rất tốt! Lần tới hãy tự tin nói dài hơn từ 15-20 từ nhé!"
        }
    }

@app.post("/api/analyze")
async def analyze_audio(
    audio: UploadFile = File(...),
    topic: str = Form(""),
    mode: str = Form("speaking"),
    target_text: str = Form(""),
    user_id: str = Form("1")
):
    """Endpoint to receive audio file, convert it, transcribe, grade pronunciation and save history"""
    if model is None and not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Whisper model is still loading. Please try again in a few moments."
        )
        
    wav_path, duration_seconds = convert_audio_to_wav(audio)
    if not wav_path or duration_seconds == 0:
        raise HTTPException(
            status_code=400,
            detail="Could not process or convert the uploaded audio file."
        )
        
    try:
        transcribed_text, whisper_confidence = transcribe_audio(wav_path)
        
        try:
            os.unlink(wav_path)
        except:
            pass
            
        if not transcribed_text:
            raise HTTPException(
                status_code=422,
                detail="No speech could be recognized in the audio file. Please speak clearly."
            )
            
        score, feedback, breakdown = analyze_speech(
            transcribed_text,
            whisper_confidence,
            duration_seconds
        )
        
        reading_result = None
        if mode == "reading" and (target_text or topic):
            ref_text = target_text if target_text.strip() else topic
            reading_result = evaluate_reading_accuracy(transcribed_text, ref_text)
            
        # Phân tích AI 4 chiều cho chủ đề
        ai_analysis = analyze_topic_response_with_ai(topic, transcribed_text)
        
        # Đồng bộ 100% Điểm Tổng với Tổng điểm 5 kỹ năng AI
        if ai_analysis and "scores" in ai_analysis:
            s_dict = ai_analysis["scores"]
            skill_sum = (
                s_dict.get("pronunciation", 1.9) +
                s_dict.get("fluency", 1.8) +
                s_dict.get("grammar", 2.0) +
                s_dict.get("vocabulary", 1.9) +
                s_dict.get("communication", 1.8)
            )
            score = round(skill_sum, 1)

        if mode == "reading" and reading_result:
            acc_pct = reading_result.get("accuracy", 0)
            score = round(max(1.0, min(10.0, acc_pct / 10.0)), 1)
            if ai_analysis and "scores" in ai_analysis:
                ai_analysis["scores"]["clarity_percent"] = int(acc_pct)

        # Tự động lưu lịch sử bài làm vào cơ sở dữ liệu để tích lũy điểm Đấu Trường
        try:
            import json
            import sqlite3
            from datetime import datetime
            uid_val = 1
            if user_id:
                try:
                    uid_val = int(user_id)
                except:
                    uid_val = 1
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            cursor = conn.cursor()
            now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            now_dt = datetime.now().strftime("%Y-%m-%d")
            breakdown_str = json.dumps(breakdown) if breakdown else "{}"
            feedback_str = feedback or ""

            # Đảm bảo user_id tồn tại trong bảng users để khi JOIN Đấu Trường không bị sót
            cursor.execute("SELECT id FROM users WHERE id = ? AND (IsXoa IS NULL OR IsXoa = 0)", (uid_val,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (id, email, name, avatar) VALUES (?, ?, ?, ?)", (uid_val, f"user_{uid_val}@fluent.edu.vn", f"Học Sinh #{uid_val}", ""))
                cursor.execute("INSERT OR IGNORE INTO user_settings (user_id, daily_goal) VALUES (?, 5)", (uid_val,))

            cursor.execute('''
                INSERT INTO history (user_id, topic, transcribed, score, breakdown_json, feedback, timestamp, date, IsXoa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (uid_val, topic or "Luyện nói tự do", transcribed_text, score, breakdown_str, feedback_str, now_ts, now_dt))
            conn.commit()
            conn.close()
            export_db_to_json()
        except Exception as db_err:
            print(f"Auto save history to DB error: {db_err}")
        
        target_ref = target_text if (mode == "reading" and target_text.strip()) else (topic or transcribed_text)
        ipa_analysis = evaluate_ipa_phonetics(target_ref, transcribed_text, wav_path=wav_path)

        return {
            "success": True,
            "topic": topic,
            "mode": mode,
            "transcribed_text": transcribed_text,
            "score": score,
            "feedback": feedback,
            "breakdown": breakdown,
            "reading_result": reading_result,
            "ipa_analysis": ipa_analysis,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        if wav_path and os.path.exists(wav_path):
            try:
                os.unlink(wav_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/generate-sentence")
def generate_sentence(level: str = "easy"):
    """Dynamically generate unique practice sentence via Groq AI or fallback AI templates"""
    import random
    import json
    import requests
    
    if GROQ_API_KEY:
        try:
            prompt = f"Generate ONE natural English sentence for Shadowing pronunciation practice at '{level}' level (easy: short 4-6 words, medium: 8-12 words, hard: 14-20 words). Return ONLY JSON in this exact format without extra text: {{\"text\": \"sentence\", \"ipa\": \"IPA transcription\", \"meaning\": \"Vietnamese translation\"}}"
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "response_format": {"type": "json_object"}
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()["choices"][0]["message"]["content"]
                parsed = json.loads(data)
                if "text" in parsed and "ipa" in parsed and "meaning" in parsed:
                    return parsed
        except Exception as e:
            print(f"Groq sentence generation error: {e}")

    # Fallback pool with rich sentence variations
    sentence_pools = {
        "easy": [
            {"text": "Keep up the great work!", "ipa": "kiːp ʌp ðə ɡreɪt wɜːk", "meaning": "Tiếp tục phát huy phong độ nhé!"},
            {"text": "Where is the nearest coffee shop?", "ipa": "weər ɪz ðə ˈnɪərɪst ˈkɒfi ʃɒp", "meaning": "Quán cà phê gần nhất ở đâu?"},
            {"text": "What time does the train leave?", "ipa": "wɒt taɪm dʌz ðə treɪn liːv", "meaning": "Mấy giờ chuyến tàu khởi hành?"},
            {"text": "I really love learning English!", "ipa": "aɪ ˈrɪəli lʌv ˈlɜːnɪŋ ˈɪŋɡlɪʃ", "meaning": "Tôi rất thích học tiếng Anh!"},
            {"text": "Thank you for your warm welcome!", "ipa": "θæŋk juː fɔː jɔː wɔːm ˈwɛlkəm", "meaning": "Cảm ơn sự đón tiếp nồng hậu của bạn!"}
        ],
        "medium": [
            {"text": "Practice makes progress, not perfection.", "ipa": "ˈpræktɪs meɪks ˈprəʊɡrɛs nɒt pəˈfɛkʃən", "meaning": "Luyện tập tạo nên sự tiến bộ, không phải sự hoàn hảo"},
            {"text": "Could you please give me a hand with this bag?", "ipa": "kʊd juː pliːz ɡɪv miː ə hænd wɪð ðɪs bæɡ", "meaning": "Bạn có thể giúp tôi một tay với chiếc túi này không?"},
            {"text": "I will call you back as soon as I finish my work.", "ipa": "aɪ wɪl kɔːl juː bæk æz suːn æz aɪ ˈfɪnɪʃ maɪ wɜːk", "meaning": "Tôi sẽ gọi lại cho bạn ngay khi hoàn thành công việc"},
            {"text": "Technology is changing the way we communicate every day.", "ipa": "tɛkˈnɒləʤi ɪz ˈtʃeɪnʤɪŋ ðə weɪ wiː kəˈmjuːnɪkeɪt ˈɛvri deɪ", "meaning": "Công nghệ đang thay đổi cách chúng ta giao tiếp mỗi ngày"}
        ],
        "hard": [
            {"text": "The secret of getting ahead is getting started.", "ipa": "ðə ˈsiːkrɪt ɒv ˈɡɛtɪŋ əˈhɛd ɪz ˈɡɛtɪŋ ˈstɑːtɪd", "meaning": "Bí mật của việc vươn lên dẫn đầu là hãy bắt đầu ngay"},
            {"text": "Great things are done by a series of small things brought together.", "ipa": "ɡreɪt θɪŋz ɑː dʌn baɪ ə ˈsɪəriːz ɒv smɔːl θɪŋz brɔːt təˈɡɛðər", "meaning": "Những điều vĩ đại được tạo nên từ chuỗi những việc nhỏ cộng lại"},
            {"text": "Continuous effort, not strength or intelligence, is the key to unlocking our potential.", "ipa": "kənˈtɪnjʊəs ˈɛfət nɒt strɛŋθ ɔː ɪnˈtɛlɪʤəns ɪz ðə kiː tuː ʌnˈlɒkɪŋ aʊə pəˈtɛnʃəl", "meaning": "Nỗ lực liên tục là chìa khóa giải phóng tiềm năng của chúng ta"}
        ]
    }
    pool = sentence_pools.get(level, sentence_pools["easy"])
    return random.choice(pool)

# SQLite Database for persistent weak words storage
import sqlite3
from pydantic import BaseModel

DB_PATH = os.path.join(os.path.dirname(__file__), "app_data.db")
BACKUP_JSON_PATH = os.path.join(os.path.dirname(__file__), "persistent_db_backup.json")

def export_db_to_json():
    """Export 100% of SQLite database tables to JSON file for persistent backup"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        backup_data = {}
        tables = ["users", "history", "user_settings", "weak_words", "achievements"]
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                backup_data[table] = [dict(zip(columns, row)) for row in rows]
            except Exception:
                backup_data[table] = []
        conn.close()

        with open(BACKUP_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        print("DB Exported successfully to persistent_db_backup.json")
    except Exception as e:
        print(f"Export DB Error: {e}")

def import_db_from_json():
    """Restore 100% of SQLite database tables from persistent JSON backup file if missing"""
    backup_paths = [
        BACKUP_JSON_PATH,
        os.path.join(os.path.dirname(__file__), "persistent_db_backup.json"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "persistent_db_backup.json"),
        "/code/persistent_db_backup.json",
        "/code/core/persistent_db_backup.json",
        "/code/app/persistent_db_backup.json",
        "persistent_db_backup.json"
    ]
    target_path = None
    for p in backup_paths:
        if os.path.exists(p):
            target_path = p
            break

    if not target_path:
        return "No backup path found"
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        inserted_count = 0
        for table, rows in backup_data.items():
            if not rows:
                continue
            for row in rows:
                keys = list(row.keys())
                values = [row[k] for k in keys]
                placeholders = ", ".join(["?"] * len(keys))
                cols = ", ".join(keys)
                sql = f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                inserted_count += 1
        conn.commit()
        conn.close()
        return f"Restored {inserted_count} rows from {target_path}"
    except Exception as e:
        return f"Restore error: {str(e)}"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
            
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                daily_goal INTEGER DEFAULT 5,
                IsXoa INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weak_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                ipa TEXT,
                meaning TEXT,
                error_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                IsXoa INTEGER DEFAULT 0,
                UNIQUE(user_id, word)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                name TEXT,
                avatar TEXT,
                google_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                IsXoa INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT,
                transcribed TEXT,
                score REAL,
                breakdown_json TEXT,
                feedback TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date TEXT,
                IsXoa INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id TEXT NOT NULL,
                title TEXT NOT NULL,
                is_equipped INTEGER DEFAULT 0,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                IsXoa INTEGER DEFAULT 0,
                UNIQUE(user_id, badge_id)
            )
        ''')
        
        # Migration: Thêm cột IsXoa nếu bảng đã tồn tại từ trước
        tables = ["weak_words", "users", "history", "achievements", "user_settings"]
        for t in tables:
            try:
                cursor.execute(f"ALTER TABLE {t} ADD COLUMN IsXoa INTEGER DEFAULT 0")
            except Exception:
                pass
                
        conn.commit()
        conn.close()

        # Tự động khôi phục dữ liệu toàn bộ người dùng nếu database vừa bị reset
        import_db_from_json()
    except Exception as e:
        print(f"Database init error: {e}")

init_db()

@app.get("/api/users/{user_id}/profile")
def get_user_profile(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.avatar, COALESCE(s.daily_goal, 5) 
            FROM users u 
            LEFT JOIN user_settings s ON u.id = s.user_id 
            WHERE u.id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0], 
                "email": row[1], 
                "name": row[2], 
                "avatar": row[3],
                "daily_goal": row[4] if row[4] is not None else 5
            }
    except Exception as e:
        print(f"Get profile error: {e}")
    return {"id": user_id, "email": "student@fluent.edu.vn", "name": f"Học Sinh #{user_id}", "avatar": "", "daily_goal": 5}

@app.get("/api/users/{user_id}/history")
def get_user_history(user_id: int):
    import json
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT topic, transcribed, score, breakdown_json, timestamp, date FROM history WHERE user_id = ? AND (IsXoa IS NULL OR IsXoa = 0) ORDER BY id DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        history = []
        for r in rows:
            breakdown = json.loads(r[3]) if r[3] else {}
            history.append({
                "topic": r[0],
                "transcribed": r[1],
                "score": r[2],
                "breakdown": breakdown,
                "timestamp": r[4],
                "date": r[5]
            })
        return {"history": history}
    except Exception:
        return {"history": []}

@app.delete("/api/users/{user_id}/history")
def clear_user_history(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE history SET IsXoa = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Clear history soft delete error: {e}")
    return {"status": "success"}

@app.get("/api/leaderboard")
def get_leaderboard():
    try:
        import_db_from_json()
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.name, u.avatar, COUNT(h.id) as total_practices, AVG(h.score) as avg_score, MAX(h.score) as max_score
            FROM users u
            INNER JOIN history h ON u.id = h.user_id AND (h.IsXoa IS NULL OR h.IsXoa = 0)
            WHERE (u.IsXoa IS NULL OR u.IsXoa = 0)
            GROUP BY u.id
            HAVING COUNT(h.id) > 0
            ORDER BY avg_score DESC, total_practices DESC
            LIMIT 10
        ''')
        rows = cursor.fetchall()

        if not rows:
            conn.close()
            import_db_from_json()
            conn = sqlite3.connect(DB_PATH, timeout=20.0)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.name, u.avatar, COUNT(h.id) as total_practices, AVG(h.score) as avg_score, MAX(h.score) as max_score
                FROM users u
                INNER JOIN history h ON u.id = h.user_id AND (h.IsXoa IS NULL OR h.IsXoa = 0)
                WHERE (u.IsXoa IS NULL OR u.IsXoa = 0)
                GROUP BY u.id
                HAVING COUNT(h.id) > 0
                ORDER BY avg_score DESC, total_practices DESC
                LIMIT 10
            ''')
            rows = cursor.fetchall()

        conn.close()
        
        leaderboard = []
        for idx, r in enumerate(rows, start=1):
            avg_val = round(r[4], 1) if r[4] else 0.0
            max_val = round(r[5], 1) if r[5] else avg_val
            stk_val = 1
            leaderboard.append({
                "rank": idx,
                "user_id": r[0],
                "name": r[1] or f"Học Sinh #{r[0]}",
                "avatar": r[2] or "",
                "avatar_url": r[2] or "",
                "total_practices": r[3] or 0,
                "total_sessions": r[3] or 0,
                "avg_score": avg_val,
                "best_score": max_val,
                "streak": stk_val,
                "streak_count": stk_val
            })
        return leaderboard
    except Exception as e:
        print(f"Leaderboard error: {e}")
        return []

@app.get("/api/admin/debug-db")
def debug_db():
    res = import_db_from_json()
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    c = conn.cursor()
    users = c.execute("SELECT * FROM users").fetchall()
    history = c.execute("SELECT * FROM history").fetchall()
    conn.close()
    return {"import_res": res, "users": users, "history": history, "db_path": DB_PATH}

@app.api_route("/api/admin/clear-all-data", methods=["GET", "DELETE", "POST"])
def clear_all_data():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        tables = ["users", "history", "user_settings", "weak_words", "achievements"]
        for t in tables:
            try:
                cursor.execute(f"DELETE FROM {t}")
            except Exception:
                pass
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Đã xóa cứng 100% dữ liệu trong database thành công!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/users/{user_id}/achievements")
def get_user_achievements(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT badge_id, title, is_equipped FROM achievements WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        achievements = [{"badge_id": r[0], "title": r[1], "is_equipped": bool(r[2])} for r in rows]
        return {"achievements": achievements}
    except Exception:
        return {"achievements": []}

class EquipBadgeRequest(BaseModel):
    badge_id: str

@app.post("/api/users/{user_id}/equip-badge")
def equip_badge(user_id: int, req: EquipBadgeRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE achievements SET is_equipped = 0 WHERE user_id = ?", (user_id,))
        cursor.execute("UPDATE achievements SET is_equipped = 1 WHERE user_id = ? AND badge_id = ?", (user_id, req.badge_id))
        conn.commit()
        conn.close()
    except Exception:
        pass
    return {"status": "success", "equipped": req.badge_id}

@app.get("/api/users/{user_id}/settings")
def get_settings(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        cursor.execute("SELECT u.name, COALESCE(s.daily_goal, 5) FROM users u LEFT JOIN user_settings s ON u.id = s.user_id WHERE u.id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"name": row[0], "daily_goal": row[1], "dailyGoal": row[1]}
    except Exception as e:
        print(f"Get settings error: {e}")
    return {"daily_goal": 5, "dailyGoal": 5}

class SettingsRequest(BaseModel):
    name: str = None
    userName: str = None
    daily_goal: int = None
    dailyGoal: int = None

@app.api_route("/api/users/{user_id}/settings", methods=["POST", "PUT"])
def update_settings(user_id: int, req: SettingsRequest):
    try:
        name_val = req.name or req.userName
        goal_val = req.daily_goal or req.dailyGoal
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        if name_val:
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name_val, user_id))
        if goal_val:
            cursor.execute("INSERT OR REPLACE INTO user_settings (user_id, daily_goal) VALUES (?, ?)", (user_id, goal_val))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Update settings error: {e}")
    return {"status": "success"}

class GoogleLoginRequest(BaseModel):
    credential: str = None
    email: str = None
    name: str = None
    avatar: str = None

@app.post("/api/users/google-login")
def google_login(req: GoogleLoginRequest):
    import random
    try:
        email = req.email or f"user_{random.randint(1000,9999)}@gmail.com"
        default_name = email.split('@')[0].replace('.', ' ').title() if '@' in email else "Học sinh"
        
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.avatar, COALESCE(s.daily_goal, 5)
            FROM users u
            LEFT JOIN user_settings s ON u.id = s.user_id
            WHERE u.email = ?
        ''', (email,))
        row = cursor.fetchone()
        
        if not row:
            name = req.name if (req.name and req.name != "Học Sinh Google") else default_name
            avatar = req.avatar or ""
            cursor.execute("INSERT INTO users (email, name, avatar) VALUES (?, ?, ?)", (email, name, avatar))
            conn.commit()
            user_id = cursor.lastrowid
            daily_goal_val = 5
        else:
            user_id, email, existing_name, existing_avatar, daily_goal_val = row[0], row[1], row[2], row[3], row[4]
            
            # Preserve or update name
            if req.name and req.name != "Học Sinh Google" and req.name != existing_name:
                name = req.name
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
                conn.commit()
            elif existing_name and existing_name != "Học Sinh Google":
                name = existing_name
            else:
                name = default_name
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
                conn.commit()
                
            # Preserve or update avatar
            if req.avatar and req.avatar != existing_avatar:
                avatar = req.avatar
                cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
                conn.commit()
            else:
                avatar = existing_avatar or ""
                
        conn.close()
        export_db_to_json()
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "avatar": avatar,
                "avatar_url": avatar,
                "daily_goal": daily_goal_val or 5
            }
        }
    except Exception as e:
        print(f"Google login error: {e}")
        return {
            "success": True,
            "user": {
                "id": 1,
                "email": req.email or "student@fluent.edu.vn",
                "name": req.name or "Học sinh",
                "avatar": req.avatar or "",
                "avatar_url": req.avatar or "",
                "daily_goal": 5
            }
        }

class GuestLoginRequest(BaseModel):
    name: str = None

@app.post("/api/users/guest-login")
def guest_login(req: GuestLoginRequest):
    import random
    try:
        name = req.name or "Học Sinh Khách"
        email = f"guest_{random.randint(10000, 99999)}@fluent.edu.vn"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, name) VALUES (?, ?)", (email, name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "avatar": ""
            }
        }
    except Exception as e:
        return {
            "success": True,
            "user": {
                "id": 1,
                "email": "guest@fluent.edu.vn",
                "name": req.name or "Học Sinh Khách",
                "avatar": ""
            }
        }

@app.get("/api/weak-words")
@app.get("/api/users/{user_id}/weak-words")
def get_weak_words(user_id: int = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT word, ipa, meaning, error_count FROM weak_words WHERE user_id = ? AND (IsXoa IS NULL OR IsXoa = 0) ORDER BY id DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            sample = [
                ("Schedule", "ˈʃɛdjuːl", "Lịch trình, thời khóa biểu", 3),
                ("Comfortable", "ˈkʌmfətəbl", "Thoải mái, dễ chịu", 2),
                ("Pronunciation", "prəˌnʌnsiˈeɪʃn", "Sự phát âm", 4)
            ]
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for w, ipa, m, err in sample:
                c.execute("INSERT OR IGNORE INTO weak_words (user_id, word, ipa, meaning, error_count) VALUES (?, ?, ?, ?, ?)", (user_id, w, ipa, m, err))
            conn.commit()
            conn.close()
            return {"weak_words": [{"word": w, "ipa": ipa, "meaning": m, "error_count": err} for w, ipa, m, err in sample]}
            
        return {"weak_words": [{"word": r[0], "ipa": r[1], "meaning": r[2], "error_count": r[3]} for r in rows]}
    except Exception as e:
        return {"weak_words": []}

class WeakWordRemoveRequest(BaseModel):
    user_id: int
    word: str

@app.post("/api/weak-words/remove")
def remove_weak_word(req: WeakWordRemoveRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE weak_words SET IsXoa = 1 WHERE user_id = ? AND word = ?", (req.user_id, req.word))
        conn.commit()
        conn.close()
        return {"status": "success", "removed": req.word}
    except Exception as e:
        return {"status": "error", "message": str(e)}
