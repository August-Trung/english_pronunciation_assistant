import streamlit as st
import whisper
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import json
import re

# Cấu hình trang
st.set_page_config(
    page_title="Phân tích Phát Âm Tiếng Anh",
    page_icon="🎤",
    layout="wide",
)

# CSS tùy chỉnh
st.markdown(
    """
<style>
    .stButton>button {
        width: 100%;
    }
    .score-excellent {
        color: #00c853;
        font-size: 48px;
        font-weight: bold;
    }
    .score-good {
        color: #ffd600;
        font-size: 48px;
        font-weight: bold;
    }
    .score-average {
        color: #ff9800;
        font-size: 48px;
        font-weight: bold;
    }
    .score-poor {
        color: #ff5252;
        font-size: 48px;
        font-weight: bold;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .streak-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Khởi tạo session state
if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = None

if "user_name" not in st.session_state:
    st.session_state.user_name = "Học viên"

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 10

if "model_size" not in st.session_state:
    st.session_state.model_size = "base"


@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load mô hình Whisper (chỉ load 1 lần)"""
    try:
        model = whisper.load_model(model_size)
        return model
    except Exception as e:
        st.error(f"Lỗi khi load Whisper model: {e}")
        return None


# Tự động load model lần đầu
if st.session_state.model is None:
    st.session_state.model = load_whisper_model("base")


def convert_audio_to_wav(audio_file):
    """Chuyển đổi file audio về định dạng WAV chuẩn"""
    try:
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_file.name, format="wav")
        return temp_file.name
    except Exception as e:
        st.error(f"Lỗi chuyển đổi audio: {e}")
        return None


def transcribe_audio(audio_path, model):
    """Nhận dạng giọng nói từ file audio bằng Whisper"""
    try:
        result = model.transcribe(audio_path, language="en")
        return result["text"].strip()
    except Exception as e:
        st.error(f"Lỗi nhận dạng giọng nói: {e}")
        return None


def check_grammar_basic(text):
    """
    Kiểm tra lỗi ngữ pháp cơ bản (mô phỏng)
    Trả về điểm từ 0-2
    """
    words = text.lower().split()
    errors = []
    score = 2.0

    # Kiểm tra Subject-Verb Agreement cơ bản
    common_errors = [
        ("i is", "i am"),
        ("he are", "he is"),
        ("she are", "she is"),
        ("they is", "they are"),
        ("we is", "we are"),
        ("i does", "i do"),
        ("he do", "he does"),
        ("she do", "she does"),
    ]

    text_lower = text.lower()
    for wrong, correct in common_errors:
        if wrong in text_lower:
            errors.append(f"Lỗi S-V: '{wrong}' → '{correct}'")
            score -= 0.3

    # Kiểm tra thiếu động từ (câu không có động từ phổ biến)
    sentences = re.split(r"[.!?]", text)
    basic_verbs = [
        "is",
        "are",
        "am",
        "was",
        "were",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "can",
        "could",
        "will",
        "would",
        "should",
        "go",
        "get",
        "make",
        "take",
        "see",
        "know",
    ]

    for sent in sentences:
        sent_words = sent.lower().split()
        if len(sent_words) > 3:  # Câu đủ dài
            has_verb = any(verb in sent_words for verb in basic_verbs)
            if not has_verb:
                score -= 0.2

    return max(score, 0), errors


