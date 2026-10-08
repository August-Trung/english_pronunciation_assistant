import os
import io
import re
import json
import logging
import hashlib
import random
import urllib.parse
from typing import List, Dict, Any, Optional
from PIL import Image

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

import requests

logger = logging.getLogger("hf_service")
logger.setLevel(logging.INFO)

# Config directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FLASHCARD_IMAGES_DIR = os.path.join(CURRENT_DIR, "uploads", "flashcard_images")
PICTURE_PRACTICE_DIR = os.path.join(CURRENT_DIR, "uploads", "picture_practice")
os.makedirs(FLASHCARD_IMAGES_DIR, exist_ok=True)
os.makedirs(PICTURE_PRACTICE_DIR, exist_ok=True)

# API Keys
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or ""
DEFAULT_GROQ_KEYS = [
    "REMOVED_GROQ_API_KEY_1",
    "REMOVED_GROQ_API_KEY_2",
    "REMOVED_GROQ_API_KEY_3",
    "REMOVED_GROQ_API_KEY_4",
]

GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

def get_hf_client() -> Optional[Any]:
    """Returns an initialized Hugging Face InferenceClient if available."""
    if not InferenceClient:
        return None
    token = HF_TOKEN.strip() if HF_TOKEN else None
    try:
        return InferenceClient(token=token, timeout=8.0)
    except Exception as e:
        logger.warning(f"Failed to initialize Hugging Face InferenceClient: {e}")
        return None

def parse_json_safely(raw_text: str) -> Any:
    """Extract and parse JSON from LLM markdown output safely."""
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    
    # Strip markdown codeblocks
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback regex search for JSON array or object
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None

def parse_flashcards_json(raw_text: str) -> List[Dict[str, Any]]:
    """Parse and normalize flashcard array output from LLM."""
    data = parse_json_safely(raw_text)
    if isinstance(data, dict):
        for key in ["cards", "flashcards", "data", "vocabulary"]:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        return []

    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue
        word = str(item.get("word", "")).strip()
        if not word:
            continue
        normalized.append({
            "word": word,
            "ipa": str(item.get("ipa", "")).strip(),
            "meaning": str(item.get("meaning", "")).strip(),
            "example": str(item.get("example", "") or item.get("example_sentence", "")).strip(),
            "pronunciation_tip": str(item.get("pronunciation_tip", "") or item.get("tip", "")).strip(),
            "image_url": str(item.get("image_url", "")).strip()
        })
    return normalized

