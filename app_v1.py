import streamlit as st
import whisper
from fuzzywuzzy import fuzz
from pydub import AudioSegment
import numpy as np
import tempfile
import os
from datetime import datetime
import io
import difflib

# Cấu hình trang
st.set_page_config(
    page_title="Chấm Phát Âm Tiếng Anh",
    page_icon="assets/logo-augusttrung.png",
    layout="wide",
)


# Khởi tạo session state
if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = None


@st.cache_resource
def load_whisper_model(model_size="base"):
    """
    Load mô hình Whisper (chỉ load 1 lần)
    model_size: 'tiny', 'base', 'small', 'medium', 'large'
    - tiny: nhanh nhất, nhẹ nhất (39M)
    - base: cân bằng tốc độ/độ chính xác (74M) - Khuyên dùng
    """
    try:
        model = whisper.load_model(model_size)
        return model
    except Exception as e:
        st.error(f"Lỗi khi load Whisper model: {e}")
        return None


def convert_audio_to_wav(audio_file):
    """
    Chuyển đổi file audio về định dạng WAV chuẩn
    """
    try:
        # Đọc file audio
        audio = AudioSegment.from_file(audio_file)

        # Chuyển về mono, sample rate 16000 (chuẩn cho Whisper)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        # Lưu vào file tạm
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_file.name, format="wav")

        return temp_file.name
    except Exception as e:
        st.error(f"Lỗi chuyển đổi audio: {e}")
        return None


def transcribe_audio(audio_path, model):
    """
    Nhận dạng giọng nói từ file audio bằng Whisper
    """
    try:
        result = model.transcribe(audio_path, language="en")
        return result["text"].strip()
    except Exception as e:
        st.error(f"Lỗi nhận dạng giọng nói: {e}")
        return None


def compare_texts(reference, transcribed):
    """
    So sánh câu mẫu với câu nhận dạng được
    Trả về: điểm số, tỷ lệ chính xác, danh sách từ sai
    """
    # Chuẩn hóa text (lowercase, loại bỏ dấu câu thừa)
    ref_clean = reference.lower().strip()
    trans_clean = transcribed.lower().strip()

    # Tính độ tương đồng bằng fuzzywuzzy
    similarity = fuzz.ratio(ref_clean, trans_clean)

    # Tách từ để tìm từ sai
    ref_words = ref_clean.split()
    trans_words = trans_clean.split()

    # Sử dụng difflib để tìm khác biệt
    matcher = difflib.SequenceMatcher(None, ref_words, trans_words)
    wrong_words = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            # Từ bị thiếu
            for word in ref_words[i1:i2]:
                wrong_words.append(f"❌ Thiếu: '{word}'")
        elif tag == "insert":
            # Từ thừa
            for word in trans_words[j1:j2]:
                wrong_words.append(f"➕ Thừa: '{word}'")
        elif tag == "replace":
            # Từ sai
            for ref_w, trans_w in zip(ref_words[i1:i2], trans_words[j1:j2]):
                wrong_words.append(f"🔄 '{ref_w}' → '{trans_w}'")

    return similarity, wrong_words


def save_result_to_history(reference, transcribed, score, wrong_words):
    """
    Lưu kết quả vào lịch sử
    """
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reference": reference,
        "transcribed": transcribed,
        "score": score,
        "wrong_words": wrong_words,
    }
    st.session_state.history.append(result)


def export_history_to_csv():
    """
    Xuất lịch sử ra CSV
    """
    if not st.session_state.history:
        return None

    csv_content = "Thời gian,Câu mẫu,Câu nhận dạng,Điểm,Từ sai\n"
    for item in st.session_state.history:
        wrong_words_str = (
            "; ".join(item["wrong_words"]) if item["wrong_words"] else "Không có"
        )
        csv_content += f"\"{item['timestamp']}\",\"{item['reference']}\",\"{item['transcribed']}\",{item['score']},\"{wrong_words_str}\"\n"

    return csv_content


# ========== GIAO DIỆN CHÍNH ==========

st.title("ỨNG DỤNG CHẤM PHÁT ÂM TIẾNG ANH")
# st.markdown("### 🎯 Miễn phí - Chạy offline/online - Không API trả phí")

st.divider()