def check_fluency(text):
    """
    Đánh giá độ trôi chảy và tự nhiên (dựa trên cấu trúc câu)
    Trả về điểm từ 0-2
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, ["Không có nội dung"]

    # Đếm số câu
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    # Tính độ dài câu trung bình
    avg_sentence_length = word_count / max(sentence_count, 1)

    score = 1.5  # Điểm cơ bản
    issues = []

    # Độ dài bài nói
    if word_count >= 40:
        score += 0.3
    elif word_count < 20:
        score -= 0.3
        issues.append("Bài nói quá ngắn")

    # Độ dài câu (câu quá ngắn hoặc quá dài đều không tốt)
    if 5 <= avg_sentence_length <= 15:
        score += 0.2
    elif avg_sentence_length < 3:
        issues.append("Câu quá ngắn, thiếu tự nhiên")
        score -= 0.2

    return max(min(score, 2.0), 0), issues


def check_vocabulary(text):
    """
    Đánh giá từ vựng (đa dạng và phù hợp chủ đề)
    Trả về điểm từ 0-2
    """
    words = text.lower().split()
    words_clean = [re.sub(r"[^a-z]", "", w) for w in words]
    words_clean = [w for w in words_clean if len(w) > 2]

    if len(words_clean) == 0:
        return 0, ["Không có từ vựng"]

    # Tính độ đa dạng từ vựng
    unique_words = set(words_clean)
    vocab_diversity = len(unique_words) / len(words_clean)

    # Đếm từ phức tạp (>= 6 ký tự)
    complex_words = [w for w in words_clean if len(w) >= 6]
    complex_ratio = len(complex_words) / len(words_clean)

    score = 1.0  # Điểm cơ bản
    issues = []

    # Điểm từ độ đa dạng
    if vocab_diversity >= 0.6:
        score += 0.5
    elif vocab_diversity < 0.4:
        issues.append("Từ vựng bị lặp lại nhiều")
        score -= 0.2

    # Điểm từ độ phức tạp
    if complex_ratio >= 0.2:
        score += 0.5
    elif complex_ratio < 0.1:
        issues.append("Nên sử dụng từ vựng đa dạng hơn")
        score -= 0.2

    return max(min(score, 2.0), 0), issues


def check_pronunciation(text, reference_text=None):
    """
    Đánh giá phát âm dựa trên:
    1. Độ CHÍNH XÁC và MẠCH LẠC của transcription (nếu không có reference)
    2. Độ TƯƠNG ĐỒNG với câu gốc (nếu có reference)
    Trả về điểm từ 0-2 và feedback chi tiết
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, ["⚠️ Không nhận dạng được nội dung"]

    # ==== PHẦN 1: NẾU CÓ REFERENCE TEXT - SO SÁNH TRỰC TIẾP ====
    if reference_text and reference_text.strip():
        return check_pronunciation_with_reference(text, reference_text)

    # ==== PHẦN 2: NẾU KHÔNG CÓ REFERENCE - ĐÁNH GIÁ DỰA TRÊN CHẤT LƯỢNG ====
    # Các pattern báo hiệu phát âm KÉM (Whisper nhận dạng sai)
    error_indicators = {
        # Từ vô nghĩa / ngẫu nhiên
        "nonsense_words": [
            "hver",
            "ung",
            "hver",
            "isch",
            "artstrom",
            "justarta",
            "matery",
            "hver",
            "الت",
            "ال",
        ],
        # Pattern lặp lại bất thường
        "repetitive": ["me me", "I I", "you you", "the the the"],
        # Từ quá ngắn không rõ nghĩa
        "unclear_short": ["i", "a", "o", "u", "e"],  # Đơn lẻ, không có ngữ cảnh
    }

    # Phân tích chất lượng transcription
    issues = []
    penalty = 0.0

    # 1. Kiểm tra từ vô nghĩa
    nonsense_count = 0
    nonsense_found = []
    text_lower = text.lower()

    for nonsense in error_indicators["nonsense_words"]:
        if nonsense in text_lower:
            nonsense_count += 1
            nonsense_found.append(nonsense)

    if nonsense_count > 0:
        penalty += 0.3 * min(nonsense_count, 3)  # Max -0.9
        issues.append(f"⚠️ Phát hiện {nonsense_count} từ không rõ nghĩa")

    # 2. Kiểm tra pattern lặp lại bất thường
    repetition_count = 0
    for pattern in error_indicators["repetitive"]:
        if pattern in text_lower:
            repetition_count += 1

    if repetition_count > 0:
        penalty += 0.2 * repetition_count
        issues.append("⚠️ Phát hiện pattern lặp từ bất thường")

    # 3. Kiểm tra tỷ lệ từ quá ngắn (< 3 ký tự) - dấu hiệu nói ngắt quãng
    short_words = [w for w in words if len(re.sub(r"[^a-zA-Z]", "", w)) < 3]
    short_ratio = len(short_words) / word_count

    if short_ratio > 0.5:  # Quá 50% từ ngắn
        penalty += 0.3
        issues.append(
            f"⚠️ Quá nhiều từ ngắn ({short_ratio*100:.0f}%) - phát âm có thể không rõ"
        )

    # 4. Kiểm tra độ dài trung bình của từ (từ quá ngắn = phát âm không rõ)
    avg_word_length = sum(len(re.sub(r"[^a-zA-Z]", "", w)) for w in words) / word_count

    if avg_word_length < 3.0:
        penalty += 0.2
        issues.append(f"⚠️ Từ trung bình quá ngắn ({avg_word_length:.1f} ký tự)")

    # 5. Kiểm tra tính mạch lạc câu (có động từ, danh từ cơ bản)
    has_basic_structure = any(
        word in text_lower
        for word in ["is", "am", "are", "have", "can", "my", "i", "you", "we"]
    )

    if not has_basic_structure:
        penalty += 0.3
        issues.append("⚠️ Thiếu cấu trúc câu cơ bản")

    # 6. Kiểm tra tỷ lệ ký tự số/đặc biệt (dấu hiệu Whisper không nhận dạng được)
    special_char_count = len(re.findall(r"[^a-zA-Z0-9\s\.\,\!\?]", text))
    if special_char_count > word_count * 0.1:  # Quá 10%
        penalty += 0.2
        issues.append("⚠️ Chứa nhiều ký tự đặc biệt (dấu hiệu không nhận dạng được)")

    # Tính điểm pronunciation (2.0 - penalty)
    score = max(2.0 - penalty, 0.0)

    # Tạo feedback chi tiết
    feedback = []
    feedback.append(f"**📊 Phân tích Pronunciation:**")
    feedback.append(f"• Tổng số từ: **{word_count}** từ")
    feedback.append(f"• Độ dài từ TB: **{avg_word_length:.1f}** ký tự")
    feedback.append(f"• Tỷ lệ từ ngắn: **{short_ratio*100:.0f}%**")
    feedback.append("")

    # Hiển thị các vấn đề phát hiện được
    if issues:
        feedback.append("**🔍 Vấn đề phát hiện:**")
        for issue in issues:
            feedback.append(f"• {issue}")
        feedback.append("")

        if nonsense_found:
            feedback.append("**❌ Từ không rõ nghĩa:**")
            feedback.append(f"• {', '.join(nonsense_found[:5])}")
            feedback.append("")

    # Đánh giá tổng quan
    if score >= 1.8:
        feedback.append(
            "**✅ Phát âm xuất sắc!** Whisper nhận dạng rất tốt, giọng nói rõ ràng."
        )
    elif score >= 1.5:
        feedback.append(
            "**✅ Phát âm tốt!** Whisper nhận dạng tốt, chỉ một vài chỗ cần cải thiện."
        )
    elif score >= 1.2:
        feedback.append(
            "**📌 Phát âm khá.** Một số từ chưa rõ, cần phát âm rõ ràng hơn."
        )
    elif score >= 0.8:
        feedback.append(
            "**⚠️ Phát âm cần cải thiện.** Nhiều từ Whisper nhận dạng không chính xác."
        )
    else:
        feedback.append(
            "**❌ Phát âm kém.** Whisper gặp khó khăn nhận dạng, cần luyện tập nhiều."
        )

    # Gợi ý cải thiện
    if score < 1.5:
        feedback.append("")
        feedback.append("**💡 Cách cải thiện:**")
        feedback.append("1. **Phát âm rõ từng từ:** Nói chậm, rõ ràng")
        feedback.append("2. **Không nói ngắt quãng:** Nói trọn câu, không dừng giữa từ")
        feedback.append("3. **Luyện âm khó:** /r/, /l/, /th/, /v/, /s/")
        feedback.append(
            "4. **Ghi âm và nghe lại:** So sánh với phát âm chuẩn (Google Translate, Youglish)"
        )

    return round(score, 1), feedback


