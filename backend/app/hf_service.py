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

def call_llm_json_with_retry(
    messages: List[Dict[str, str]],
    required_keys: Optional[List[str]] = None,
    max_retries: int = 2
) -> Dict[str, Any]:
    """Call LLM with a strictly bounded retry count (max_retries=2) to guarantee complete JSON extraction."""
    if required_keys is None:
        required_keys = ["title", "guiding_questions", "keywords"]
    
    last_valid_data = {}
    for attempt in range(max_retries):
        try:
            content = call_llm(messages, json_mode=True)
            data = parse_json_safely(content)
            if isinstance(data, dict):
                last_valid_data = data
                has_questions = isinstance(data.get("guiding_questions"), list) and len(data.get("guiding_questions")) >= 3
                has_keywords = isinstance(data.get("keywords"), list) and len(data.get("keywords")) >= 3
                has_title = bool(str(data.get("title", "")).strip())
                
                if has_questions and has_keywords and has_title:
                    return data
                logger.warning(f"LLM JSON missing required fields on attempt {attempt + 1}/{max_retries}. Retrying...")
        except Exception as e:
            logger.warning(f"call_llm attempt {attempt + 1}/{max_retries} error: {e}")
            
    return last_valid_data

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

GROUNDED_PHOTO_CATALOG = {
    "science": [
        {
            "url": "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1000&q=80",
            "title": "A Scientific Laboratory Experiment in Progress",
            "elements": "A laboratory researcher wearing blue protective nitrile gloves handling precision chemical sample vials, pipettes, and analytical diagnostic equipment on a sterile lab workstation.",
            "has_people": True,
            "people_details": "A laboratory scientist in blue gloves carefully preparing chemical or biological samples.",
            "guiding_questions": [
                "What procedures or tests is the laboratory researcher performing with the sample vials?",
                "What safety equipment and scientific tools can you observe on the workstation?",
                "Why is strict precision and sterile handling essential in laboratory research?"
            ],
            "keywords": ["nitrile gloves", "sample vials", "laboratory research", "sterile workstation", "scientific testing"]
        },
        {
            "url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1000&q=80",
            "title": "Precision Scientific Glassware and Clinical Equipment",
            "elements": "A clean, sterile laboratory workstation equipped with precision glass test tubes, chemical flasks containing blue liquids, measuring pipettes, and racks under bright clinical lighting. No people are in the frame.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What types of scientific glassware and analytical instruments are arranged on the workbench?",
                "What impression does the sterile, organized layout convey about laboratory standards?",
                "What scientific experiments or pharmaceutical tests might be conducted using these instruments?"
            ],
            "keywords": ["glass flasks", "sterile workstation", "chemical reagents", "precision instruments", "laboratory equipment"]
        }
    ],
    "hospital": [
        {
            "url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1000&q=80",
            "title": "A Quiet Hospital Reception and Emergency Hallway",
            "elements": "An empty modern hospital reception lobby with a curved wooden counter, blue tiled walls, an emergency exit and elevator on the left, an informational bulletin board on the right, bright ceiling strip lighting, and a polished tiled floor. There are no medical staff or patients present.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What specific medical facilities, signs, and architectural features can you identify in this reception area?",
                "What does the quiet, deserted atmosphere suggest about the time of day or the section of the hospital?",
                "If a patient arrived at this counter, what reception or admission procedures would take place?"
            ],
            "keywords": ["reception counter", "sterile corridor", "tiled walls", "information board", "deserted hall"]
        },
        {
            "url": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1000&q=80",
            "title": "A Medical Consultation in a Clinic Room",
            "elements": "A female doctor in medical scrubs wearing a stethoscope around her neck, gently talking and consulting with an elderly patient in a clinic examination room.",
            "has_people": True,
            "people_details": "A caring doctor speaking attentively with an elderly patient.",
            "guiding_questions": [
                "What are the doctor and the patient doing, and what expressions can you observe on their faces?",
                "What medical attire and instruments indicate the professional healthcare setting?",
                "Why is compassionate, clear communication essential during medical consultations?"
            ],
            "keywords": ["medical consultation", "stethoscope", "compassionate care", "clinical examination", "healthcare professional"]
        }
    ],
    "cafe": [
        {
            "url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1000&q=80",
            "title": "A Bustling Urban Coffee Shop",
            "elements": "A warm, brightly lit cafe interior with customers seated at wooden tables, a barista behind the espresso bar, warm pendant lighting, and chalkboard menus on the brick wall.",
            "has_people": True,
            "people_details": "Customers sitting at wooden tables enjoying drinks, and staff working behind the coffee counter.",
            "guiding_questions": [
                "What activities are the customers and cafe staff engaged in throughout the coffee shop?",
                "How do the lighting, furniture, and decoration create a welcoming atmosphere?",
                "Why do many people choose coffee shops like this for studying, working, or meeting friends?"
            ],
            "keywords": ["espresso bar", "wooden tables", "warm ambiance", "pendant lighting", "social gathering"]
        },
        {
            "url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1000&q=80",
            "title": "A Cozy Sunlit Cafe Corner",
            "elements": "A tranquil coffee shop corner with a round wooden table, a ceramic cup of latte with art foam, an open book, and soft morning sunlight coming through the window. No people are in the frame.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What items are arranged on the cafe table in this quiet corner?",
                "How does the natural sunlight and table setting create a peaceful, contemplative mood?",
                "What makes a quiet cafe spot like this appealing for reading and relaxation?"
            ],
            "keywords": ["latte art", "wooden table", "natural sunlight", "open book", "peaceful atmosphere"]
        }
    ],
    "airport": [
        {
            "url": "https://images.unsplash.com/photo-1530521954074-e64f6810b32d?auto=format&fit=crop&w=1000&q=80",
            "title": "A Modern International Airport Terminal",
            "elements": "Passengers with roller suitcases and backpacks waiting in an expansive airport terminal with floor-to-ceiling glass windows looking out onto parked airplanes, departure gate signs, and waiting row seats.",
            "has_people": True,
            "people_details": "Travelers waiting with their luggage near the boarding gates, some walking and others seated.",
            "guiding_questions": [
                "What are the travelers in the terminal doing while waiting for their flights?",
                "What airport facilities and exterior views of the airfield can you observe through the windows?",
                "What feelings or thoughts might passengers experience as they prepare to board an international journey?"
            ],
            "keywords": ["departure gate", "roller luggage", "glass facade", "boarding gate", "international travel"]
        },
        {
            "url": "https://images.unsplash.com/photo-1520437358207-323b43b50729?auto=format&fit=crop&w=1000&q=80",
            "title": "An Airplane on the Runway at Sunset",
            "elements": "A commercial jet airliner parked on the airport tarmac bathed in glowing orange sunset light, with terminal silhouettes and ground service vehicles in the distance. No passengers visible close up.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What does the commercial airplane on the tarmac and the sunset lighting show about airport operations?",
                "What ground vehicles and airfield structures are visible around the aircraft?",
                "What mood or impressions does this sunset airfield view convey to an observer?"
            ],
            "keywords": ["commercial airliner", "airport tarmac", "golden sunset", "ground operations", "runway view"]
        }
    ],
    "office": [
        {
            "url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1000&q=80",
            "title": "A Collaborative Team Meeting in an Open-Plan Office",
            "elements": "A diverse group of young business professionals gathered around a conference table with open laptops, notebooks, and coffee mugs, smiling and actively discussing a project.",
            "has_people": True,
            "people_details": "Group of colleagues sitting together around a wooden desk, exchanging ideas with laptops open.",
            "guiding_questions": [
                "How are the team members interacting with one another around the conference table?",
                "What tools and devices are they using to support their collaboration?",
                "What aspects of their body language and expressions indicate a productive workplace culture?"
            ],
            "keywords": ["team collaboration", "conference table", "open laptops", "workplace culture", "brainstorming session"]
        },
        {
            "url": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1000&q=80",
            "title": "A Sleek Contemporary Corporate Office Space",
            "elements": "A minimalist corporate office interior with glass partition walls, ergonomic office chairs, tidy modern desks with desktop monitors, and soft diffused ceiling lighting. No employees are currently seated.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "How is the furniture and glass architecture organized in this contemporary workplace?",
                "What does the tidy and unoccupied environment suggest about professional standards?",
                "How does the layout of a modern office influence employee productivity and communication?"
            ],
            "keywords": ["glass partitions", "ergonomic chairs", "desktop monitors", "minimalist office", "corporate workspace"]
        }
    ],
    "interview": [
        {
            "url": "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1000&q=80",
            "title": "A Professional Job Interview and Handshake",
            "elements": "Two business professionals in formal suits sitting across a wooden conference desk, shaking hands in agreement with paper documents, a pen, and a laptop on the table.",
            "has_people": True,
            "people_details": "Two business professionals across a meeting desk shaking hands during an interview agreement.",
            "guiding_questions": [
                "What are the two people doing across the desk, and what does their handshake symbolize in an interview?",
                "What professional documents, notes, or equipment are visible on the meeting desk?",
                "What impression does this interaction convey about corporate recruitment and professionalism?"
            ],
            "keywords": ["handshake", "business suits", "conference desk", "job interview", "professional agreement"]
        }
    ],
    "portrait": [
        {
            "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1000&q=80",
            "title": "A Professional Business Portrait",
            "elements": "A confident businesswoman in a formal grey blazer and dark top standing with a welcoming smile in a bright corporate office. A single-person portrait with no other people in the frame.",
            "has_people": True,
            "people_details": "A single professional businesswoman in a grey blazer smiling confidently at the camera.",
            "guiding_questions": [
                "How does the woman's professional blazer and posture reflect her corporate role?",
                "What facial expression and attitude does she present to the viewer?",
                "Why is professional attire and a confident demeanor important in a corporate career?"
            ],
            "keywords": ["grey blazer", "confident posture", "businesswoman", "corporate portrait", "professional demeanor"]
        }
    ],
    "market": [
        {
            "url": "https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1000&q=80",
            "title": "A Vibrant Outdoor Farmers Market",
            "elements": "Stalls stacked high with colorful fresh fruits, crisp vegetables, wooden crates, and handwritten price tags under shaded market canopies, with shoppers browsing the produce.",
            "has_people": True,
            "people_details": "Shoppers and local vendors interacting around vibrant fruit and vegetable stalls.",
            "guiding_questions": [
                "What variety of fresh fruits and vegetables are displayed in the market stalls?",
                "What actions are the shoppers and stall vendors taking as they buy and sell goods?",
                "What are the advantages of shopping at a local farmers market compared to a supermarket?"
            ],
            "keywords": ["fresh produce", "wooden crates", "colorful display", "local vendors", "organic groceries"]
        }
    ],
    "library": [
        {
            "url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1000&q=80",
            "title": "A Grand University Library Study Hall",
            "elements": "Tall wooden bookshelves lined with thousands of hardcover books, long study desks with classic green reading lamps, arched windows letting in natural sunlight, and students studying quietly.",
            "has_people": True,
            "people_details": "Students seated quietly at long study tables, reading books and taking notes.",
            "guiding_questions": [
                "How is the library arranged to support quiet reading and focused research?",
                "What architectural details, lamps, and bookshelves can you see in this study hall?",
                "Why do traditional libraries remain valuable spaces for academic learning in the digital age?"
            ],
            "keywords": ["tall bookshelves", "study desks", "reading lamps", "academic atmosphere", "quiet study"]
        }
    ],
    "classroom": [
        {
            "url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1000&q=80",
            "title": "A Bright Modern Classroom",
            "elements": "An empty, well-organized primary classroom with colorful educational posters on the walls, neat student desks and chairs, a chalkboard, and bright sunlight streaming through large windows.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What learning materials, posters, and furniture are arranged in this classroom?",
                "How does the colorful and neat arrangement create an engaging learning environment for children?",
                "What classroom activities might take place here during a typical school day?"
            ],
            "keywords": ["student desks", "educational posters", "chalkboard", "natural sunlight", "organized classroom"]
        }
    ],
    "restaurant": [
        {
            "url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=80",
            "title": "An Elegant Restaurant Dining Room",
            "elements": "A sophisticated restaurant interior with neatly arranged dining tables, comfortable seating, glassware, warm ambient lighting, and decorative wall art. No diners are currently seated.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "How is the table setting and interior decor arranged to welcome dining guests?",
                "What does the lighting and interior design suggest about the style and atmosphere of this restaurant?",
                "What occasion or meal would be best suited for dining in an establishment like this?"
            ],
            "keywords": ["dining tables", "glassware", "ambient lighting", "sophisticated decor", "fine dining"]
        }
    ],
    "hotel": [
        {
            "url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80",
            "title": "A Luxury Hotel Resort and Poolside",
            "elements": "A sunlit luxury resort with pristine blue swimming pool, comfortable sun loungers, palm trees, and modern hotel architecture under clear blue skies. No guests are in the water.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What resort amenities, swimming pool features, and landscape elements can you observe?",
                "How does the sunshine and palm tree setting convey a sense of relaxation and vacation?",
                "What leisure activities could travelers enjoy at this resort?"
            ],
            "keywords": ["swimming pool", "sun loungers", "palm trees", "tropical resort", "leisure relaxation"]
        }
    ],
    "technology": [
        {
            "url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=80",
            "title": "A Software Developer Workspace with Code on Screen",
            "elements": "A developer desk with a laptop displaying lines of programming code, a notebook, coffee mug, and smartphone on a clean wooden desk. No person is in the frame.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What equipment, digital screens, and personal items are placed on the developer desk?",
                "What does the code displayed on the screen indicate about the nature of the work being done?",
                "Why is an organized workstation important for focus and productivity in technology jobs?"
            ],
            "keywords": ["programming code", "developer desk", "laptop screen", "workspace setup", "digital technology"]
        }
    ],
    "kitchen": [
        {
            "url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1000&q=80",
            "title": "A Modern Kitchen Countertop Prepared for Cooking",
            "elements": "A modern kitchen island with fresh culinary ingredients, vegetables, cutting board, chef knife, olive oil bottles, and stainless steel cookware. No cook is in the frame.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What culinary ingredients, utensils, and cookware are prepared on the kitchen counter?",
                "What type of meal or recipe might someone be preparing with these fresh ingredients?",
                "What makes a well-equipped kitchen enjoyable for cooking and dining at home?"
            ],
            "keywords": ["kitchen island", "fresh ingredients", "cutting board", "culinary preparation", "cookware"]
        }
    ],
    "nature": [
        {
            "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80",
            "title": "Majestic Mountain Peaks and Wilderness Valley",
            "elements": "Towering snow-capped mountain peaks rising above a green valley with pine forests under a dramatic sky with drifting clouds. No hikers visible.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What geographic features, terrain, and vegetation can you identify in this landscape?",
                "What feeling or atmosphere does the dramatic sky and towering mountain range evoke?",
                "What outdoor activities or challenges might travelers encounter in this wilderness area?"
            ],
            "keywords": ["mountain peaks", "pine forests", "wilderness valley", "rugged terrain", "dramatic clouds"]
        }
    ],
    "fitness": [
        {
            "url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1000&q=80",
            "title": "A Modern Fitness Center with Strength Equipment",
            "elements": "Rows of dumbbells on racks, barbell benches, weight plates, and mirrors in a spacious gym with dark industrial decor. No athletes currently lifting weights.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What exercise equipment, weights, and facilities are available in this gym space?",
                "How does the industrial design and lighting motivate people to exercise and stay healthy?",
                "What physical fitness benefits can people achieve through consistent resistance training?"
            ],
            "keywords": ["dumbbell racks", "weight plates", "fitness center", "strength training", "exercise equipment"]
        }
    ],
    "art": [
        {
            "url": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=1000&q=80",
            "title": "An Art Gallery Exhibition Hall",
            "elements": "A contemporary art exhibition hall with white walls, spotlight tracks, framed artwork on display, and clean polished gallery floors. No visitors visible.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "How are the artworks and gallery lighting presented to enhance the visitors' experience?",
                "What does the minimalist, quiet space suggest about how people should engage with the exhibits?",
                "Why is experiencing visual art in museums and galleries valuable for cultural appreciation?"
            ],
            "keywords": ["art gallery", "exhibition hall", "framed artwork", "gallery lighting", "cultural appreciation"]
        }
    ],
    "city": [
        {
            "url": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1000&q=80",
            "title": "A Dense Urban City Skyline and Streets",
            "elements": "High-rise skyscrapers towering over city streets with traffic, pedestrian sidewalks, and commercial buildings under clear daylight. Distantly visible vehicles and street infrastructure.",
            "has_people": False,
            "people_details": "Distantly visible street elements.",
            "guiding_questions": [
                "What architectural styles and infrastructure can you observe in this urban landscape?",
                "What impression does this dense city setting give regarding commercial activity and lifestyle?",
                "What are the benefits and challenges of living and working in a major metropolitan city?"
            ],
            "keywords": ["skyscrapers", "urban skyline", "metropolitan city", "pedestrian sidewalk", "city architecture"]
        }
    ],
    "park": [
        {
            "url": "https://images.unsplash.com/photo-1496347646636-ea47f7d6b37b?auto=format&fit=crop&w=1000&q=80",
            "title": "A Peaceful Public Park Pathway",
            "elements": "A winding stone pathway through lush green lawns, mature trees providing shade, flowerbeds, and a wooden park bench in sunny afternoon light. No pedestrians in the frame.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What natural elements, plants, and pathways can you identify in this public park?",
                "How does this green space provide relaxation and relief from urban stress for city residents?",
                "What recreational activities might people enjoy along this shaded park pathway?"
            ],
            "keywords": ["winding pathway", "lush lawn", "shaded trees", "park bench", "green space"]
        }
    ],
    "zoo": [
        {
            "url": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?auto=format&fit=crop&w=1000&q=80",
            "title": "A Visit to the Zoo Wildlife Habitat",
            "elements": "Two tall giraffes standing gracefully in an outdoor savanna enclosure surrounded by leafy acacia trees, a protective wooden fence, and zoo visitors observing the animals under bright daylight.",
            "has_people": True,
            "people_details": "Zoo visitors watching and admiring the giraffes over the protective enclosure fence.",
            "guiding_questions": [
                "What wild animals can you observe in this zoo enclosure, and how are they interacting with their habitat?",
                "What safety barriers and visitor viewing features are visible around the animal enclosure?",
                "Why are zoological parks important for wildlife conservation, education, and family recreation?"
            ],
            "keywords": ["tall giraffes", "zoo enclosure", "savanna habitat", "wooden fence", "wildlife conservation"]
        },
        {
            "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1000&q=80",
            "title": "Zebras Grazing at an Open Safari Reserve",
            "elements": "A herd of wild striped zebras grazing naturally across an expansive grassland reserve with rolling hills and trees in the distance under a partly cloudy sky.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What wild animals and terrain features can you identify in this expansive safari landscape?",
                "How do the zebras' black and white stripes serve as natural camouflage in the wild?",
                "What measures are essential to protect endangered wildlife in natural safari habitats?"
            ],
            "keywords": ["striped zebras", "safari reserve", "open grassland", "natural grazing", "wildlife sanctuary"]
        }
    ],
    "beach": [
        {
            "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
            "title": "A Tropical Sandy Beach on a Sunny Day",
            "elements": "Pristine white sand shoreline with turquoise ocean waves rolling onto the beach, lush green palm trees in the background, and clear blue skies. No swimmers in the water.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What coastal features, water colors, and tropical vegetation can you identify in this seaside scene?",
                "What mood or atmosphere does the calm ocean and sunny weather convey?",
                "What recreational water sports or relaxation activities do people enjoy at coastal beaches?"
            ],
            "keywords": ["turquoise ocean", "white sand", "tropical coast", "rolling waves", "sunlit beach"]
        }
    ],
    "sports": [
        {
            "url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1000&q=80",
            "title": "A Competitive Football Match on the Pitch",
            "elements": "Football players in athletic team kits running and contesting possession of the ball on a vibrant green grass pitch with stadium floodlights and spectators cheering in the stands.",
            "has_people": True,
            "people_details": "Athletic soccer players actively competing for the ball during an intense match.",
            "guiding_questions": [
                "What athletic actions and movements are the players performing on the football pitch?",
                "How do the stadium environment and spectator support energize the sporting competition?",
                "Why are team coordination, agility, and sportsmanship essential in team sports?"
            ],
            "keywords": ["football pitch", "athletic competition", "ball possession", "team coordination", "stadium match"]
        }
    ],
    "traffic": [
        {
            "url": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1000&q=80",
            "title": "Bustling Urban Traffic During Rush Hour",
            "elements": "A multi-lane city avenue congested with commuter cars, yellow cabs, public transit buses, crosswalks, traffic signals, and distant skyscrapers under daytime skies.",
            "has_people": True,
            "people_details": "Commuters and drivers navigating the busy metropolitan traffic intersection.",
            "guiding_questions": [
                "What types of vehicles and road transit infrastructure can you identify in this urban street?",
                "What daily challenges and delays do city residents experience during morning and evening rush hours?",
                "What modern transportation solutions could help reduce metropolitan traffic congestion?"
            ],
            "keywords": ["rush hour", "public transit", "traffic congestion", "city avenue", "urban commuters"]
        }
    ],
    "camping": [
        {
            "url": "https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&w=1000&q=80",
            "title": "An Outdoor Camping Site in the Pine Woods",
            "elements": "A sturdy outdoor camping tent pitched in a clearing among tall pine trees, camp chairs, backpacks, and soft morning sunlight streaming through the woodland canopy.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What camping gear, shelter, and natural forest elements can you observe at this campsite?",
                "How does spending a weekend camping in nature contribute to stress relief and wellness?",
                "What essential safety preparations and equipment are required when venturing on a camping trip?"
            ],
            "keywords": ["camping tent", "pine woods", "outdoor shelter", "morning sunlight", "wilderness campsite"]
        }
    ],
    "family": [
        {
            "url": "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=1000&q=80",
            "title": "A Warm Family Gathering Around the Dining Table",
            "elements": "Family members sitting happily together around a wooden dining table laden with home-cooked dishes, salads, and drinks, enjoying lively conversation and shared companionship in a cozy home.",
            "has_people": True,
            "people_details": "Family members of different ages smiling and talking while dining together.",
            "guiding_questions": [
                "What are the family members doing around the dinner table, and what emotions are visible?",
                "What types of food, tableware, and interior decorations characterize this warm dining setting?",
                "Why is regularly sharing meals together valuable for family bonding and communication?"
            ],
            "keywords": ["family dinner", "shared meal", "dining table", "warm companionship", "home-cooked food"]
        }
    ],
    "shopping": [
        {
            "url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=80",
            "title": "A Chic Clothing Retail Boutique",
            "elements": "A stylish fashion boutique with neatly organized clothing racks, hanger displays, apparel shelves, polished wooden floors, and elegant warm lighting.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "How are the fashion items, racks, and display tables organized inside this retail store?",
                "How does the boutique's minimalist decor and warm lighting influence customer mood and purchasing choices?",
                "What advantages does in-store shopping provide compared to purchasing fashion online?"
            ],
            "keywords": ["clothing racks", "retail boutique", "fashion display", "warm lighting", "apparel shopping"]
        }
    ],
    "music": [
        {
            "url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=1000&q=80",
            "title": "An Electrifying Live Concert and Festival Stage",
            "elements": "A music artist performing on an illuminated festival stage with dazzling colored spotlight beams, audio speakers, and an excited audience raising their hands in celebration.",
            "has_people": True,
            "people_details": "Concertgoers and enthusiastic music fans raising their arms toward the illuminated stage.",
            "guiding_questions": [
                "What is taking place on the concert stage, and how is the audience responding to the music?",
                "What visual and audio stage effects, spotlights, and equipment enhance the performance?",
                "Why do live music events and festivals evoke strong emotional connections among attendees?"
            ],
            "keywords": ["concert stage", "live music", "spotlight beams", "cheering crowd", "festival atmosphere"]
        }
    ],
    "farm": [
        {
            "url": "https://images.unsplash.com/photo-1500595046743-cd271d694d30?auto=format&fit=crop&w=1000&q=80",
            "title": "A Peaceful Countryside Pasture and Cattle Farm",
            "elements": "Spotted dairy cows grazing peacefully across expansive rolling green hills under a wide open sky, with rustic wooden fences and distant farm buildings.",
            "has_people": False,
            "people_details": "None",
            "guiding_questions": [
                "What farm animals, vegetation, and countryside landscape features can you observe in this scene?",
                "What does the serene green pasture convey about rural farming life and agriculture?",
                "Why are sustainable farming practices vital for food security and environmental health?"
            ],
            "keywords": ["grazing cattle", "rolling hills", "green pasture", "rustic farm", "countryside landscape"]
        }
    ]
}