# Sidebar - Cài đặt
with st.sidebar:
    st.header("⚙️ Cài đặt")

    model_size = st.selectbox(
        "Chọn mô hình Whisper:",
        ["tiny", "base", "small"],
        index=1,
        help="base: cân bằng tốc độ/độ chính xác (khuyên dùng)",
    )

    if st.button("🔄 Load Model"):
        with st.spinner("Đang tải mô hình..."):
            st.session_state.model = load_whisper_model(model_size)
            if st.session_state.model:
                st.success(f"✅ Đã load model {model_size}!")

    st.divider()

    st.header("📊 Lịch sử")
    if st.session_state.history:
        st.write(f"Tổng số lần chấm: {len(st.session_state.history)}")

        if st.button("📥 Tải xuống lịch sử (CSV)"):
            csv_data = export_history_to_csv()
            if csv_data:
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"pronunciation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

        if st.button("🗑️ Xóa lịch sử"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Chưa có lịch sử chấm điểm")

# Load model mặc định nếu chưa có
if st.session_state.model is None:
    with st.spinner("Đang tải mô hình Whisper lần đầu..."):
        st.session_state.model = load_whisper_model("base")

# Phần nhập câu mẫu
st.subheader("📝 Bước 1: Nhập câu mẫu cần đọc")
reference_text = st.text_input(
    "Câu mẫu:",
    value="I want to eat an apple",
    placeholder="Nhập câu tiếng Anh cần luyện phát âm...",
)

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
        st.error("⚠️ Model chưa được load. Vui lòng đợi hoặc thử load lại.")
    else:
        with st.spinner("🔄 Đang xử lý âm thanh..."):
            try:
                # Xác định nguồn audio (ưu tiên file upload)
                audio_source = uploaded_file if uploaded_file else audio_recording

                # Chuyển đổi audio về WAV chuẩn
                wav_path = convert_audio_to_wav(audio_source)

                if wav_path:
                    # Nhận dạng giọng nói
                    with st.spinner("🎧 Đang nhận dạng giọng nói..."):
                        transcribed_text = transcribe_audio(
                            wav_path, st.session_state.model
                        )

                    # Xóa file tạm
                    try:
                        os.unlink(wav_path)
                    except:
                        pass

                    if transcribed_text:
                        # So sánh và tính điểm
                        score, wrong_words = compare_texts(
                            reference_text, transcribed_text
                        )

                        # Lưu vào lịch sử
                        save_result_to_history(
                            reference_text, transcribed_text, score, wrong_words
                        )

                        # Hiển thị kết quả
                        st.success("✅ Chấm điểm hoàn tất!")

                        st.divider()

                        # Kết quả chi tiết
                        st.subheader("📊 Kết quả chi tiết")

                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.markdown("**📝 Câu mẫu:**")
                            st.info(reference_text)

                        with col_b:
                            st.markdown("**🗣️ Bạn đã nói:**")
                            st.info(transcribed_text)

                        # Điểm số
                        st.markdown("### 🎯 Điểm số")

                        # Hiển thị điểm với màu sắc
                        if score >= 90:
                            score_color = "🟢"
                            grade = "Xuất sắc"
                        elif score >= 75:
                            score_color = "🟡"
                            grade = "Khá"
                        elif score >= 60:
                            score_color = "🟠"
                            grade = "Trung bình"
                        else:
                            score_color = "🔴"
                            grade = "Cần cải thiện"

                        st.markdown(f"## {score_color} **{score}/100** - {grade}")

                        # Progress bar
                        st.progress(score / 100)

                        # Từ sai
                        if wrong_words:
                            st.markdown("### ⚠️ Chi tiết lỗi:")
                            for word in wrong_words:
                                st.warning(word)
                        else:
                            st.success("🎉 Hoàn hảo! Không có lỗi nào!")

                    else:
                        st.error("❌ Không thể nhận dạng giọng nói. Vui lòng thử lại.")
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
            st.write(f"**Câu mẫu:** {item['reference']}")
            st.write(f"**Nhận dạng:** {item['transcribed']}")
            if item["wrong_words"]:
                st.write("**Lỗi:**")
                for w in item["wrong_words"]:
                    st.write(f"- {w}")

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
