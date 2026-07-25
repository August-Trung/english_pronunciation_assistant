import streamlit as st
import whisper
from fuzzywuzzy import fuzz
from pydub import AudioSegment
import numpy as np
import tempfile
import os
from datetime import datetime, timedelta
import io
import difflib
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import json

# Cấu hình trang
st.set_page_config(
    page_title="Chấm Phát Âm Tiếng Anh",
    page_icon="assets/logo-augusttrung.png",
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

if "practice_mode" not in st.session_state:
    st.session_state.practice_mode = "Tự do"

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 10

if "favorite_sentences" not in st.session_state:
    st.session_state.favorite_sentences = []

if "model_size" not in st.session_state:
    st.session_state.model_size = "base"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "sentence_notes" not in st.session_state:
    st.session_state.sentence_notes = {}

# Thư viện câu mẫu theo chủ đề
SENTENCE_LIBRARY = {
    "📚 Cơ bản - Beginner": [
        "Hello, my name is John",
        "I like apples",
        "This is a book",
        "Good morning teacher",
        "How are you today",
        "Thank you very much",
        "I am a student",
        "The weather is nice",
    ],
    "🎓 Trung cấp - Intermediate": [
        "I want to eat an apple",
        "She is reading a book in the library",
        "The weather is nice today",
        "Can you help me with this problem",
        "I am studying English every day",
        "My favorite color is blue",
        "I enjoy listening to music",
        "We will go to the park tomorrow",
    ],
    "🚀 Nâng cao - Advanced": [
        "I would like to introduce myself to everyone here",
        "The quick brown fox jumps over the lazy dog",
        "She sells seashells by the seashore",
        "Peter Piper picked a peck of pickled peppers",
        "How much wood would a woodchuck chuck",
        "The sixth sick sheikh's sixth sheep's sick",
        "I saw Susie sitting in a shoeshine shop",
        "Unique New York, unique New York, you know you need unique New York",
    ],
    "💼 Giao tiếp - Communication": [
        "Excuse me, where is the nearest bus stop",
        "Could you please speak more slowly",
        "I would like to book a table for two",
        "What time does the meeting start",
        "I need to cancel my appointment",
        "Can I have the menu please",
        "How much does this cost",
        "I'm looking for the train station",
    ],
    "📖 IELTS Speaking": [
        "I believe that education is the key to success",
        "In my opinion, technology has changed our lives",
        "There are several reasons why I prefer living in the city",
        "I would like to talk about my hometown",
        "One of the most important things in life is health",
        "I think that learning a foreign language is essential",
    ],
}


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


def compare_texts(reference, transcribed):
    """So sánh câu mẫu với câu nhận dạng được"""
    ref_clean = reference.lower().strip()
    trans_clean = transcribed.lower().strip()

    similarity = fuzz.ratio(ref_clean, trans_clean)

    ref_words = ref_clean.split()
    trans_words = trans_clean.split()

    matcher = difflib.SequenceMatcher(None, ref_words, trans_words)
    wrong_words = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            for word in ref_words[i1:i2]:
                wrong_words.append(f"❌ Thiếu: '{word}'")
        elif tag == "insert":
            for word in trans_words[j1:j2]:
                wrong_words.append(f"➕ Thừa: '{word}'")
        elif tag == "replace":
            for ref_w, trans_w in zip(ref_words[i1:i2], trans_words[j1:j2]):
                wrong_words.append(f"🔄 '{ref_w}' → '{trans_w}'")

    return similarity, wrong_words


def save_result_to_history(reference, transcribed, score, wrong_words):
    """Lưu kết quả vào lịch sử"""
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "reference": reference,
        "transcribed": transcribed,
        "score": score,
        "wrong_words": wrong_words,
        "word_count": len(reference.split()),
        "user": st.session_state.user_name,
        "mode": st.session_state.practice_mode,
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
        "favorites": st.session_state.favorite_sentences,
        "notes": st.session_state.sentence_notes,
    }
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def import_history_from_json(json_file):
    """Nhập lịch sử từ JSON"""
    try:
        data = json.loads(json_file.read())
        st.session_state.history = data.get("history", [])
        st.session_state.favorite_sentences = data.get("favorites", [])
        st.session_state.sentence_notes = data.get("notes", {})
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

    # Kiểm tra có luyện hôm nay không
    if unique_dates[0] != today:
        # Kiểm tra có luyện hôm qua không
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