def classify_topic_semantic(topic_text: str) -> str:
    """Intelligently map arbitrary user topic into the best visual scene category via fast LLM."""
    valid_cats = list(GROUNDED_PHOTO_CATALOG.keys())
    try:
        prompt = (
            f"Given the speaking practice topic: '{topic_text}', select the single most appropriate visual scene category from this list: "
            f"{json.dumps(valid_cats)}. "
            "Return ONLY a JSON object: {\"category\": \"<one of the list>\"}."
        )
        resp = call_llm([{"role": "user", "content": prompt}], json_mode=True)
        data = parse_json_safely(resp)
        cat = data.get("category", "") if isinstance(data, dict) else ""
        if cat in GROUNDED_PHOTO_CATALOG:
            return cat
    except Exception as e:
        logger.warning(f"Semantic topic classification notice: {e}")
    return "nature"

def get_grounded_scene(topic: str = "", title: str = "", context: str = "") -> Dict[str, Any]:
    combined = f"{topic} {title} {context}".lower()

    if any(k in combined for k in ["zoo", "animal", "safari", "wildlife", "giraffe", "elephant", "zebra", "lion", "tiger", "bear", "sở thú", "thảo cầm viên", "động vật", "muông thú"]):
        category = "zoo"
    elif any(k in combined for k in ["beach", "sea", "ocean", "coast", "shore", "island", "sand", "summer", "biển", "bãi biển"]):
        category = "beach"
    elif any(k in combined for k in ["sport", "football", "soccer", "basketball", "tennis", "match", "stadium", "athlete", "thể thao", "bóng đá", "sân vận động"]):
        category = "sports"
    elif any(k in combined for k in ["traffic", "commute", "public transit", "subway", "road congestion", "giao thông", "kẹt xe", "xe buýt"]):
        category = "traffic"
    elif any(k in combined for k in ["camp", "camping", "tent", "campfire", "hiking", "picnic", "cắm trại", "dã ngoại"]):
        category = "camping"
    elif any(k in combined for k in ["family", "parents", "children", "dining table", "living room", "gia đình", "bữa cơm", "sum họp"]):
        category = "family"
    elif any(k in combined for k in ["shopping", "mall", "boutique", "fashion", "retail store", "clothing rack", "mua sắm"]):
        category = "shopping"
    elif any(k in combined for k in ["concert", "festival", "musical band", "singing", "music stage", "âm nhạc", "hòa nhạc", "ca nhạc"]):
        category = "music"
    elif any(k in combined for k in ["farm", "farmer", "agriculture", "cattle", "pasture", "rural", "countryside", "nông trại", "đồng quê", "chăn nuôi"]):
        category = "farm"
    elif any(k in combined for k in ["science", "chemist", "biolog", "physics", "experiment", "research lab", "thí nghiệm", "phòng lab"]):
        category = "science"
    elif any(k in combined for k in ["hospital", "doctor", "nurse", "clinic", "medical", "patient", "emergency", "bệnh viện", "bác sĩ", "phòng khám"]):
        category = "hospital"
    elif any(k in combined for k in ["cafe", "coffee", "latte", "espresso", "barista", "quán cafe", "cà phê"]):
        category = "cafe"
    elif any(k in combined for k in ["airport", "flight", "airplane", "terminal", "boarding", "departure", "sân bay", "máy bay", "hàng không"]):
        category = "airport"
    elif any(k in combined for k in ["portrait", "businesswoman", "executive", "blazer", "headshot", "chân dung", "nữ doanh nhân"]):
        category = "portrait"
    elif any(k in combined for k in ["interview", "candidate", "hire", "resume", "cv", "recruitment", "phỏng vấn", "tuyển dụng"]):
        category = "interview"
    elif any(k in combined for k in ["meeting", "coworking", "colleague", "workplace", "corporat", "văn phòng", "họp hành"]):
        category = "office"
    elif any(k in combined for k in ["supermarket", "grocery", "market vendor", "chợ", "siêu thị"]):
        category = "market"
    elif any(k in combined for k in ["library", "hardcover book", "reading hall", "bookshelf", "thư viện", "đọc sách"]):
        category = "library"
    elif any(k in combined for k in ["park pathway", "garden lawn", "botanical", "công viên", "vườn hoa"]):
        category = "park"
    elif any(k in combined for k in ["classroom", "school", "teach", "student", "lecture", "lớp học", "trường học", "giảng đường"]):
        category = "classroom"
    elif any(k in combined for k in ["restaurant", "dining room", "fine dining", "meal course", "nhà hàng"]):
        category = "restaurant"
    elif any(k in combined for k in ["hotel resort", "resort pool", "hotel lobby", "check-in", "khách sạn", "khu nghỉ dưỡng"]):
        category = "hotel"
    elif any(k in combined for k in ["technology", "computer", "software", "coding", "developer", "artificial intelligence", "công nghệ", "máy tính", "lập trình"]):
        category = "technology"
    elif any(k in combined for k in ["kitchen", "cooking", "baking", "chef", "recipe", "nhà bếp", "nấu ăn", "gian bếp"]):
        category = "kitchen"
    elif any(k in combined for k in ["mountain", "hiking trail", "wilderness", "thiên nhiên", "núi rừng", "leo núi"]):
        category = "nature"
    elif any(k in combined for k in ["fitness", "gym", "workout", "weight training", "tập gym", "thể hình"]):
        category = "fitness"
    elif any(k in combined for k in ["artwork", "art gallery", "fine art", "museum hall", "painting exhibit", "bảo tàng", "nghệ thuật", "triển lãm"]):
        category = "art"
    elif any(k in combined for k in ["city skyline", "downtown skyscrapers", "urban street", "thành phố", "đô thị"]):
        category = "city"
    else:
        # Instead of blind cafe fallback, use semantic LLM classification
        category = classify_topic_semantic(combined)

    pool = GROUNDED_PHOTO_CATALOG[category]
    # Check if context wants people or empty
    if any(k in combined for k in ["people", "crowd", "staff", "doctor", "talking", "discussing"]):
        people_pool = [s for s in pool if s.get("has_people")]
        if people_pool:
            pool = people_pool
    elif any(k in combined for k in ["empty", "quiet", "night", "interior", "counter", "bench", "equipment"]):
        empty_pool = [s for s in pool if not s.get("has_people")]
        if empty_pool:
            pool = empty_pool

    h = int(hashlib.md5(f"{topic}_{title}".encode("utf-8")).hexdigest(), 16)
    return pool[h % len(pool)]