def check_pronunciation_with_reference(transcribed, reference):
    """
    So sánh transcribed text với reference text để đánh giá phát âm
    Sử dụng Word Error Rate (WER) và phân tích chi tiết
    """

    # Chuẩn hóa text
    def normalize(text):
        text = text.lower()
        text = re.sub(r"[^a-z\s]", "", text)  # Chỉ giữ chữ cái và space
        return text.split()

    ref_words = normalize(reference)
    trans_words = normalize(transcribed)

    if len(ref_words) == 0:
        return 0, ["⚠️ Câu tham chiếu không hợp lệ"]

    # Tính Word Error Rate (WER) bằng Levenshtein Distance
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    # Phân tích chi tiết từng từ
    correct_words = 0
    missing_words = []
    extra_words = []

    # So sánh từng từ (simple alignment)
    ref_set = set(ref_words)
    trans_set = set(trans_words)

    # Từ đúng: có trong cả 2
    matched_ref = []
    matched_trans = []

    for word in ref_words:
        if word in trans_set and word not in matched_ref:
            correct_words += 1
            matched_ref.append(word)
            matched_trans.append(word)

    # Từ thiếu: có trong ref nhưng không khớp
    for word in ref_words:
        if word not in matched_ref:
            missing_words.append(word)

    # Từ thừa: có trong trans nhưng không khớp (CHỈ ĐỂ HIỂN THỊ, KHÔNG TRỪ ĐIỂM)
    for word in trans_words:
        if word not in matched_trans and word not in ref_set:
            extra_words.append(word)

    # Tính accuracy CHỈ dựa trên từ ĐÚNG và THIẾU (bỏ qua từ thừa)
    # Công thức: Accuracy = (Từ đúng) / (Tổng từ gốc)
    accuracy = correct_words / len(ref_words)
    accuracy_percent = accuracy * 100

    # Tính lỗi chỉ từ missing words
    error_rate = len(missing_words) / len(ref_words)

    # Tính điểm pronunciation dựa trên accuracy
    if accuracy >= 0.95:
        score = 2.0
        grade = "Xuất sắc"
        emoji = "🟢"
    elif accuracy >= 0.90:
        score = 1.8
        grade = "Rất tốt"
        emoji = "🟢"
    elif accuracy >= 0.80:
        score = 1.5
        grade = "Khá tốt"
        emoji = "🟡"
    elif accuracy >= 0.70:
        score = 1.2
        grade = "Trung bình khá"
        emoji = "🟡"
    elif accuracy >= 0.60:
        score = 0.9
        grade = "Trung bình"
        emoji = "🟠"
    elif accuracy >= 0.50:
        score = 0.6
        grade = "Yếu"
        emoji = "🟠"
    else:
        score = 0.3
        grade = "Kém"
        emoji = "🔴"

    # Tạo feedback chi tiết
    feedback = []
    feedback.append(f"**📊 Phân tích So sánh với Câu Gốc:**")
    feedback.append(f"• **Độ chính xác: {emoji} {accuracy_percent:.1f}%** ({grade})")
    feedback.append(f"• Câu gốc: **{len(ref_words)}** từ")
    feedback.append(f"• Bạn nói: **{len(trans_words)}** từ")
    feedback.append(f"• Từ phát âm đúng: **{correct_words}/{len(ref_words)}** từ")
    feedback.append(f"• Từ thiếu/sai: **{len(missing_words)}** từ")
    if extra_words:
        feedback.append(
            f"• Từ mở rộng thêm: **{len(extra_words)}** từ *(không trừ điểm)*"
        )
    feedback.append("")

    # Hiển thị từ thiếu chi tiết
    if missing_words:
        feedback.append(f"**❌ Từ THIẾU/SAI ({len(missing_words)} từ):**")
        missing_unique = list(set(missing_words))[:15]
        feedback.append(f"• {', '.join(missing_unique)}")
        feedback.append("")

    if extra_words:
        feedback.append(f"**➕ Từ MỞ RỘNG THÊM ({len(extra_words)} từ):**")
        extra_unique = list(set(extra_words))[:15]
        feedback.append(f"• {', '.join(extra_unique)}")
        feedback.append(f"• *(Không bị trừ điểm - Khuyến khích mở rộng ý!)*")
        feedback.append("")

    # Đánh giá tổng quan
    if accuracy >= 0.90:
        feedback.append(
            "**✅ Xuất sắc!** Phát âm rất chuẩn, phần lớn từ trong câu gốc đều đúng."
        )
    elif accuracy >= 0.80:
        feedback.append(
            "**✅ Rất tốt!** Phần lớn từ phát âm chuẩn, chỉ thiếu/sai một vài từ."
        )
    elif accuracy >= 0.70:
        feedback.append("**📌 Khá tốt.** Một số từ trong câu gốc cần cải thiện.")
    elif accuracy >= 0.60:
        feedback.append("**⚠️ Trung bình.** Nhiều từ trong câu gốc bị thiếu/sai.")
    else:
        feedback.append(
            "**❌ Cần cải thiện.** Phần lớn từ trong câu gốc chưa phát âm đúng."
        )

    # Gợi ý cải thiện
    if accuracy < 0.85:
        feedback.append("")
        feedback.append("**💡 Gợi ý cải thiện:**")
        feedback.append("1. **Tập trung vào từ THIẾU/SAI** ở trên")
        feedback.append("2. **Đọc chậm từng từ** trong câu gốc")
        feedback.append("3. **Nghe và nhắc lại** nhiều lần")
        feedback.append("4. **So sánh ghi âm** của bạn với phát âm chuẩn")

    if extra_words and accuracy >= 0.75:
        feedback.append("")
        feedback.append("**🌟 Điểm cộng:**")
        feedback.append("• Bạn đã mở rộng ý rất tốt! Tiếp tục phát triển kỹ năng này!")

    return round(score, 1), feedback


