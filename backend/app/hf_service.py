import os
import io
import re
import json
import logging
import hashlib
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

def get_hf_client() -> Optional[Any]:
    """Returns an initialized Hugging Face InferenceClient if available."""
    if not InferenceClient:
        return None
    token = HF_TOKEN.strip() if HF_TOKEN else None
    try:
        return InferenceClient(token=token)
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
        # Look for cards/flashcards array inside object
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
    """Call LLM with Hugging Face primary, fallback to Groq."""
    hf = get_hf_client()
    if hf and HF_TOKEN:
        try:
            # Try HF Router / Serverless LLM
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
            logger.warning(f"HF Chat Completion failed: {e}, attempting fallback to Groq...")

    # Fallback to Groq API Pool
    groq_keys = list(DEFAULT_GROQ_KEYS)
    for env_name in ["GROQ_API_KEY", "GROQ_API_KEY_1", "GROQ_API_KEY_2"]:
        v = os.getenv(env_name, "").strip()
        if v and v not in groq_keys:
            groq_keys.insert(0, v)

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    for key in groq_keys:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
                timeout=15
            )
            if res.status_code == 200:
                result_json = res.json()
                return result_json["choices"][0]["message"]["content"]
        except Exception as err:
            logger.warning(f"Groq fallback error with key {key[:10]}...: {err}")
            continue

    return "[]"

def generate_deck_content(topic: str, level: str = "intermediate", count: int = 5) -> List[Dict[str, Any]]:
    """Generate high quality vocabulary flashcards with IPA and tips via LLM."""
    sys_prompt = (
        "You are an expert English tutor for Vietnamese learners. "
        "Create high-frequency vocabulary flashcards tailored to the given topic and level. "
        "For each word, provide: "
        "1. word: The target English word. "
        "2. ipa: Accurate phonetic transcription in /IPA/. "
        "3. meaning: Concise and accurate Vietnamese translation. "
        "4. example: A natural, practical English example sentence highlighting the word. "
        "5. pronunciation_tip: Practical mouth shape, tongue placement, or stress guidance in Vietnamese. "
        "Return ONLY a valid JSON object with a 'cards' array."
    )
    user_prompt = f"Topic: '{topic}'. Proficiency Level: '{level}'. Number of flashcards: {count}. Return JSON format."

    content = call_llm([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ], json_mode=True)

    cards = parse_flashcards_json(content)
    if not cards:
        # Minimal fallback cards if LLM output fails
        cards = [
            {
                "word": topic.split()[0].capitalize() if topic else "Vocabulary",
                "ipa": "/vəˈkæb.jə.ler.i/",
                "meaning": "Từ vựng quan trọng theo chủ đề",
                "example": f"This word is key when discussing {topic}.",
                "pronunciation_tip": "Nhấn rõ trọng âm âm tiết chính.",
                "image_url": ""
            }
        ]
    return cards

def generate_vocabulary_image(word: str, context: str = "", output_dir: Optional[str] = None) -> Optional[str]:
    """Generate an educational illustration for a vocabulary word using Hugging Face FLUX.1-schnell."""
    target_dir = output_dir or FLASHCARD_IMAGES_DIR
    os.makedirs(target_dir, exist_ok=True)

    # Cache check by slug
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", word.lower().strip())
    filename = f"vocab_{slug}.jpg"
    file_path = os.path.join(target_dir, filename)
    relative_url = f"/uploads/flashcard_images/{filename}"

    if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
        return relative_url

    prompt = (
        f"A clear, colorful educational illustration representing the English concept '{word}'. "
        f"{context if context else 'Clear visual storytelling'}, "
        "minimalist, modern 3D cartoon style, soft lighting, vibrant colors, white clean background, high resolution, no text"
    )

    hf = get_hf_client()
    if hf:
        try:
            # FLUX.1-schnell or SDXL on Hugging Face Serverless
            img: Image.Image = hf.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )
            # Save compressed JPEG
            img.convert("RGB").save(file_path, "JPEG", quality=85)
            return relative_url
        except Exception as e:
            logger.warning(f"HF FLUX.1 image generation failed for '{word}': {e}")
            try:
                # Fallback to SDXL-Lightning
                img = hf.text_to_image(
                    prompt=prompt,
                    model="ByteDance/SDXL-Lightning"
                )
                img.convert("RGB").save(file_path, "JPEG", quality=85)
                return relative_url
            except Exception as e2:
                logger.warning(f"HF SDXL fallback failed: {e2}")

    # Fallback to generating a clean educational SVG placeholder image
    try:
        from PIL import ImageDraw, ImageFont
        img = Image.new("RGB", (640, 480), color=(240, 244, 255))
        draw = ImageDraw.Draw(img)
        # Draw background card
        draw.rectangle([20, 20, 620, 460], fill=(255, 255, 255), outline=(200, 215, 240), width=4)
        # Draw header text
        text = f"{word.upper()}"
        draw.text((320, 220), text, fill=(40, 60, 120), anchor="mm")
        subtext = "AI Visual Illustration"
        draw.text((320, 270), subtext, fill=(120, 140, 170), anchor="mm")
        img.save(file_path, "JPEG", quality=80)
        return relative_url
    except Exception as e_canvas:
        logger.error(f"Canvas fallback failed: {e_canvas}")
        return None

def generate_picture_scenario(topic: str = "Daily Life", level: str = "intermediate") -> Dict[str, Any]:
    """Generate a multimodal Describe the Picture challenge scenario."""
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
    image_prompt = str(data.get("image_prompt", f"A lively, detailed scenario depicting {topic}, cinematic daylight, photo style"))
    guiding_questions = data.get("guiding_questions", [
        "Where is this scene taking place?",
        "What are the main people or objects doing?",
        "What atmosphere or mood do you observe?"
    ])
    keywords = data.get("keywords", ["atmosphere", "activity", "surrounding", "foreground", "expression"])

    # Generate the scenario image
    hash_id = hashlib.md5(f"{title}_{topic}".encode("utf-8")).hexdigest()[:10]
    filename = f"scenario_{hash_id}.jpg"
    file_path = os.path.join(PICTURE_PRACTICE_DIR, filename)
    relative_url = f"/uploads/picture_practice/{filename}"

    if not os.path.exists(file_path):
        hf = get_hf_client()
        image_generated = False
        if hf:
            try:
                img = hf.text_to_image(prompt=image_prompt, model="black-forest-labs/FLUX.1-schnell")
                img.convert("RGB").save(file_path, "JPEG", quality=85)
                image_generated = True
            except Exception as e:
                logger.warning(f"HF scenario image failed: {e}")
        
        if not image_generated:
            # Fallback illustration
            try:
                img = Image.new("RGB", (768, 512), color=(235, 240, 248))
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.rectangle([20, 20, 748, 492], fill=(255, 255, 255), outline=(180, 200, 230), width=4)
                draw.text((384, 230), title[:40], fill=(30, 50, 100), anchor="mm")
                draw.text((384, 280), f"Topic: {topic}", fill=(100, 120, 150), anchor="mm")
                img.save(file_path, "JPEG", quality=80)
            except Exception:
                pass

    return {
        "title": title,
        "image_url": relative_url,
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

    # Match keywords (case-insensitive substring)
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