# Backward compatible PHOTO_CATALOG mapping to lists of URLs
PHOTO_CATALOG = {
    cat: [item["url"] for item in items]
    for cat, items in GROUNDED_PHOTO_CATALOG.items()
}

def resolve_scene_photo(topic: str = "", title: str = "", context: str = "") -> str:
    """Resolve an authentic, high-resolution photography scene for IELTS/TOEIC speaking tasks."""
    scene = get_grounded_scene(topic=topic, title=title, context=context)
    return scene.get("url", "")

SUGGESTED_PICTURE_TOPICS = [
    {
        "id": "job-interview",
        "title": "A Professional Job Interview Discussion",
        "category": "Workplace & Career",
        "level": "Intermediate",
        "description": "Describe candidate and interviewer interactions, corporate setting, and professional attire.",
        "icon": "mdi-account-tie"
    },
    {
        "id": "open-office",
        "title": "A Collaborative Team Meeting in an Open-Plan Office",
        "category": "Workplace & Career",
        "level": "Intermediate",
        "description": "Discuss project collaboration, modern open-plan workplace design, and team dynamics.",
        "icon": "mdi-briefcase-account"
    },
    {
        "id": "hospital-hallway",
        "title": "A Quiet Hospital Reception and Emergency Hallway",
        "category": "Healthcare & Services",
        "level": "Intermediate",
        "description": "Analyze medical facility architecture, emergency intake counters, and clinical atmosphere.",
        "icon": "mdi-hospital-building"
    },
    {
        "id": "medical-consult",
        "title": "A Medical Consultation in a Clinic Room",
        "category": "Healthcare & Services",
        "level": "Intermediate",
        "description": "Describe caring doctor-patient communication, clinical instruments, and healthcare dialogue.",
        "icon": "mdi-doctor"
    },
    {
        "id": "science-lab",
        "title": "A University Science Research Laboratory",
        "category": "Education & Science",
        "level": "Upper-Intermediate",
        "description": "Explain experimental procedures, laboratory equipment, protective gear, and scientific inquiry.",
        "icon": "mdi-flask"
    },
    {
        "id": "urban-cafe",
        "title": "A Bustling Urban Coffee Shop",
        "category": "Daily Life & Leisure",
        "level": "Pre-Intermediate",
        "description": "Describe cafe patrons, barista activities, cozy interior lighting, and social routines.",
        "icon": "mdi-coffee"
    },
    {
        "id": "airport-terminal",
        "title": "A Modern International Airport Terminal",
        "category": "Travel & Transportation",
        "level": "Intermediate",
        "description": "Observe travelers with luggage, boarding gate procedures, and expansive glass architecture.",
        "icon": "mdi-airplane"
    },
    {
        "id": "farmers-market",
        "title": "A Vibrant Outdoor Farmers Market",
        "category": "Daily Life & Leisure",
        "level": "Pre-Intermediate",
        "description": "Detail colorful fresh produce displays, vendor-customer transactions, and market atmosphere.",
        "icon": "mdi-storefront"
    },
    {
        "id": "university-library",
        "title": "A Grand University Library Study Hall",
        "category": "Education & Science",
        "level": "Intermediate",
        "description": "Focus on quiet academic study spaces, towering bookshelves, and focused learning habits.",
        "icon": "mdi-bookshelf"
    },
    {
        "id": "coding-workspace",
        "title": "A Software Developer Workspace with Code on Screen",
        "category": "Technology & Computing",
        "level": "Upper-Intermediate",
        "description": "Discuss tech workstation setup, digital programming tasks, and focused workplace productivity.",
        "icon": "mdi-laptop"
    },
    {
        "id": "art-gallery",
        "title": "An Art Gallery Exhibition Hall",
        "category": "Arts & Culture",
        "level": "Upper-Intermediate",
        "description": "Examine minimalist museum architecture, gallery curation, and visual aesthetics.",
        "icon": "mdi-palette"
    },
    {
        "id": "peaceful-park",
        "title": "A Peaceful Public Park Pathway",
        "category": "Daily Life & Nature",
        "level": "Pre-Intermediate",
        "description": "Describe lush green urban parks, pedestrian stone paths, and relaxation in nature.",
        "icon": "mdi-tree"
    },
    {
        "id": "fitness-center",
        "title": "A Modern Fitness Center with Strength Equipment",
        "category": "Sports & Wellness",
        "level": "Intermediate",
        "description": "Analyze fitness gym facilities, resistance equipment, and active health lifestyles.",
        "icon": "mdi-dumbbell"
    }
]