def call_llm(messages: List[Dict[str, str]], json_mode: bool = True) -> str:
    """Fast, reliable LLM invocation: Groq active models primary (0.8s latency), Hugging Face fallback."""
    # 1. Try Groq Pool (Ultra-fast 0.5s - 1s response)
    groq_keys = list(DEFAULT_GROQ_KEYS)
    for env_name in ["GROQ_API_KEY", "GROQ_API_KEY_1", "GROQ_API_KEY_2"]:
        v = os.getenv(env_name, "").strip()
        if v and v not in groq_keys:
            groq_keys.insert(0, v)

    for model_name in GROQ_MODELS:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        for key in groq_keys[:2]:  # Try primary keys
            try:
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=8
                )
                if res.status_code == 200:
                    result_json = res.json()
                    content = result_json["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 10:
                        return content
            except Exception as err:
                logger.warning(f"Groq {model_name} error: {err}")
                continue

    # 2. Fallback to Hugging Face Inference Router
    hf = get_hf_client()
    if hf and HF_TOKEN:
        try:
            resp = hf.chat_completion(
                messages=messages,
                model="Qwen/Qwen2.5-72B-Instruct",
                max_tokens=1500,
                temperature=0.7
            )
            content = resp.choices[0].message.content
            if content:
                return content
        except Exception as e:
            logger.warning(f"HF Chat Completion failed: {e}")

    return "[]"

def generate_deck_content(topic: str, level: str = "intermediate", count: int = 5) -> List[Dict[str, Any]]:
    """Generate high quality vocabulary flashcards with IPA, tips, and fast visual illustrations."""
    sys_prompt = (
        "You are an expert English teacher. "
        "Create vocabulary flashcards for the given topic. "
        "Return a JSON object with a 'cards' array. "
        "Each card must have: "
        "'word' (English word), "
        "'ipa' (phonetic notation, e.g. /ˌbaɪ.oʊ.daɪˈvɜːr.sə.ti/), "
        "'meaning' (clear Vietnamese meaning), "
        "'example' (natural English sentence using the word), "
        "'pronunciation_tip' (concise Vietnamese pronunciation guide)."
    )
    user_prompt = f"Topic: '{topic}'. Level: '{level}'. Count: {count}. Output JSON."

    content = call_llm([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ], json_mode=True)

    cards = parse_flashcards_json(content)
    if not cards:
        # Fallback card list if LLM unavailable
        cards = [
            {
                "word": "Communication",
                "ipa": "/kəˌmjuː.nəˈkeɪ.ʃən/",
                "meaning": "sự giao tiếp, truyền đạt",
                "example": f"Effective communication is essential when discussing {topic}.",
                "pronunciation_tip": "Nhấn trọng âm vào âm tiết /keɪ/.",
                "image_url": ""
            },
            {
                "word": "Collaboration",
                "ipa": "/kəˌlæb.əˈreɪ.ʃən/",
                "meaning": "sự cộng tác, hợp tác",
                "example": "Team collaboration brings the best project results.",
                "pronunciation_tip": "Nhấn mạnh vào âm /reɪ/.",
                "image_url": ""
            }
        ]

    # Attach fast visual illustrations to every card
    for c in cards:
        w = c.get("word", "")
        safe_prompt = urllib.parse.quote_plus(f"{w} {topic} clear 3D cartoon educational illustration")
        c["image_url"] = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=640&height=400&nologo=true"

    return cards

def generate_vocabulary_image(word: str, context: str = "", output_dir: Optional[str] = None) -> str:
    """Generate or retrieve instant visual illustration URL."""
    random_seed = random.randint(1, 999999)
    safe_prompt = urllib.parse.quote_plus(f"{word} {context} clear 3D colorful education illustration")
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?width=640&height=400&nologo=true&seed={random_seed}"

def generate_picture_scenario(topic: str = "Daily Life", level: str = "intermediate") -> Dict[str, Any]:
    """Generate a multimodal Describe the Picture challenge scenario with instant image URL."""
    sys_prompt = (
        "You are an IELTS & TOEIC Speaking Examiner. "
        "Create an engaging 'Describe the Picture' speaking task. "
        "Provide: "
        "1. title: An engaging title for the picture scene (e.g. 'A Lively Coffee Shop on a Rainy Afternoon'). "
        "2. image_prompt: A vivid prompt for image generation model showing people, activities, foreground, and background. "
        "3. guiding_questions: 3 questions helping the candidate structure their 60s response. "
        "4. keywords: 4-6 target vocabulary words or collocations candidates should use. "
        "Return ONLY a valid JSON object with fields 'title', 'image_prompt', 'guiding_questions', 'keywords'."
    )
    user_prompt = f"Topic: '{topic}'. Candidate level: '{level}'. Return JSON."

    content = call_llm([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ], json_mode=True)

    data = parse_json_safely(content) or {}
    title = str(data.get("title", f"Scene in {topic}"))
    image_prompt = str(data.get("image_prompt", f"A lively, detailed scene of {topic}, daylight, vibrant colors, cinematic"))
    guiding_questions = data.get("guiding_questions", [
        "Where is this scene taking place?",
        "What are the main people or objects doing?",
        "What atmosphere or mood do you observe?"
    ])
    keywords = data.get("keywords", ["atmosphere", "activity", "surrounding", "foreground", "expression"])

    # Instant high-quality scene image URL
    safe_img_prompt = urllib.parse.quote_plus(f"{image_prompt} detailed photo realistic scene 4k")
    random_seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{safe_img_prompt}?width=768&height=512&nologo=true&seed={random_seed}"

    return {
        "title": title,
        "image_url": image_url,
        "image_prompt": image_prompt,
        "guiding_questions": guiding_questions,
        "keywords": keywords,
        "suggested_time_seconds": 60
    }

def evaluate_picture_speaking(
    transcription: str,
    topic: str,
    keywords: List[str],
    guiding_questions: List[str]
) -> Dict[str, Any]:
    """Evaluate candidate speech transcription against the picture scenario using LLM."""
    if not transcription.strip():
        return {
            "score": 0,
            "fluency_score": 0,
            "vocabulary_score": 0,
            "grammar_score": 0,
            "matched_keywords": [],
            "feedback": "Không nhận diện được giọng nói. Vui lòng kiểm tra micro và thu âm lại rõ ràng hơn.",
            "sample_response": ""
        }

    lower_trans = transcription.lower()
    matched = [kw for kw in keywords if kw.lower() in lower_trans]

    sys_prompt = (
        "You are an IELTS Speaking Examiner evaluating a candidate describing a picture. "
        "Evaluate their transcription in terms of Fluency, Vocabulary Usage, and Grammar. "
        "Provide constructive and encouraging feedback in Vietnamese (chuẩn UTF-8 có dấu). "
        "Also provide an improved, natural native-like sample response (in English). "
        "Return ONLY a JSON object with: "
        "'fluency_score' (0-100), 'grammar_score' (0-100), 'vocabulary_score' (0-100), "
        "'overall_score' (0-100), 'feedback' (Vietnamese), 'sample_response' (English)."
    )

    user_prompt = (
        f"Topic: {topic}\n"
        f"Target Keywords: {', '.join(keywords)}\n"
        f"Guiding Questions: {'; '.join(guiding_questions)}\n"
        f"Candidate Transcription: \"{transcription}\"\n"
        "Evaluate candidate's response and output JSON."
    )

    content = call_llm([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ], json_mode=True)

    data = parse_json_safely(content) or {}
    overall = int(data.get("overall_score", 75))
    fluency = int(data.get("fluency_score", 70))
    vocab = int(data.get("vocabulary_score", 75))
    grammar = int(data.get("grammar_score", 70))
    feedback = str(data.get("feedback", "Bạn đã miêu tả được các chi tiết chính của bức tranh. Hãy chú ý sử dụng thêm từ nối để bài nói trôi chảy hơn."))
    sample_response = str(data.get("sample_response", "In this picture, I can clearly see people enjoying their time..."))

    return {
        "score": overall,
        "fluency_score": fluency,
        "vocabulary_score": vocab,
        "grammar_score": grammar,
        "matched_keywords": matched,
        "total_keywords": len(keywords),
        "feedback": feedback,
        "sample_response": sample_response
    }