def check_communication(text):
    """
    Đánh giá khả năng truyền đạt ý (có trả lời đúng câu hỏi, logic, rõ ràng)
    Trả về điểm từ 0-2
    """
    words = text.lower().split()
    word_count = len(words)

    score = 1.0  # Điểm cơ bản
    issues = []

    # Kiểm tra độ dài (có đủ nội dung không)
    if word_count >= 30:
        score += 0.5
    elif word_count < 15:
        score -= 0.3
        issues.append("Câu trả lời quá ngắn, thiếu chi tiết")

    # Kiểm tra có từ nối (because, and, so, but) - thể hiện logic
    connectors = ["because", "and", "so", "but", "also", "however", "therefore"]
    has_connector = any(conn in words for conn in connectors)
    if has_connector:
        score += 0.3
    else:
        issues.append("Nên dùng từ nối để liên kết ý")

    # Kiểm tra có câu giới thiệu (my name, i am, i like, my favorite)
    intro_phrases = ["my name", "i am", "my favorite", "i like", "i love"]
    has_intro = any(phrase in text.lower() for phrase in intro_phrases)
    if has_intro:
        score += 0.2

    return max(min(score, 2.0), 0), issues


def analyze_speech(transcribed_text, audio_path=None, reference_text=None):
    """
    Phân tích bài nói theo 5 tiêu chí (mỗi tiêu chí /2 điểm, tổng /10)
    """
    if not transcribed_text or len(transcribed_text.strip()) == 0:
        return 0, ["⚠️ Không nhận dạng được nội dung. Vui lòng thử lại."], {}

    # Chấm từng tiêu chí
    pronunciation_score, pronunciation_issues = check_pronunciation(
        transcribed_text, reference_text
    )
    fluency_score, fluency_issues = check_fluency(transcribed_text)
    grammar_score, grammar_issues = check_grammar_basic(transcribed_text)
    vocabulary_score, vocabulary_issues = check_vocabulary(transcribed_text)
    communication_score, communication_issues = check_communication(transcribed_text)

    # Tổng điểm /10
    total_score = (
        pronunciation_score
        + fluency_score
        + grammar_score
        + vocabulary_score
        + communication_score
    )

    # Chuyển sang thang điểm 100
    final_score_100 = (total_score / 10) * 100

    # Tạo breakdown chi tiết
    breakdown = {
        "Pronunciation": pronunciation_score,
        "Fluency": fluency_score,
        "Grammar": grammar_score,
        "Vocabulary": vocabulary_score,
        "Communication": communication_score,
        "Total": total_score,
    }

    # Tạo feedback chi tiết
    feedback = []

    feedback.append(
        f"📊 **TỔNG ĐIỂM: {total_score:.1f}/10** ({final_score_100:.0f}/100)"
    )
    feedback.append("---")

    # 1. Pronunciation
    feedback.append(f"🗣️ **1. Pronunciation (Phát âm): {pronunciation_score:.1f}/2**")
    feedback.append("")
    if pronunciation_issues:
        for issue in pronunciation_issues:
            feedback.append(f"{issue}")
    feedback.append("")

    # 2. Fluency
    feedback.append(f"🎵 **2. Fluency (Độ trôi chảy): {fluency_score:.1f}/2**")
    if fluency_issues:
        for issue in fluency_issues:
            feedback.append(f"   • {issue}")
    else:
        feedback.append("   • Nói khá tự nhiên và mạch lạc")
    feedback.append("")

    # 3. Grammar
    feedback.append(f"📝 **3. Grammar (Ngữ pháp): {grammar_score:.1f}/2**")
    if grammar_issues:
        for issue in grammar_issues:
            feedback.append(f"   • {issue}")
    else:
        feedback.append("   • Ngữ pháp chính xác")
    feedback.append("")

    # 4. Vocabulary
    feedback.append(f"📚 **4. Vocabulary (Từ vựng): {vocabulary_score:.1f}/2**")
    if vocabulary_issues:
        for issue in vocabulary_issues:
            feedback.append(f"   • {issue}")
    else:
        feedback.append("   • Từ vựng đa dạng và phù hợp")
    feedback.append("")

    # 5. Communication
    feedback.append(f"💬 **5. Communication (Giao tiếp): {communication_score:.1f}/2**")
    if communication_issues:
        for issue in communication_issues:
            feedback.append(f"   • {issue}")
    else:
        feedback.append("   • Truyền đạt ý rõ ràng và logic")

    return round(final_score_100, 1), feedback, breakdown


def save_result_to_history(topic, transcribed, score, wrong_words, breakdown=None):
    """Lưu kết quả vào lịch sử"""
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "reference": topic,
        "transcribed": transcribed,
        "score": score,
        "wrong_words": wrong_words,
        "word_count": len(transcribed.split()),
        "user": st.session_state.user_name,
        "mode": "Bài nói tự do",
        "breakdown": breakdown if breakdown else {},
    }
    st.session_state.history.append(result)


