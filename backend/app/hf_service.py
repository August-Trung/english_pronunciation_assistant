import os
import io
import re
import json
import logging
import hashlib
import random
import base64
import html
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
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
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

def get_theme_palette(topic_str: str) -> Dict[str, str]:
    t = (topic_str or "").lower()
    if any(k in t for k in ["science", "lab", "tech", "computer", "research", "digital", "data"]):
        return {
            "c1": "#090D16", "c2": "#0F172A", "c3": "#0284C7",
            "accent": "#38BDF8", "pill_bg": "#0369A1",
            "icon": "flask"
        }
    if any(k in t for k in ["cafe", "coffee", "food", "market", "restaurant", "eat", "daily", "shop"]):
        return {
            "c1": "#1C1917", "c2": "#451A03", "c3": "#B45309",
            "accent": "#FBBF24", "pill_bg": "#78350F",
            "icon": "cafe"
        }
    if any(k in t for k in ["interview", "work", "job", "career", "office", "business", "meeting", "collaborat"]):
        return {
            "c1": "#0B0F19", "c2": "#1E1B4B", "c3": "#4338CA",
            "accent": "#A5B4FC", "pill_bg": "#312E81",
            "icon": "business"
        }
    if any(k in t for k in ["travel", "airport", "nature", "vacation", "trip", "park", "tour"]):
        return {
            "c1": "#042F2E", "c2": "#064E3B", "c3": "#059669",
            "accent": "#6EE7B7", "pill_bg": "#065F46",
            "icon": "travel"
        }
    return {
        "c1": "#0F172A", "c2": "#1E1B4B", "c3": "#2563EB",
        "accent": "#93C5FD", "pill_bg": "#1D4ED8",
        "icon": "book"
    }

def get_icon_svg(icon_type: str, color: str) -> str:
    if icon_type == "flask":
        return f'<path d="M19 3H5v2l5 6v7c0 1.1.9 2 2 2h4c1.1 0 2-.9 2-2v-7l5-6V3zm-3 13h-4v-5l-3-3.6V5h10v1.4L16 11v5z" fill="{color}"/>'
    elif icon_type == "cafe":
        return f'<path d="M4 19h16v2H4v-2zm16-9h-2V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v8c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4v-1h2c1.1 0 2-.9 2-2v-2c0-1.1-.9-2-2-2zm-4 3c0 1.1-.9 2-2 2H8c-1.1 0-2-.9-2-2V5h10v8zm2-3h-2V7h2v3z" fill="{color}"/>'
    elif icon_type == "business":
        return f'<path d="M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z" fill="{color}"/>'
    elif icon_type == "travel":
        return f'<path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" fill="{color}"/>'
    else:
        return f'<path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" fill="{color}"/>'

def generate_educational_svg(title: str, topic: str = "", subtitle: str = "", category: str = "general") -> str:
    """Generate instant, ultra-high reliability vector illustration card as base64 data URI."""
    palette = get_theme_palette(f"{topic} {title} {category}")
    esc_title = html.escape((title or "English Practice")[:45])
    esc_topic = html.escape((topic or "Visual Study")[:25].upper())
    esc_sub = html.escape(subtitle[:65] if subtitle else "Observe details, analyze vocabulary, and practice pronunciation")
    icon_svg = get_icon_svg(palette["icon"], palette["accent"])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{palette['c1']}"/>
      <stop offset="50%" stop-color="{palette['c2']}"/>
      <stop offset="100%" stop-color="{palette['c3']}"/>
    </linearGradient>
    <pattern id="dotGrid" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="#FFFFFF" fill-opacity="0.06"/>
    </pattern>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="35" result="blur"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="url(#bgGrad)"/>
  <rect width="100%" height="100%" fill="url(#dotGrid)"/>

  <circle cx="680" cy="90" r="140" fill="{palette['accent']}" opacity="0.18" filter="url(#softGlow)"/>
  <circle cx="120" cy="400" r="120" fill="{palette['c3']}" opacity="0.25" filter="url(#softGlow)"/>

  <rect x="36" y="36" width="728" height="408" rx="20" fill="#FFFFFF" fill-opacity="0.04" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="1.5"/>

  <g transform="translate(64, 60)">
    <rect width="180" height="30" rx="15" fill="{palette['pill_bg']}" fill-opacity="0.5" stroke="{palette['accent']}" stroke-opacity="0.5" stroke-width="1"/>
    <text x="90" y="20" fill="{palette['accent']}" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.2">{esc_topic}</text>
  </g>

  <g transform="translate(400, 180)">
    <circle cx="0" cy="0" r="48" fill="#FFFFFF" fill-opacity="0.08" stroke="{palette['accent']}" stroke-width="2"/>
    <circle cx="0" cy="0" r="40" fill="{palette['c1']}" fill-opacity="0.8"/>
    <g transform="translate(-16, -16) scale(1.35)">
      {icon_svg}
    </g>
  </g>

  <text x="400" y="280" fill="#FFFFFF" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="28" font-weight="800" text-anchor="middle">
    {esc_title}
  </text>
  <text x="400" y="318" fill="#CBD5E1" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="16" font-weight="500" text-anchor="middle">
    {esc_sub}
  </text>

  <g transform="translate(400, 390)">
    <rect x="-140" y="-14" width="280" height="28" rx="14" fill="#FFFFFF" fill-opacity="0.06" stroke="#FFFFFF" stroke-opacity="0.1" stroke-width="1"/>
    <text x="0" y="4" fill="#94A3B8" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="600" text-anchor="middle" letter-spacing="1">
      STUDY STUDIO &bull; DUAL-CODING VISUAL
    </text>
  </g>