def get_weak_words():
    """Phân tích từ thường bị sai"""
    if not st.session_state.history:
        return []

    all_wrong_words = []
    for item in st.session_state.history:
        for error in item.get("wrong_words", []):
            if "→" in error:
                word = error.split("'")[1]
                all_wrong_words.append(word)
            elif "Thiếu" in error:
                word = error.split("'")[1]
                all_wrong_words.append(word)

    word_counts = Counter(all_wrong_words)
    return word_counts.most_common(10)


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

    # Lấy 7 ngày gần nhất
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
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎯 Luyện tập", "📊 Thống kê", "📚 Thư viện câu", "⚙️ Cài đặt"]
)

# TAB 1: LUYỆN TẬP
with tab1:
    st.title("🎯 ỨNG DỤNG CHẤM PHÁT ÂM TIẾNG ANH")

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

    # Chọn chế độ luyện tập
    practice_mode = st.radio(
        "🎮 Chế độ luyện tập:",
        ["Tự do", "Theo chủ đề", "Yêu thích"],
        horizontal=True,
        key="practice_mode_radio",
    )
    st.session_state.practice_mode = practice_mode

    # Phần nhập câu mẫu
    st.subheader("📝 Bước 1: Chọn hoặc nhập câu mẫu")

    if practice_mode == "Theo chủ đề":
        col_cat, col_sent = st.columns([1, 2])
        with col_cat:
            category = st.selectbox("Chọn chủ đề:", list(SENTENCE_LIBRARY.keys()))
        with col_sent:
            reference_text = st.selectbox("Chọn câu:", SENTENCE_LIBRARY[category])
    elif practice_mode == "Yêu thích":
        if st.session_state.favorite_sentences:
            reference_text = st.selectbox(
                "Chọn từ danh sách yêu thích:", st.session_state.favorite_sentences
            )
        else:
            st.info(
                "💡 Chưa có câu yêu thích. Thêm câu yêu thích trong tab 'Thư viện câu'!"
            )
            reference_text = st.text_input(
                "Hoặc nhập câu mới:",
                value="I want to eat an apple",
                placeholder="Nhập câu tiếng Anh...",
            )
    else:
        reference_text = st.text_input(
            "Câu mẫu:",
            value="I want to eat an apple",
            placeholder="Nhập câu tiếng Anh cần luyện phát âm...",
        )

    # Hiển thị thông tin câu và ghi chú
    if reference_text:
        col_info_a, col_info_b = st.columns(2)
        with col_info_a:
            st.caption(f"📏 Độ dài: {len(reference_text.split())} từ")
        with col_info_b:
            st.caption(f"🔤 Ký tự: {len(reference_text)} ký tự")

        # Hiển thị ghi chú nếu có
        if reference_text in st.session_state.sentence_notes:
            st.info(f"📝 Ghi chú: {st.session_state.sentence_notes[reference_text]}")

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

    # Nút chấm điểm
    st.subheader("🎯 Bước 3: Chấm điểm")

    if st.button("🔍 Chấm điểm phát âm", type="primary", use_container_width=True):

        if not reference_text:
            st.error("⚠️ Vui lòng nhập câu mẫu!")
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
                            score, wrong_words = compare_texts(
                                reference_text, transcribed_text
                            )
                            save_result_to_history(
                                reference_text, transcribed_text, score, wrong_words
                            )

                            st.success("✅ Chấm điểm hoàn tất!")
                            st.balloons()

                            st.divider()

                            # Kết quả với animation
                            col_result1, col_result2 = st.columns(2)

                            with col_result1:
                                st.markdown("**📝 Câu mẫu:**")
                                st.info(reference_text)

                            with col_result2:
                                st.markdown("**🗣️ Bạn đã nói:**")
                                st.info(transcribed_text)

                            # Điểm số lớn với màu sắc
                            st.markdown("### 🎯 Điểm số")

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
                                    f'<div class="{score_class}">{emoji} {score}</div>',
                                    unsafe_allow_html=True,
                                )

                            with col_score2:
                                st.markdown(f"### {grade}")
                                st.progress(score / 100)

                                # Lời khuyên
                                if score >= 90:
                                    st.success("🎉 Xuất sắc! Phát âm của bạn rất tốt!")
                                elif score >= 75:
                                    st.info(
                                        "👍 Tốt lắm! Tiếp tục luyện tập để hoàn thiện hơn."
                                    )
                                elif score >= 60:
                                    st.warning(
                                        "💪 Khá ổn! Hãy chú ý các từ bị sai phía dưới."
                                    )
                                else:
                                    st.error(
                                        "📚 Cần cải thiện. Hãy nghe và bắt chước kỹ hơn."
                                    )

                            # Từ sai
                            if wrong_words:
                                st.markdown("### ⚠️ Chi tiết lỗi:")
                                for word in wrong_words:
                                    st.warning(word)
                            else:
                                st.success("🎉 Hoàn hảo! Không có lỗi nào!")

                            # Gợi ý luyện tập
                            if wrong_words:
                                with st.expander("💡 Gợi ý cải thiện"):
                                    st.write("**Cách luyện tập hiệu quả:**")
                                    st.write("1. Nghe lại câu mẫu từ người bản ngữ")
                                    st.write("2. Tập phát âm chậm từng từ bị sai")
                                    st.write("3. Ghi âm lại và so sánh")
                                    st.write("4. Luyện tập 3-5 lần/ngày")

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
                    st.write(f"**📝 Câu mẫu:** {item['reference']}")
                    st.write(f"**🗣️ Nhận dạng:** {item['transcribed']}")
                with col_h2:
                    st.metric("Điểm số", f"{item['score']}/100")
                    st.write(f"**👤 Người dùng:** {item['user']}")
                    st.write(f"**🎮 Chế độ:** {item['mode']}")

                if item["wrong_words"]:
                    st.write("**⚠️ Lỗi:**")
                    for w in item["wrong_words"]:
                        st.write(f"- {w}")

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
            st.metric("Tổng số lần chấm", stats["total_attempts"])

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

        # Phân tích từ hay sai
        st.subheader("🔍 Từ thường bị sai")
        weak_words = get_weak_words()

        if weak_words:
            col_weak1, col_weak2 = st.columns([2, 1])

            with col_weak1:
                st.write("**Top 10 từ cần luyện thêm:**")
                for idx, (word, count) in enumerate(weak_words, 1):
                    st.write(f"{idx}. **{word}** - Sai {count} lần")

            with col_weak2:
                # Biểu đồ từ hay sai
                if len(weak_words) > 0:
                    words, counts = zip(*weak_words[:5])
                    fig_weak = go.Figure(
                        data=[
                            go.Bar(
                                x=list(counts),
                                y=list(words),
                                orientation="h",
                                marker_color="#ff5252",
                            )
                        ]
                    )
                    fig_weak.update_layout(
                        title="Top 5 từ hay sai", xaxis_title="Số lần", height=300
                    )
                    st.plotly_chart(fig_weak, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu về từ bị sai.")

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
                    file_name=f"pronunciation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with col_export2:
            json_data = export_history_to_json()
            if json_data:
                st.download_button(
                    label="💾 Tải JSON (Backup)",
                    data=json_data,
                    file_name=f"pronunciation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
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
        st.info("📊 Chưa có dữ liệu thống kê. Hãy bắt đầu luyện tập!")

# TAB 3: THƯ VIỆN CÂU
with tab3:
    st.title("📚 Thư viện câu mẫu")

    st.markdown("### Danh sách câu theo chủ đề")

    for category, sentences in SENTENCE_LIBRARY.items():
        with st.expander(f"{category} ({len(sentences)} câu)"):
            for idx, sentence in enumerate(sentences, 1):
                col_sent, col_fav, col_note = st.columns([3, 1, 1])

                with col_sent:
                    st.write(f"{idx}. {sentence}")

                with col_fav:
                    if sentence in st.session_state.favorite_sentences:
                        if st.button("⭐", key=f"unfav_{category}_{idx}"):
                            st.session_state.favorite_sentences.remove(sentence)
                            st.rerun()
                    else:
                        if st.button("☆", key=f"fav_{category}_{idx}"):
                            st.session_state.favorite_sentences.append(sentence)
                            st.rerun()

                with col_note:
                    if st.button("📝", key=f"note_{category}_{idx}"):
                        st.session_state[f"show_note_{sentence}"] = True

                # Hiển thị form ghi chú
                if st.session_state.get(f"show_note_{sentence}", False):
                    with st.form(key=f"note_form_{category}_{idx}"):
                        current_note = st.session_state.sentence_notes.get(sentence, "")
                        note_text = st.text_area(
                            "Ghi chú của bạn:", value=current_note, height=100
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Lưu"):
                                if note_text.strip():
                                    st.session_state.sentence_notes[sentence] = (
                                        note_text
                                    )
                                else:
                                    if sentence in st.session_state.sentence_notes:
                                        del st.session_state.sentence_notes[sentence]
                                st.session_state[f"show_note_{sentence}"] = False
                                st.rerun()

                        with col_cancel:
                            if st.form_submit_button("❌ Hủy"):
                                st.session_state[f"show_note_{sentence}"] = False
                                st.rerun()

    st.divider()

    # Danh sách yêu thích
    st.markdown("### ⭐ Câu yêu thích của bạn")

    if st.session_state.favorite_sentences:
        for idx, sentence in enumerate(st.session_state.favorite_sentences, 1):
            col_fav_sent, col_fav_note, col_fav_remove = st.columns([3, 1, 1])

            with col_fav_sent:
                st.write(f"{idx}. {sentence}")
                # Hiển thị ghi chú nếu có
                if sentence in st.session_state.sentence_notes:
                    st.caption(f"📝 {st.session_state.sentence_notes[sentence]}")

            with col_fav_note:
                if st.button("📝", key=f"note_fav_{idx}"):
                    st.session_state[f"show_note_fav_{sentence}"] = True

            with col_fav_remove:
                if st.button("🗑️", key=f"remove_fav_{idx}"):
                    st.session_state.favorite_sentences.remove(sentence)
                    st.rerun()

            # Form ghi chú cho câu yêu thích
            if st.session_state.get(f"show_note_fav_{sentence}", False):
                with st.form(key=f"note_form_fav_{idx}"):
                    current_note = st.session_state.sentence_notes.get(sentence, "")
                    note_text = st.text_area(
                        "Ghi chú của bạn:", value=current_note, height=100
                    )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Lưu"):
                            if note_text.strip():
                                st.session_state.sentence_notes[sentence] = note_text
                            else:
                                if sentence in st.session_state.sentence_notes:
                                    del st.session_state.sentence_notes[sentence]
                            st.session_state[f"show_note_fav_{sentence}"] = False
                            st.rerun()

                    with col_cancel:
                        if st.form_submit_button("❌ Hủy"):
                            st.session_state[f"show_note_fav_{sentence}"] = False
                            st.rerun()
    else:
        st.info("Chưa có câu yêu thích. Nhấn ☆ để thêm câu vào danh sách!")

# TAB 4: CÀI ĐẶT
with tab4:
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
        "Số lần luyện tập mỗi ngày:",
        min_value=1,
        max_value=50,
        value=st.session_state.daily_goal,
        help="Đặt mục tiêu số lần luyện tập hàng ngày",
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
    **🎯 Ứng dụng Chấm Phát Âm Tiếng Anh**
    
    **Phiên bản:** 2.0 Enhanced
    
    **Tính năng chính:**
    - Chấm điểm phát âm tự động với AI
    - Thống kê chi tiết và biểu đồ trực quan
    - Theo dõi streak và mục tiêu hàng ngày
    - Thư viện câu mẫu phong phú
    - Ghi chú cá nhân cho từng câu
    - Sao lưu/khôi phục dữ liệu
    - Phân tích từ hay bị sai
    
    **Công nghệ:**
    - Streamlit
    - OpenAI Whisper
    - Plotly Charts
    - FuzzyWuzzy
    
    **Hỗ trợ:** Mọi thắc mắc vui lòng liên hệ qua email hoặc GitHub.
    """
    )

    st.divider()

    # Nút reset toàn bộ
    st.subheader("🚨 Zone Nguy hiểm")

    if st.button("🗑️ Xóa toàn bộ dữ liệu và cài đặt", type="secondary"):
        if st.session_state.get("confirm_reset_all", False):
            st.session_state.history = []
            st.session_state.favorite_sentences = []
            st.session_state.sentence_notes = {}
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
    color: #1f77b4; /* xanh nhạt khi hover */
}
</style>

<div style='text-align: center; color: gray; padding: 16px 0; font-size: 14px;'>
    <p><strong>Ứng dụng Chấm Phát Âm Tiếng Anh</strong></p>
    <p>Miễn phí • Offline/Online • Không dùng API trả phí</p>
    <p>Sử dụng: Whisper (OpenAI) + Streamlit</p>
    <p style='margin-top:10px;'>© 2025 
        <a href='https://www.facebook.com/augusttrung1823/' target='_blank' class='footer-link'>
            August Trung
        </a>. All rights reserved.
    </p>
</div>
""",
    unsafe_allow_html=True,
)