def export_history_to_csv():
    """Xuất lịch sử ra CSV"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode("utf-8")


def export_history_to_json():
    """Xuất lịch sử ra JSON (để backup)"""
    if not st.session_state.history:
        return None

    data = {
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": st.session_state.user_name,
        "history": st.session_state.history,
    }
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def import_history_from_json(json_file):
    """Nhập lịch sử từ JSON"""
    try:
        data = json.loads(json_file.read())
        st.session_state.history = data.get("history", [])
        return True
    except Exception as e:
        st.error(f"Lỗi import: {e}")
        return False


def get_statistics():
    """Tính toán thống kê"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)

    stats = {
        "total_attempts": len(df),
        "avg_score": df["score"].mean(),
        "max_score": df["score"].max(),
        "min_score": df["score"].min(),
        "today_attempts": len(df[df["date"] == datetime.now().strftime("%Y-%m-%d")]),
        "excellent_count": len(df[df["score"] >= 90]),
        "good_count": len(df[(df["score"] >= 75) & (df["score"] < 90)]),
        "average_count": len(df[(df["score"] >= 60) & (df["score"] < 75)]),
        "poor_count": len(df[df["score"] < 60]),
    }

    return stats


def calculate_streak():
    """Tính chuỗi ngày luyện tập liên tục"""
    if not st.session_state.history:
        return 0

    df = pd.DataFrame(st.session_state.history)
    unique_dates = sorted(df["date"].unique(), reverse=True)

    if not unique_dates:
        return 0

    today = datetime.now().strftime("%Y-%m-%d")

    if unique_dates[0] != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if unique_dates[0] != yesterday:
            return 0

    streak = 1
    for i in range(len(unique_dates) - 1):
        current = datetime.strptime(unique_dates[i], "%Y-%m-%d")
        next_date = datetime.strptime(unique_dates[i + 1], "%Y-%m-%d")

        if (current - next_date).days == 1:
            streak += 1
        else:
            break

    return streak


def create_progress_chart():
    """Tạo biểu đồ tiến độ"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)
    df["attempt_number"] = range(1, len(df) + 1)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["attempt_number"],
            y=df["score"],
            mode="lines+markers",
            name="Điểm số",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        )
    )

    fig.add_hline(
        y=90, line_dash="dash", line_color="green", annotation_text="Xuất sắc (90)"
    )
    fig.add_hline(
        y=75, line_dash="dash", line_color="orange", annotation_text="Khá (75)"
    )
    fig.add_hline(
        y=60, line_dash="dash", line_color="red", annotation_text="Trung bình (60)"
    )

    fig.update_layout(
        title="📈 Biểu đồ tiến độ học tập",
        xaxis_title="Lần chấm",
        yaxis_title="Điểm số",
        yaxis_range=[0, 105],
        hovermode="x unified",
    )

    return fig


def create_score_distribution():
    """Tạo biểu đồ phân bố điểm"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(x=df["score"], nbinsx=20, marker_color="#1f77b4", opacity=0.7)
    )

    fig.update_layout(
        title="📊 Phân bố điểm số",
        xaxis_title="Điểm số",
        yaxis_title="Số lần",
        bargap=0.1,
    )

    return fig