</svg>"""

    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

PHOTO_CATALOG = {
    "science": [
        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&w=1000&q=80"
    ],
    "cafe": [
        "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1000&q=80"
    ],
    "airport": [
        "https://images.unsplash.com/photo-1530521954074-e64f6810b32d?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1520437358207-323b43b50729?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1517400508447-f8dd518b86db?auto=format&fit=crop&w=1000&q=80"
    ],
    "office": [
        "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1000&q=80"
    ],
    "interview": [
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1000&q=80"
    ],
    "market": [
        "https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=1000&q=80"
    ],
    "library": [
        "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=1000&q=80"
    ],
    "hospital": [
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1000&q=80"
    ],
    "city": [
        "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=1000&q=80"
    ],
    "park": [
        "https://images.unsplash.com/photo-1496347646636-ea47f7d6b37b?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1000&q=80"
    ],
    "classroom": [
        "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1000&q=80"
    ],
    "restaurant": [
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=1000&q=80"
    ],
    "hotel": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1000&q=80"
    ],
    "technology": [
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1000&q=80"
    ],
    "kitchen": [
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1507048331197-7d4ac70811cf?auto=format&fit=crop&w=1000&q=80"
    ],
    "nature": [
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"
    ],
    "fitness": [
        "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1000&q=80"
    ],
    "art": [
        "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=1000&q=80",
        "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80"
    ]
}

def resolve_scene_photo(topic: str = "", title: str = "", context: str = "") -> str:
    """Resolve an authentic, high-resolution photography scene for IELTS/TOEIC speaking tasks."""
    combined = f"{topic} {title} {context}".lower()

    if any(k in combined for k in ["science", "lab", "chemist", "biolog", "physics", "experiment", "research"]):
        pool = PHOTO_CATALOG["science"]
    elif any(k in combined for k in ["cafe", "coffee", "latte", "espresso", "barista"]):
        pool = PHOTO_CATALOG["cafe"]
    elif any(k in combined for k in ["airport", "flight", "plane", "terminal", "boarding", "departure"]):
        pool = PHOTO_CATALOG["airport"]
    elif any(k in combined for k in ["interview", "candidate", "hire", "resume", "cv"]):
        pool = PHOTO_CATALOG["interview"]
    elif any(k in combined for k in ["office", "meeting", "business", "colleague", "workplace", "corporat"]):
        pool = PHOTO_CATALOG["office"]
    elif any(k in combined for k in ["market", "supermarket", "grocery", "shop", "store", "vendor"]):
        pool = PHOTO_CATALOG["market"]
    elif any(k in combined for k in ["library", "book", "study", "reading", "shelf"]):
        pool = PHOTO_CATALOG["library"]
    elif any(k in combined for k in ["hospital", "doctor", "nurse", "clinic", "medical", "patient"]):
        pool = PHOTO_CATALOG["hospital"]
    elif any(k in combined for k in ["park", "garden", "outdoor", "lawn", "walk"]):
        pool = PHOTO_CATALOG["park"]
    elif any(k in combined for k in ["class", "school", "teach", "student", "learn", "lecture"]):
        pool = PHOTO_CATALOG["classroom"]
    elif any(k in combined for k in ["restaurant", "dinner", "lunch", "eat", "dining", "meal", "food"]):
        pool = PHOTO_CATALOG["restaurant"]
    elif any(k in combined for k in ["hotel", "reception", "resort", "lobby", "check-in"]):
        pool = PHOTO_CATALOG["hotel"]
    elif any(k in combined for k in ["tech", "comput", "ai", "software", "program", "code"]):
        pool = PHOTO_CATALOG["technology"]
    elif any(k in combined for k in ["kitchen", "cook", "bake", "chef", "recipe"]):
        pool = PHOTO_CATALOG["kitchen"]
    elif any(k in combined for k in ["nature", "mountain", "beach", "lake", "forest", "hiking"]):
        pool = PHOTO_CATALOG["nature"]
    elif any(k in combined for k in ["fitness", "gym", "sport", "workout", "exercise", "athlet"]):
        pool = PHOTO_CATALOG["fitness"]
    elif any(k in combined for k in ["art", "museum", "gallery", "paint", "exhibit"]):
        pool = PHOTO_CATALOG["art"]
    elif any(k in combined for k in ["city", "street", "urban", "downtown", "traffic", "build"]):
        pool = PHOTO_CATALOG["city"]
    else:
        pool = PHOTO_CATALOG["cafe"]

    # Stable pseudo-random selection based on hash of topic and title
    h = int(hashlib.md5(f"{topic}_{title}".encode("utf-8")).hexdigest(), 16)
    return pool[h % len(pool)]

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

    # Attach authentic visual photography scenes to every card
    for c in cards:
        w = c.get("word", "")
        c["image_url"] = resolve_scene_photo(
            topic=topic,
            title=w,
            context=c.get("meaning", "")
        )

    return cards

def generate_vocabulary_image(word: str, context: str = "", output_dir: Optional[str] = None) -> str:
    """Generate or retrieve authentic visual photograph URL."""
    return resolve_scene_photo(topic=context, title=word)

def generate_picture_scenario(topic: str = "Daily Life", level: str = "intermediate") -> Dict[str, Any]:
    """Generate an authentic Describe the Picture challenge scenario with real scene photograph."""
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

    # High-definition authentic scene photo for IELTS / TOEIC description
    image_url = resolve_scene_photo(
        topic=topic,
        title=title,
        context=image_prompt
    )

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