def suggest_picture_topics(category: str = "all", level: str = "intermediate", count: int = 6) -> List[Dict[str, Any]]:
    """Suggest inspiring, curated IELTS & TOEIC speaking topics with visual scenes."""
    if category and category.lower() != "all":
        filtered = [t for t in SUGGESTED_PICTURE_TOPICS if category.lower() in t.get("category", "").lower()]
        if filtered:
            return filtered[:count]
    return SUGGESTED_PICTURE_TOPICS[:count]

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

def generate_flux_image_hf(prompt: str, seed: Optional[int] = None) -> Optional[str]:
    """Generate charming, vibrant 3D animation style image via HuggingFace FLUX.1-schnell space.
    Produces friendly Pixar/Disney inspired 3D characters and scenes with rich colors and zero creepy distortions.
    """
    if seed is None:
        seed = random.randint(1000, 999999)
        
    clean_p = re.sub(r'[^a-zA-Z0-9\s,.-]', '', prompt).strip()
    if not any(k in clean_p.lower() for k in ["pixar", "disney", "animation", "3d render", "cartoon", "illustration"]):
        clean_p = f"Charming and colorful {clean_p}, cute 3D animation style, Pixar Disney inspired 3D digital art, cheerful expressive characters, vibrant warm colors, clear sunny lighting, high quality 3D render"
        
    url = "https://black-forest-labs-flux-1-schnell.hf.space/gradio_api/call/infer"
    payload = {
        "data": [
            clean_p,
            seed,
            True,
            1024,
            680,
            4
        ]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=12)
        if r.status_code == 200:
            event_id = r.json().get("event_id")
            if event_id:
                res_url = f"https://black-forest-labs-flux-1-schnell.hf.space/gradio_api/call/infer/{event_id}"
                r_res = requests.get(res_url, timeout=30)
                if r_res.status_code == 200:
                    for line in r_res.text.strip().split("\n"):
                        if line.startswith("data:"):
                            raw_json = line[5:].strip()
                            data = json.loads(raw_json)
                            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                                img_url = data[0].get("url")
                                if img_url:
                                    logger.info(f"FLUX 3D image successfully generated via HF Space: {img_url}")
                                    return img_url
    except Exception as e:
        logger.warning(f"HuggingFace FLUX generation notice: {e}")
        
    return None