def create_weekly_chart():
    """Biểu đồ theo tuần"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)
    df["date"] = pd.to_datetime(df["date"])

    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    date_range = pd.date_range(start=start_date, end=end_date)
    daily_stats = []

    for date in date_range:
        date_str = date.strftime("%Y-%m-%d")
        day_data = df[df["date"] == date_str]

        if len(day_data) > 0:
            daily_stats.append(
                {
                    "date": date.strftime("%d/%m"),
                    "count": len(day_data),
                    "avg_score": day_data["score"].mean(),
                }
            )
        else:
            daily_stats.append(
                {"date": date.strftime("%d/%m"), "count": 0, "avg_score": 0}
            )

    stats_df = pd.DataFrame(daily_stats)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=stats_df["date"],
            y=stats_df["count"],
            name="Số lần luyện",
            marker_color="#1f77b4",
        )
    )

    fig.update_layout(
        title="📅 Hoạt động 7 ngày gần nhất",
        xaxis_title="Ngày",
        yaxis_title="Số lần luyện tập",
    )

    return fig


# ========== GIAO DIỆN CHÍNH ==========

# Header với tabs
tab1, tab2, tab3 = st.tabs(["🎤 Phân tích Bài nói", "📊 Thống kê", "⚙️ Cài đặt"])

# TAB 1: PHÂN TÍCH BÀI NÓI
with tab1:
    st.title("🎤 PHÂN TÍCH PHÁT ÂM BÀI NÓI TỰ DO")

    # Thông tin người dùng và streak
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)

    with col_info1:
        st.markdown(f"**👤 Học viên:** {st.session_state.user_name}")

    with col_info2:
        streak = calculate_streak()
        if streak > 0:
            st.markdown(f"**🔥 Streak:** {streak} ngày")

    with col_info3:
        stats = get_statistics()
        if stats:
            st.markdown(
                f"**📈 Hôm nay:** {stats['today_attempts']}/{st.session_state.daily_goal} lần"
            )
            progress = min(stats["today_attempts"] / st.session_state.daily_goal, 1.0)
            st.progress(progress)

    with col_info4:
        if stats:
            st.markdown(f"**⭐ Điểm TB:** {stats['avg_score']:.1f}/100")

    st.divider()

    # Phần nhập chủ đề
    st.subheader("📝 Bước 1: Nhập chủ đề/đề bài")

    # THÊM COLUMNS
    col_topic1, col_topic2 = st.columns([2, 1])

    with col_topic1:
        topic_input = st.text_input(
            "Chủ đề bài nói của bạn:",
            value="",
            placeholder="Ví dụ: My favorite hobby, My hometown, A memorable trip...",
            help="Nhập chủ đề mà bạn sẽ nói về",
        )

    with col_topic2:
        use_reference = st.checkbox(
            "📋 Có câu mẫu?", help="Bật nếu bạn có câu gốc cần đọc theo", value=False
        )

    # THÊM PHẦN REFERENCE TEXT
    reference_text = None
    if use_reference:
        reference_text = st.text_area(
            "📝 Nhập câu gốc (reference):",
            value="",
            placeholder="Ví dụ: Hello everyone, my name is Ivy. I'm a student...",
            help="Nhập câu gốc mà bạn cần đọc theo",
            height=100,
        )
        if reference_text:
            st.info(f"📌 Câu gốc: **{reference_text[:100]}...**")
    elif topic_input:
        st.info(f"📌 Chủ đề: **{topic_input}**")

    st.divider()

    # Phần ghi âm và upload
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ Bước 2a: Ghi âm trực tiếp")
        audio_recording = st.audio_input("Nhấn để ghi âm:")

    with col2:
        st.subheader("📤 Bước 2b: Hoặc upload file audio")
        uploaded_file = st.file_uploader(
            "Chọn file audio:",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Hỗ trợ các định dạng: WAV, MP3, M4A, OGG, FLAC",
        )

    st.divider()

    # Nút phân tích
    st.subheader("🎯 Bước 3: Phân tích bài nói")

    if st.button("🔍 Phân tích phát âm", type="primary", use_container_width=True):

        if not topic_input:
            st.warning("⚠️ Vui lòng nhập chủ đề bài nói!")
        elif not audio_recording and not uploaded_file:
            st.error("⚠️ Vui lòng ghi âm hoặc upload file audio!")
        elif not st.session_state.model:
            st.error("⚠️ Model chưa được load. Vui lòng load trong tab Cài đặt.")
        else:
            with st.spinner("🔄 Đang xử lý âm thanh..."):
                try:
                    audio_source = uploaded_file if uploaded_file else audio_recording
                    wav_path = convert_audio_to_wav(audio_source)

                    if wav_path:
                        with st.spinner("🎧 Đang nhận dạng giọng nói..."):
                            transcribed_text = transcribe_audio(
                                wav_path, st.session_state.model
                            )

                        try:
                            os.unlink(wav_path)
                        except:
                            pass

                        if transcribed_text:
                            score, feedback, breakdown = analyze_speech(
                                transcribed_text, wav_path, reference_text
                            )
                            save_result_to_history(
                                topic_input,
                                transcribed_text,
                                score,
                                feedback,
                                breakdown,
                            )

                            st.success("✅ Phân tích hoàn tất!")
                            st.balloons()

                            st.divider()

                            # Kết quả
                            col_result1, col_result2 = st.columns(2)

                            with col_result1:
                                st.markdown("**📌 Chủ đề:**")
                                st.info(topic_input)

                            with col_result2:
                                st.markdown("**🗣️ Nội dung bạn đã nói:**")
                                st.info(transcribed_text)

                            # Điểm số tổng quan
                            st.markdown("### 🎯 Kết quả chấm điểm")

                            # Hiển thị điểm chi tiết theo 5 tiêu chí
                            col_breakdown = st.columns(6)

                            criteria_emojis = ["🗣️", "🎵", "📝", "📚", "💬", "⭐"]
                            criteria_names = [
                                "Pronunciation",
                                "Fluency",
                                "Grammar",
                                "Vocabulary",
                                "Communication",
                                "Total",
                            ]

                            for i, (emoji, name) in enumerate(
                                zip(criteria_emojis, criteria_names)
                            ):
                                with col_breakdown[i]:
                                    if name == "Total":
                                        st.metric(
                                            f"{emoji} {name}",
                                            f"{breakdown.get('Total', 0):.1f}/10",
                                            help="Tổng điểm",
                                        )
                                    else:
                                        st.metric(
                                            f"{emoji} {name[:4]}.",
                                            f"{breakdown.get(name, 0):.1f}/2",
                                            help=name,
                                        )

                            st.divider()

                            # Điểm số lớn với màu sắc (chuyển sang thang 100 để hiển thị)
                            if score >= 90:
                                score_class = "score-excellent"
                                grade = "Xuất sắc"
                                emoji = "🟢"
                            elif score >= 75:
                                score_class = "score-good"
                                grade = "Khá"
                                emoji = "🟡"
                            elif score >= 60:
                                score_class = "score-average"
                                grade = "Trung bình"
                                emoji = "🟠"
                            else:
                                score_class = "score-poor"
                                grade = "Cần cải thiện"
                                emoji = "🔴"

                            col_score1, col_score2 = st.columns([1, 2])

                            with col_score1:
                                st.markdown(
                                    f'<div class="{score_class}">{emoji} {score:.0f}/100</div>',
                                    unsafe_allow_html=True,
                                )

                            with col_score2:
                                st.markdown(f"### {grade}")
                                st.progress(score / 100)

                                if score >= 90:
                                    st.success(
                                        "🎉 Xuất sắc! Phát âm và nội dung rất tốt!"
                                    )
                                elif score >= 75:
                                    st.info(
                                        "👍 Tốt lắm! Tiếp tục luyện tập để hoàn thiện hơn."
                                    )
                                elif score >= 60:
                                    st.warning(
                                        "💪 Khá ổn! Hãy chú ý các góp ý phía dưới."
                                    )
                                else:
                                    st.error(
                                        "📚 Cần cải thiện. Hãy luyện tập thêm về phát âm và độ dài bài nói."
                                    )

                            # Feedback chi tiết
                            st.markdown("### 💡 Phản hồi chi tiết")

                            # Hiển thị feedback dạng markdown
                            feedback_text = "\n".join(feedback)
                            st.markdown(feedback_text)

                            # Gợi ý luyện tập
                            with st.expander("📖 Gợi ý cải thiện cho từng tiêu chí"):
                                st.markdown(
                                    """
                                **🗣️ Pronunciation (Phát âm):**
                                - Nghe và bắt chước người bản ngữ (BBC Learning English, VOA)
                                - Tập phát âm các âm khó: /θ/, /ð/, /r/, /l/
                                - Ghi âm và so sánh với bản gốc
                                
                                **🎵 Fluency (Độ trôi chảy):**
                                - Luyện nói không ngắt quãng 1-2 phút
                                - Giảm "uh", "um" bằng cách suy nghĩ trước khi nói
                                - Đọc to 10-15 phút mỗi ngày
                                
                                **📝 Grammar (Ngữ pháp):**
                                - Học thuộc các thì cơ bản (hiện tại, quá khứ, tương lai)
                                - Chú ý Subject-Verb Agreement (I am, He is, They are)
                                - Làm bài tập ngữ pháp trên app (Duolingo, Grammarly)
                                
                                **📚 Vocabulary (Từ vựng):**
                                - Học 10 từ mới mỗi ngày theo chủ đề
                                - Sử dụng từ vựng đa dạng, tránh lặp lại
                                - Đọc sách/báo tiếng Anh để mở rộng vốn từ
                                
                                **💬 Communication (Giao tiếp):**
                                - Trả lời đầy đủ câu hỏi với lý do và ví dụ
                                - Sử dụng từ nối: because, and, so, but
                                - Tổ chức ý: Introduction → Main idea → Example → Conclusion
                                """
                                )

                        else:
                            st.error(
                                "❌ Không thể nhận dạng giọng nói. Vui lòng thử lại."
                            )
                    else:
                        st.error("❌ Không thể xử lý file audio.")

                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

    # Hiển thị lịch sử gần đây
    if st.session_state.history:
        st.divider()
        st.subheader("📜 Lịch sử gần đây (5 lần cuối)")

        for item in reversed(st.session_state.history[-5:]):
            with st.expander(f"⏰ {item['timestamp']} - Điểm: {item['score']}/100"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"**📌 Chủ đề:** {item['reference']}")
                    st.write(f"**🗣️ Nội dung:** {item['transcribed'][:100]}...")
                with col_h2:
                    st.metric("Điểm số", f"{item['score']}/100")
                    st.write(f"**👤 Người dùng:** {item['user']}")
                    st.write(f"**📝 Số từ:** {item['word_count']}")

                # Hiển thị breakdown nếu có
                if "breakdown" in item and item["breakdown"]:
                    st.write("**📊 Chi tiết điểm:**")
                    breakdown = item["breakdown"]
                    col_b = st.columns(5)
                    labels = [
                        "Pronunciation",
                        "Fluency",
                        "Grammar",
                        "Vocabulary",
                        "Communication",
                    ]
                    for idx, label in enumerate(labels):
                        if label in breakdown:
                            with col_b[idx]:
                                st.metric(label[:6], f"{breakdown[label]:.1f}/2")

# TAB 2: THỐNG KÊ
with tab2:
    st.title("📊 Thống kê và Phân tích")

    stats = get_statistics()

    if stats and stats["total_attempts"] > 0:
        # Hiển thị Streak
        streak = calculate_streak()
        if streak > 0:
            st.markdown(
                f"""
            <div class="streak-badge">
                🔥 Streak: {streak} ngày liên tục!
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown("")

        # Tổng quan
        st.subheader("📈 Tổng quan")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Tổng số lần phân tích", stats["total_attempts"])

        with col2:
            st.metric("Điểm trung bình", f"{stats['avg_score']:.1f}/100")

        with col3:
            st.metric("Điểm cao nhất", f"{stats['max_score']}/100")

        with col4:
            st.metric("Hôm nay", f"{stats['today_attempts']} lần")

        st.divider()

        # Biểu đồ
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            progress_chart = create_progress_chart()
            if progress_chart:
                st.plotly_chart(progress_chart, use_container_width=True)

        with col_chart2:
            dist_chart = create_score_distribution()
            if dist_chart:
                st.plotly_chart(dist_chart, use_container_width=True)

        st.divider()

        # Biểu đồ hoạt động 7 ngày
        weekly_chart = create_weekly_chart()
        if weekly_chart:
            st.plotly_chart(weekly_chart, use_container_width=True)

        st.divider()

        # Phân loại điểm
        st.subheader("🎯 Phân loại kết quả")

        col_cat1, col_cat2, col_cat3, col_cat4 = st.columns(4)

        with col_cat1:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #00c853;">
                <h3>🟢 Xuất sắc</h3>
                <h2>{stats['excellent_count']}</h2>
                <p>≥ 90 điểm</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat2:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ffd600;">
                <h3>🟡 Khá</h3>
                <h2>{stats['good_count']}</h2>
                <p>75-89 điểm</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat3:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ff9800;">
                <h3>🟠 Trung bình</h3>
                <h2>{stats['average_count']}</h2>
                <p>60-74 điểm</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat4:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ff5252;">
                <h3>🔴 Cần cải thiện</h3>
                <h2>{stats['poor_count']}</h2>
                <p>< 60 điểm</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Xuất báo cáo
        st.subheader("📥 Xuất dữ liệu")

        col_export1, col_export2, col_export3 = st.columns(3)

        with col_export1:
            csv_data = export_history_to_csv()
            if csv_data:
                st.download_button(
                    label="💾 Tải CSV",
                    data=csv_data,
                    file_name=f"speech_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with col_export2:
            json_data = export_history_to_json()
            if json_data:
                st.download_button(
                    label="💾 Tải JSON (Backup)",
                    data=json_data,
                    file_name=f"speech_analysis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

        with col_export3:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                if st.session_state.get("confirm_delete", False):
                    st.session_state.history = []
                    st.session_state.confirm_delete = False
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    st.warning("⚠️ Nhấn lần nữa để xác nhận!")

    else:
        st.info("📊 Chưa có dữ liệu thống kê. Hãy bắt đầu phân tích bài nói đầu tiên!")

# TAB 3: CÀI ĐẶT
with tab3:
    st.title("⚙️ Cài đặt")

    # Thông tin người dùng
    st.subheader("👤 Thông tin người dùng")
    user_name = st.text_input("Tên của bạn:", value=st.session_state.user_name)

    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        st.success("✅ Đã lưu tên!")

    st.divider()

    # Cài đặt mục tiêu
    st.subheader("🎯 Mục tiêu luyện tập")
    daily_goal = st.slider(
        "Số lần phân tích mỗi ngày:",
        min_value=1,
        max_value=50,
        value=st.session_state.daily_goal,
        help="Đặt mục tiêu số lần phân tích bài nói hàng ngày",
    )

    if daily_goal != st.session_state.daily_goal:
        st.session_state.daily_goal = daily_goal
        st.success(f"✅ Đã đặt mục tiêu: {daily_goal} lần/ngày")

    st.divider()

    # Cài đặt Model Whisper
    st.subheader("🤖 Mô hình AI")

    col_model1, col_model2 = st.columns(2)

    with col_model1:
        model_size = st.selectbox(
            "Chọn mô hình Whisper:",
            options=["tiny", "base", "small"],
            index=["tiny", "base", "small"].index(st.session_state.model_size),
            help="""
            - tiny: Nhanh nhất, độ chính xác thấp nhất (39MB)
            - base: Cân bằng tốc độ và độ chính xác (74MB) - Khuyến nghị
            - small: Chậm hơn nhưng chính xác hơn (244MB)
            """,
        )

    with col_model2:
        if st.session_state.model is not None:
            st.success(f"Model đang dùng: **{st.session_state.model_size}**")
        else:
            st.warning("Chưa load model")

    if st.button("Load/Reload Model", type="primary", use_container_width=True):
        with st.spinner(f"Đang tải model {model_size}..."):
            model = load_whisper_model(model_size)
            if model:
                st.session_state.model = model
                st.session_state.model_size = model_size
                st.success(f"✅ Đã load model {model_size} thành công!")
                st.balloons()
            else:
                st.error("❌ Không thể load model. Vui lòng thử lại.")

    st.divider()

    # Import/Export dữ liệu
    st.subheader("💾 Sao lưu & Khôi phục")

    col_backup1, col_backup2 = st.columns(2)

    with col_backup1:
        st.markdown("**Xuất dữ liệu (Backup)**")
        json_backup = export_history_to_json()
        if json_backup:
            st.download_button(
                label="📥 Tải file backup (JSON)",
                data=json_backup,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("Chưa có dữ liệu để backup")

    with col_backup2:
        st.markdown("**Nhập dữ liệu (Restore)**")
        upload_backup = st.file_uploader(
            "Chọn file backup JSON:",
            type=["json"],
            help="Upload file JSON đã backup trước đó",
        )

        if upload_backup:
            if st.button("📤 Khôi phục dữ liệu", use_container_width=True):
                if import_history_from_json(upload_backup):
                    st.success("✅ Đã khôi phục dữ liệu thành công!")
                    st.rerun()
                else:
                    st.error("❌ Không thể khôi phục. File không hợp lệ.")

    st.divider()

    # Thông tin ứng dụng
    st.subheader("ℹ️ Thông tin ứng dụng")

    st.info(
        """
    **🎤 Ứng dụng Phân tích Phát Âm Bài Nói Tự Do**
    
    **Phiên bản:** 3.1 - Enhanced Pronunciation Feedback
    
    **Tính năng chính:**
    - Phân tích phát âm tự động với AI (Whisper)
    - Chấm điểm theo 5 tiêu chí với phản hồi chi tiết
    - Phát hiện từ phát âm sai và đưa ra gợi ý sửa
    - Thống kê chi tiết và biểu đồ trực quan
    - Theo dõi streak và mục tiêu hàng ngày
    - Sao lưu/khôi phục dữ liệu
    
    **Công nghệ:**
    - Streamlit
    - OpenAI Whisper (ASR)
    - Plotly Charts
    - Advanced NLP Analysis
    
    **Thang điểm:**
    - Pronunciation: Độ rõ ràng, chính xác phát âm (/2)
    - Fluency: Độ trôi chảy, tự nhiên (/2)
    - Grammar: Ngữ pháp chính xác (/2)
    - Vocabulary: Từ vựng đa dạng (/2)
    - Communication: Truyền đạt ý rõ ràng (/2)
    - Tổng: /10 điểm (tương đương /100)
    """
    )

    st.divider()

    # Nút reset toàn bộ
    st.subheader("🚨 Zone Nguy hiểm")

    if st.button("🗑️ Xóa toàn bộ dữ liệu và cài đặt", type="secondary"):
        if st.session_state.get("confirm_reset_all", False):
            st.session_state.history = []
            st.session_state.user_name = "Học viên"
            st.session_state.daily_goal = 10
            st.session_state.confirm_reset_all = False
            st.success("✅ Đã reset toàn bộ!")
            st.rerun()
        else:
            st.session_state.confirm_reset_all = True
            st.error(
                "⚠️ CẢNH BÁO: Bạn sẽ mất toàn bộ dữ liệu! Nhấn lần nữa để xác nhận."
            )

# Footer
st.divider()
st.markdown(
    """
<style>
.footer-link {
    color: gray;
    text-decoration: none;
    transition: color 0.3s ease;
}
.footer-link:hover {
    color: #1f77b4;
}
</style>

<div style='text-align: center; color: gray; padding: 16px 0; font-size: 14px;'>
    <p><strong>Ứng dụng Phân tích Phát Âm Bài Nói Tự Do</strong></p>
    <p>Miễn phí • Offline/Online • Không dùng API trả phí</p>
    <p>Sử dụng: Whisper (OpenAI) + Streamlit + Enhanced Pronunciation Analysis</p>
    <p style='margin-top:10px;'>© 2025 
        <a href='https://www.facebook.com/augusttrung1823/' target='_blank' class='footer-link'>
            August Trung
        </a>. All rights reserved.
    </p>
</div>
""",
    unsafe_allow_html=True,
)