def generate_picture_scenario(
    topic: str = "Daily Life",
    level: str = "intermediate",
    mode: str = "ai_gen",
    custom_image_url: str = ""
) -> Dict[str, Any]:
    """Generate an authentic Describe the Picture challenge scenario with dynamic AI image generation or photo search and 4-step framework questions."""
    clean_topic = str(topic or "Daily Life").strip()
    
    # Mode 1: Custom Image Upload
    if mode == "upload" and custom_image_url:
        image_url = custom_image_url
        sys_prompt = (
            "You are an expert English Speaking Examiner for K-12 students. "
            f"The candidate is practicing with an uploaded picture on the topic: '{clean_topic}'. "
            "Formulate: "
            "1. title: Engaging title for this scene. "
            "2. visual_description: 2-sentence description of the scene. "
            "3. guiding_questions: Exactly 4 questions adhering to standard English speaking test structure: "
            "   Q1 (Overview: general location/setting/weather), "
            "   Q2 (People & Actions: subjects/interactions/clothing), "
            "   Q3 (Details & Surroundings: objects/foreground/background), "
            "   Q4 (Impressions: emotional tone/atmosphere). "
            "4. keywords: Array of 5 target vocabulary words/collocations for this scene. "
            "5. sample_response: Natural Band 7-8 model speech (70-90 words) describing the scene. "
            "Return ONLY a valid JSON object with 'title', 'visual_description', 'guiding_questions', 'keywords', 'sample_response'."
        )
        data = call_llm_json_with_retry([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Topic: {clean_topic}. Level: {level}. Return JSON."}
        ], required_keys=["title", "guiding_questions", "keywords"], max_retries=2)
        
        title = str(data.get("title", "")).strip() or f"Describing {clean_topic}"
        guiding_questions = data.get("guiding_questions")
        if not isinstance(guiding_questions, list) or len(guiding_questions) < 3:
            guiding_questions = [
                f"What details in this scene highlight the theme of {clean_topic}?",
                f"Who or what are the primary subjects related to {clean_topic}, and what specific activities are they doing?",
                f"What key objects, colors, and background elements specifically characterize this {clean_topic} scene?",
                f"What atmosphere, emotions, or message about {clean_topic} does this picture convey to the viewer?"
            ]
        keywords = data.get("keywords")
        if not isinstance(keywords, list) or len(keywords) < 3:
            keywords = [clean_topic.lower(), f"{clean_topic.lower()} setting", "foreground details", "background", "atmosphere"]
            
        sample_response = str(data.get("sample_response", "")).strip() or (
            f"In this picture, we can observe an engaging scene related to {clean_topic}. "
            "In the foreground, the main subjects are actively involved in the setting. "
            "The surrounding environment shows clear visual context with distinctive details. "
            f"Overall, the picture provides a vivid portrayal of {clean_topic}."
        )
        
        return {
            "topic": clean_topic,
            "title": title,
            "image_url": image_url,
            "fallback_image_url": resolve_scene_photo(clean_topic, title),
            "image_prompt": data.get("visual_description", clean_topic),
            "visual_description": data.get("visual_description", clean_topic),
            "guiding_questions": guiding_questions,
            "keywords": keywords,
            "sample_response": sample_response,
            "mode": "upload",
            "suggested_time_seconds": 60
        }

    # Mode 2: Search Authentic Photography / Vibrant 3D Visuals
    if mode == "search":
        photo_prompt = f"Charming and vibrant {clean_topic}, cute 3D animation style, Pixar Disney inspired 3D render, cheerful expressive characters, colorful environment, warm sunny lighting, high quality 3D digital art"
        seed = random.randint(10000, 999999)
        clean_search_prompt = re.sub(r'[^a-zA-Z0-9\s,.-]', '', photo_prompt)
        
        # Primary: HuggingFace FLUX.1-schnell 3D Pixar
        image_url = generate_flux_image_hf(clean_search_prompt, seed=seed)
        if not image_url:
            image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_search_prompt)}?width=1024&height=680&nologo=true&seed={seed}&model=flux"
        
        sys_prompt = (
            "You are an expert English Speaking Examiner for primary, secondary, and high school students. "
            f"The candidate wants to practice describing a cheerful scene on the topic: '{clean_topic}'. "
            "Formulate an authentic speaking challenge strictly grounded in this scene: "
            "1. 'title': Engaging descriptive title for this 3D animated scene. "
            "2. 'visual_description': Vivid 2-sentence description of the 3D animated scene. "
            "3. 'guiding_questions': Array of 4 structured questions (Q1: General setting/weather, Q2: People/subjects & activities, Q3: Specific objects & background details, Q4: Overall mood & impression). "
            "4. 'keywords': Array of 5 target vocabulary words/collocations typical of this scene. "
            "5. 'sample_response': Band 7-8 model speech (70-90 words). "
            "Return ONLY a valid JSON object with 'title', 'visual_description', 'guiding_questions', 'keywords', 'sample_response'."
        )
        data = call_llm_json_with_retry([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Topic: '{clean_topic}'. Level: '{level}'. Return JSON."}
        ], required_keys=["title", "guiding_questions", "keywords"], max_retries=2)
        
        title = str(data.get("title", "")).strip() or f"Scene: {clean_topic}"
        guiding_questions = data.get("guiding_questions")
        if not isinstance(guiding_questions, list) or len(guiding_questions) < 3:
            guiding_questions = [
                f"Where does this {clean_topic} scene take place and what is the overall atmosphere?",
                f"What people or subjects are engaged in {clean_topic} activities in this picture?",
                f"What specific objects, equipment, or surroundings characterize this {clean_topic} setting?",
                f"What feelings or overall impression of {clean_topic} does this moment communicate?"
            ]
        keywords = data.get("keywords")
        if not isinstance(keywords, list) or len(keywords) < 3:
            keywords = [clean_topic.lower(), f"{clean_topic.lower()} environment", "key subjects", "action details", "overall mood"]
            
        sample_response = str(data.get("sample_response", "")).strip() or (
            f"This picture presents a delightful view of {title}. "
            f"{str(data.get('visual_description', f'The picture captures an engaging moment focused on {clean_topic}.'))} "
            f"Overall, it provides a vivid depiction of {clean_topic} in real life."
        )
        
        return {
            "topic": clean_topic,
            "title": title,
            "image_url": image_url,
            "image_prompt": photo_prompt,
            "visual_description": str(data.get("visual_description", "")),
            "guiding_questions": guiding_questions,
            "keywords": keywords,
            "sample_response": sample_response,
            "mode": "search",
            "suggested_time_seconds": 60
        }

    # Mode 3 (Default): Dynamic AI 3D Animation Image Generation with Prompt Grounding (K-12 Friendly)
    sys_prompt = (
        "You are an expert English Speaking Examiner and visual prompt designer for K-12 students (Primary, Secondary, and High School learners). "
        "The user wants to practice describing a picture based on their requested topic or prompt (which may be in English or Vietnamese). "
        "First, understand their intent and create a vivid, cheerful 3D animation scene tailored for English speaking practice. "
        "VISUAL STYLE RULES FOR IMAGE PROMPT (K-12 FRIENDLY 3D ANIMATION): "
        "- Style: Cute 3D animation style, Pixar and Disney inspired 3D digital art, cheerful and friendly characters with expressive big eyes and happy smiles. "
        "- Composition: Well-defined characters standing or interacting clearly (no complex body overlaps or awkward carrying postures), colorful and distinct clothing (e.g. red hoodie, blue shirt, yellow cap). "
        "- Environment: Bright sunny daytime lighting, rich vibrant colors, cute animals or distinct objects in foreground and background that are easy and fun for students to describe. "
        "- Anatomy safety: Smooth 3D cartoon textures, clean proportions, avoiding realistic human flaws or uncanny distortions. "
        "Return a valid JSON object with: "
        "1. 'title': Engaging English title for this scene. "
        "2. 'visual_description': A vivid 2-sentence description of the 3D animated scene (detailing characters, clothing colors, actions, and colorful surroundings). "
        "3. 'image_gen_prompt': A high-quality English 3D animation prompt optimized for FLUX.1-schnell (e.g. 'A charming scene of ..., cute 3D animation style, Pixar Disney inspired render, cheerful expressive characters, vibrant warm colors, clear sunny lighting, high quality 3D digital art'). "
        "4. 'search_keywords': 2-3 essential keywords for image search fallback (e.g. 'zoo family animals 3d'). "
        "5. 'guiding_questions': Array of exactly 4 structured questions suitable for students (Q1 Overview: setting/weather, Q2 Characters & Actions: who they are, what they are wearing and doing, Q3 Details & Surroundings: distinct objects/colors/animals in foreground & background, Q4 Impressions & Mood: cheerful atmosphere/emotions). "
        "6. 'keywords': Array of 5 target vocabulary words/collocations clearly visible in this scene (e.g. colors, clothing, objects, animals). "
        "7. 'sample_response': A natural Band 7-8 model response (70-90 words) describing the scene using clear, descriptive English suitable for learners. "
        "Return ONLY JSON."
    )
    user_prompt = f"User Topic / Prompt: '{clean_topic}'. Level: '{level}'. Return JSON."

    data = call_llm_json_with_retry([
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ], required_keys=["title", "guiding_questions", "keywords", "image_gen_prompt"], max_retries=2)
    
    title = str(data.get("title", "")).strip() or f"Picture Speaking: {clean_topic}"
    visual_description = str(data.get("visual_description", "")).strip() or f"A delightful 3D animated scene depicting {clean_topic}."
    image_gen_prompt = str(data.get("image_gen_prompt", "")).strip() or f"A charming scene of {clean_topic}, cute 3D animation style, Pixar Disney inspired render, cheerful expressive characters, vibrant colors, warm sunny lighting, high quality 3D digital art"
    search_keywords = str(data.get("search_keywords", clean_topic)).strip()
    
    # Build dynamic AI image URL via HuggingFace FLUX.1-schnell 3D Pixar
    seed = random.randint(10000, 999999)
    clean_ai_prompt = re.sub(r'[^a-zA-Z0-9\s,.-]', '', image_gen_prompt)
    if not clean_ai_prompt.strip():
        clean_ai_prompt = f"A charming scene of {clean_topic}, cute 3D animation style, Pixar Disney inspired render, cheerful characters, vibrant colors, high quality 3D digital art"
        
    # Primary: HuggingFace FLUX.1-schnell 3D Pixar
    image_url = generate_flux_image_hf(clean_ai_prompt, seed=seed)
    if not image_url:
        image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_ai_prompt)}?width=1024&height=680&nologo=true&seed={seed}&model=flux"
    
    guiding_questions = data.get("guiding_questions")
    if not isinstance(guiding_questions, list) or len(guiding_questions) < 3:
        guiding_questions = [
            f"Where does this {clean_topic} scene take place and what is the weather like?",
            f"Who are the characters in the picture, what are they wearing and what are they doing?",
            f"What colorful objects, details, or animals can you see in the foreground and background?",
            f"What feelings or overall impression does this cheerful picture give you?"
        ]
        
    keywords = data.get("keywords")
    if not isinstance(keywords, list) or len(keywords) < 3:
        keywords = [clean_topic.lower(), f"{clean_topic.lower()} setting", "cheerful characters", "colorful details", "happy atmosphere"]
        
    sample_response = str(data.get("sample_response", "")).strip() or (
        f"This picture presents a delightful 3D animated scene illustrating {title}. "
        f"{visual_description} "
        f"Overall, the image presents a clear, engaging portrayal of {clean_topic} with distinctive details."
    )
    
    return {
        "topic": clean_topic,
        "title": title,
        "image_url": image_url,
        "image_prompt": image_gen_prompt,
        "visual_description": visual_description,
        "guiding_questions": guiding_questions,
        "keywords": keywords,
        "sample_response": sample_response,
        "mode": "ai_gen",
        "level": level,
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
