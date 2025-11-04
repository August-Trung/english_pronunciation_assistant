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

# Page config
st.set_page_config(
    page_title="English Speaking Practice",
    page_icon="assets/logo-augusttrung.png",
    layout="wide",
)

# Custom CSS
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

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "model" not in st.session_state:
    st.session_state.model = None

if "user_name" not in st.session_state:
    st.session_state.user_name = "Student"

if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 5

if "model_size" not in st.session_state:
    st.session_state.model_size = "base"


@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load Whisper model (only once)"""
    try:
        model = whisper.load_model(model_size)
        return model
    except Exception as e:
        st.error(f"Error loading Whisper model: {e}")
        return None


# Auto-load model on first run
if st.session_state.model is None:
    st.session_state.model = load_whisper_model("base")


def convert_audio_to_wav(audio_file):
    """Convert audio file to standard WAV format"""
    try:
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_file.name, format="wav")
        return temp_file.name
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None


def transcribe_audio(audio_path, model):
    """Transcribe audio using Whisper with confidence check"""
    try:
        result = model.transcribe(audio_path, language="en", word_timestamps=True)

        # Get transcribed text
        text = result["text"].strip()

        # Calculate average confidence from segments
        avg_confidence = 0
        if "segments" in result and len(result["segments"]) > 0:
            confidences = []
            for segment in result["segments"]:
                if "no_speech_prob" in segment:
                    # Lower no_speech_prob = higher confidence
                    confidence = 1.0 - segment["no_speech_prob"]
                    confidences.append(confidence)

            if confidences:
                avg_confidence = sum(confidences) / len(confidences)

        return text, avg_confidence
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None, 0


def detect_transcription_quality(text, whisper_confidence):
    """
    Detect transcription quality using linguistic patterns (NOT content-specific)
    Returns: (quality_score: float 0-1, warnings: list)
    """
    warnings = []
    quality_score = whisper_confidence

    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, ["No speech detected"]

    # 1. Check for very short/fragmented words (sign of poor audio)
    very_short = [w for w in words if len(re.sub(r"[^a-zA-Z]", "", w)) <= 2]
    very_short_ratio = len(very_short) / word_count

    if very_short_ratio > 0.5:
        quality_score -= 0.2
        warnings.append("Many short/unclear words detected")

    # 2. Check for repeated words (stuttering or audio glitch)
    word_list = [re.sub(r"[^a-z]", "", w.lower()) for w in words]
    word_list = [w for w in word_list if w]

    if len(word_list) > 1:
        repeated_count = 0
        for i in range(len(word_list) - 1):
            if word_list[i] == word_list[i + 1] and len(word_list[i]) > 2:
                repeated_count += 1

        if repeated_count > 2:
            quality_score -= 0.1
            warnings.append("Audio may have stuttering or glitches")

    # 3. Check sentence structure completeness
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    if len(sentences) > 0:
        incomplete_count = 0
        for sent in sentences:
            sent_words = sent.lower().split()
            # Very basic: sentence should have at least subject + verb pattern
            has_pronoun = any(
                w in sent_words
                for w in ["i", "you", "he", "she", "we", "they", "it", "my", "there"]
            )
            has_verb = any(
                w in sent_words
                for w in [
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
                    "will",
                    "like",
                    "love",
                    "want",
                    "go",
                    "play",
                    "make",
                ]
            )

            if len(sent_words) > 4 and not (has_pronoun and has_verb):
                incomplete_count += 1

        if incomplete_count > len(sentences) // 2:
            quality_score -= 0.15
            warnings.append("Some sentences may be incomplete or unclear")

    # 4. Check for excessive special characters (sign of recognition failure)
    special_char_count = len(re.findall(r"[^a-zA-Z0-9\s\.,!?\'-]", text))
    if special_char_count > word_count * 0.1:
        quality_score -= 0.15
        warnings.append("Audio contains unclear segments")

    quality_score = max(quality_score, 0.1)

    return quality_score, warnings


def check_pronunciation(text, whisper_confidence=1.0):
    """
    Check pronunciation quality based on:
    1. Whisper confidence
    2. General linguistic quality (NOT content-specific)
    Returns score 0-2, level, adjusted confidence, and warnings
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0, "Needs practice", whisper_confidence, ["No speech detected"]

    # Detect quality issues using general patterns
    quality_score, warnings = detect_transcription_quality(text, whisper_confidence)

    # Calculate pronunciation score
    score = quality_score * 2.0  # Convert 0-1 to 0-2

    # Cap score based on quality
    if quality_score < 0.5:
        score = min(score, 1.0)
    elif quality_score < 0.7:
        score = min(score, 1.5)

    score = max(min(score, 2.0), 0.3)

    # Feedback level
    if quality_score < 0.6:
        level = "Needs practice"
    elif score >= 1.7:
        level = "Good"
    elif score >= 1.2:
        level = "Fair"
    else:
        level = "Needs practice"

    return round(score, 1), level, quality_score, warnings


def check_fluency(text):
    """
    Check fluency based on response length
    Returns score 0-2
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return 0

    # Simple scoring based on length
    if word_count < 10:
        score = 0.8
    elif 10 <= word_count < 25:
        score = 1.5
    else:
        score = 2.0

    return round(score, 1)


def check_grammar(text):
    """
    Basic grammar check
    Returns score 0-2
    """
    words = text.lower().split()
    score = 2.0

    # Check for common errors
    common_errors = [
        ("i is", "i am"),
        ("he are", "he is"),
        ("she are", "she is"),
        ("they is", "they are"),
        ("we is", "we are"),
    ]

    text_lower = text.lower()
    error_count = 0

    for wrong, correct in common_errors:
        if wrong in text_lower:
            error_count += 1
            score -= 0.5

    # Check for basic sentence structure
    has_verb = any(
        word in words
        for word in ["is", "am", "are", "have", "has", "like", "love", "play", "go"]
    )

    if not has_verb and len(words) > 3:
        score -= 0.5

    return max(round(score, 1), 1.0)


def check_vocabulary(text):
    """
    Check vocabulary diversity
    Returns score 0-2
    """
    words = text.lower().split()
    words_clean = [re.sub(r"[^a-z]", "", w) for w in words]
    words_clean = [w for w in words_clean if len(w) > 2]

    if len(words_clean) == 0:
        return 1.0

    # Calculate diversity
    unique_words = set(words_clean)
    diversity = len(unique_words) / len(words_clean)

    score = 1.0

    if diversity >= 0.7:
        score = 2.0
    elif diversity >= 0.5:
        score = 1.5
    else:
        score = 1.0

    return round(score, 1)


def check_communication(text, topic):
    """
    Check if student answered the topic
    Returns score 0-2
    """
    words = text.lower().split()
    word_count = len(words)

    score = 1.0

    # Length bonus
    if word_count >= 20:
        score += 0.5
    elif word_count < 10:
        score -= 0.3

    # Check for connectors (shows organized thinking)
    connectors = ["because", "and", "so", "but", "also"]
    has_connector = any(conn in words for conn in connectors)
    if has_connector:
        score += 0.3

    # Check for personal response markers
    personal_markers = ["i", "my", "me"]
    has_personal = any(marker in words for marker in personal_markers)
    if has_personal:
        score += 0.2

    return max(min(round(score, 1), 2.0), 0.5)


def generate_feedback(transcribed_text, breakdown, topic, quality_score=1.0):
    """
    Generate encouraging English feedback for elementary students
    Includes warnings about transcription quality when needed
    """
    feedback = []

    # Add IMPORTANT notice if quality is questionable
    if quality_score < 0.7:
        feedback.append("### ⚠️ IMPORTANT: Please Read This First!\n")
        feedback.append(f"**Audio Recognition Quality: {quality_score*100:.0f}%**\n")

        if quality_score < 0.5:
            feedback.append(
                "❌ **The audio was very unclear.** The text below might be VERY DIFFERENT from what you actually said!\n"
            )
            feedback.append("**What to do:**")
            feedback.append("1. ✅ Check if the text matches what you said")
            feedback.append("2. 🔄 If it's wrong, please record again")
            feedback.append("3. 🎤 Speak clearly and slowly")
            feedback.append("4. 🤫 Record in a quiet room\n")
        else:
            feedback.append(
                "⚠️ **Some words might not be recognized correctly.** Please check if the text below matches what you said.\n"
            )
            feedback.append("**Tips for better recognition:**")
            feedback.append("- Speak clearly (not too fast)")
            feedback.append("- Use a quiet room")
            feedback.append("- Hold microphone close to your mouth\n")

        feedback.append("---\n")

    feedback.append("### 🌟 Your Feedback\n")

    word_count = len(transcribed_text.split())

    # Adjust tone based on quality
    if quality_score < 0.6:
        feedback.append(
            "*Note: The scores below are based on what the system heard, which may not be accurate due to audio quality issues.*\n"
        )

    # Fluency feedback
    feedback.append("**Fluency & Speaking:**")
    if breakdown["Fluency"] >= 1.5:
        feedback.append("Great job! You spoke clearly and smoothly. Keep it up!")
    elif breakdown["Fluency"] >= 1.0:
        feedback.append(
            "Good effort! Try to speak a little more next time. You can add more details about your ideas."
        )
    else:
        feedback.append(
            "Keep practicing! Try to speak in longer sentences. For example, instead of saying 'I like blue', you can say 'I like blue because it makes me feel happy.'"
        )
    feedback.append("")

    # Vocabulary feedback
    feedback.append("**Vocabulary:**")
    if breakdown["Vocabulary"] >= 1.5:
        feedback.append(
            "Wonderful! You used different words in your answer. That's excellent!"
        )
    else:
        feedback.append(
            "Good start! Next time, try to use more describing words like 'beautiful', 'exciting', 'delicious', or 'interesting'."
        )
    feedback.append("")

    # Grammar feedback
    feedback.append("**Grammar:**")
    if breakdown["Grammar"] >= 1.5:
        feedback.append("Excellent! Your sentences were correct. Well done!")
    else:
        feedback.append(
            "Nice try! Remember to use complete sentences. For example: 'I like playing soccer' instead of 'Like soccer'."
        )
    feedback.append("")

    # Pronunciation feedback
    feedback.append("**Pronunciation:**")
    if quality_score < 0.5:
        feedback.append(
            "I couldn't hear your pronunciation clearly because of audio quality. Please:"
        )
        feedback.append("- Record in a quiet room with no background noise")
        feedback.append("- Speak directly into the microphone")
        feedback.append("- Speak at a normal speed (not too fast or slow)")
        feedback.append("- Make sure your device microphone works properly")
    elif quality_score < 0.7:
        feedback.append("Some parts were hard to hear. Try to:")
        feedback.append("- Speak more clearly")
        feedback.append("- Reduce background noise")
        feedback.append("- Check your microphone")
    elif breakdown["Pronunciation"] >= 1.7:
        feedback.append(
            "Amazing! Your pronunciation was clear and easy to understand. Keep speaking with confidence!"
        )
    elif breakdown["Pronunciation"] >= 1.2:
        feedback.append(
            "Good job! Your pronunciation was mostly clear. Keep practicing speaking slowly and clearly."
        )
    else:
        feedback.append(
            "Keep practicing! Try to speak each word clearly. You're doing great, and practice will make you even better!"
        )
    feedback.append("")

    # Communication feedback
    feedback.append("**Communication:**")
    if breakdown["Communication"] >= 1.5:
        feedback.append(
            "Fantastic! You answered the question well and shared your ideas clearly!"
        )
    else:
        feedback.append(
            "Good effort! Try to give more details when you answer. Think about: What? Why? How? When?"
        )
    feedback.append("")

    # Overall suggestion
    total_score = breakdown["Total"]
    feedback.append("---")
    feedback.append("### 💡 Suggestion for next time:\n")

    if quality_score < 0.6:
        feedback.append("**Most Important: Fix your audio quality first!**")
        feedback.append(
            "Your speaking might be good, but the system can't hear it properly."
        )
        feedback.append("Please follow the recording tips above, then try again. 🎤")
    elif total_score >= 8:
        feedback.append(
            "You're doing excellent! Keep practicing and try speaking about different topics."
        )
    elif total_score >= 6:
        feedback.append(
            "You're doing well! Try to speak a bit longer and use more interesting words."
        )
    else:
        feedback.append(
            "Great start! Keep practicing every day. Try to speak at least 2-3 sentences about any topic you like."
        )

    feedback.append(
        "\n**Remember:** Practice makes perfect! Don't be afraid to make mistakes. Every try makes you better! 🌈"
    )

    return "\n".join(feedback)


def analyze_speech(transcribed_text, topic, whisper_confidence=1.0):
    """
    Analyze speech with simplified criteria for elementary students
    Uses general linguistic patterns, NOT content-specific checks
    Returns score, feedback, and breakdown
    """
    if not transcribed_text or len(transcribed_text.strip()) == 0:
        return 0, ["⚠️ No speech detected. Please try again."], {}

    # Score each criterion (0-2 points each)
    pronunciation_score, pronunciation_level, quality_score, detected_warnings = (
        check_pronunciation(transcribed_text, whisper_confidence)
    )
    fluency_score = check_fluency(transcribed_text)
    grammar_score = check_grammar(transcribed_text)
    vocabulary_score = check_vocabulary(transcribed_text)
    communication_score = check_communication(transcribed_text, topic)

    # Apply quality penalty to all scores if recognition is questionable
    quality_multiplier = 1.0
    if quality_score < 0.5:
        quality_multiplier = 0.6  # Reduce all scores by 40%
    elif quality_score < 0.7:
        quality_multiplier = 0.8  # Reduce all scores by 20%

    # Apply multiplier to all scores except pronunciation (already considered)
    fluency_score *= quality_multiplier
    grammar_score *= quality_multiplier
    vocabulary_score *= quality_multiplier
    communication_score *= quality_multiplier

    # Total score out of 10
    total_score = (
        pronunciation_score
        + fluency_score
        + grammar_score
        + vocabulary_score
        + communication_score
    )

    # Convert to 0-10 scale
    final_score_10 = round(total_score, 1)

    # Create breakdown
    breakdown = {
        "Pronunciation": round(pronunciation_score, 1),
        "Fluency": round(fluency_score, 1),
        "Grammar": round(grammar_score, 1),
        "Vocabulary": round(vocabulary_score, 1),
        "Communication": round(communication_score, 1),
        "Total": final_score_10,
        "Confidence": round(quality_score * 100, 1),
        "RawConfidence": round(whisper_confidence * 100, 1),
        "DetectedWarnings": detected_warnings,
    }

    # Generate encouraging feedback
    feedback_text = generate_feedback(transcribed_text, breakdown, topic, quality_score)

    return final_score_10, feedback_text, breakdown


def save_result_to_history(topic, transcribed, score, feedback, breakdown=None):
    """Save result to history"""
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "topic": topic,
        "transcribed": transcribed,
        "score": score,
        "feedback": feedback,
        "word_count": len(transcribed.split()),
        "user": st.session_state.user_name,
        "breakdown": breakdown if breakdown else {},
    }
    st.session_state.history.append(result)


def export_history_to_csv():
    """Export history to CSV"""
    if not st.session_state.history:
        return None
    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode("utf-8")


def export_history_to_json():
    """Export history to JSON"""
    if not st.session_state.history:
        return None
    data = {
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": st.session_state.user_name,
        "history": st.session_state.history,
    }
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def import_history_from_json(json_file):
    """Import history from JSON"""
    try:
        data = json.loads(json_file.read())
        st.session_state.history = data.get("history", [])
        return True
    except Exception as e:
        st.error(f"Import error: {e}")
        return False


def get_statistics():
    """Calculate statistics"""
    if not st.session_state.history:
        return None

    df = pd.DataFrame(st.session_state.history)

    stats = {
        "total_attempts": len(df),
        "avg_score": df["score"].mean(),
        "max_score": df["score"].max(),
        "min_score": df["score"].min(),
        "today_attempts": len(df[df["date"] == datetime.now().strftime("%Y-%m-%d")]),
        "excellent_count": len(df[df["score"] >= 8]),
        "good_count": len(df[(df["score"] >= 6) & (df["score"] < 8)]),
        "average_count": len(df[(df["score"] >= 4) & (df["score"] < 6)]),
        "poor_count": len(df[df["score"] < 4]),
    }

    return stats


def calculate_streak():
    """Calculate practice streak"""
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
    """Create progress chart"""
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
            name="Score",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        )
    )

    fig.add_hline(
        y=8, line_dash="dash", line_color="green", annotation_text="Excellent (8)"
    )
    fig.add_hline(
        y=6, line_dash="dash", line_color="orange", annotation_text="Good (6)"
    )

    fig.update_layout(
        title="📈 Your Progress",
        xaxis_title="Practice Number",
        yaxis_title="Score",
        yaxis_range=[0, 11],
        hovermode="x unified",
    )

    return fig


def create_weekly_chart():
    """Create weekly activity chart"""
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
            name="Practice Times",
            marker_color="#1f77b4",
        )
    )

    fig.update_layout(
        title="📅 Last 7 Days Activity",
        xaxis_title="Date",
        yaxis_title="Number of Practices",
    )

    return fig


# ========== MAIN INTERFACE ==========

# Header with tabs
tab1, tab2, tab3 = st.tabs(["🎤 Practice", "📊 Stats", "⚙️ Settings"])

# TAB 1: PRACTICE
with tab1:
    st.title("🎤 ENGLISH SPEAKING PRACTICE")
    st.markdown("### Practice speaking English with fun topics!")

    # User info and streak
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.markdown(f"**👤 Student:** {st.session_state.user_name}")

    with col_info2:
        streak = calculate_streak()
        if streak > 0:
            st.markdown(f"**🔥 Streak:** {streak} days")

    with col_info3:
        stats = get_statistics()
        if stats:
            st.markdown(
                f"**📈 Today:** {stats['today_attempts']}/{st.session_state.daily_goal}"
            )
            progress = min(stats["today_attempts"] / st.session_state.daily_goal, 1.0)
            st.progress(progress)

    st.divider()

    # Topic input
    st.subheader("📝 Step 1: Choose your topic")

    # Provide example topics
    example_topics = [
        "What is your favorite color?",
        "Tell me about your family",
        "What do you like to do after school?",
        "Describe your best friend",
        "What is your favorite food?",
        "Tell me about your pet",
        "What do you want to be when you grow up?",
        "Describe your favorite toy",
    ]

    col_topic1, col_topic2 = st.columns([3, 1])

    with col_topic1:
        topic_input = st.text_input(
            "Your speaking topic:",
            value="",
            placeholder="Example: What is your favorite color?",
            help="Choose a topic you want to talk about",
        )

    with col_topic2:
        if st.button("🎲 Random Topic", use_container_width=True):
            import random

            topic_input = random.choice(example_topics)
            st.rerun()

    # Show example topics
    with st.expander("💡 Need ideas? Click here for example topics"):
        st.write("Here are some fun topics you can talk about:")
        for i, topic in enumerate(example_topics, 1):
            st.write(f"{i}. {topic}")

    if topic_input:
        st.info(f"📌 Your topic: **{topic_input}**")

    st.divider()

    # Recording section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ Step 2a: Record your answer")
        audio_recording = st.audio_input("Click to record:")

    with col2:
        st.subheader("📤 Step 2b: Or upload audio file")
        uploaded_file = st.file_uploader(
            "Choose audio file:",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Supported formats: WAV, MP3, M4A, OGG, FLAC",
        )

    st.divider()

    # Analyze button
    st.subheader("🎯 Step 3: Check your speaking")

    if st.button("🔍 Analyze My Speaking", type="primary", use_container_width=True):

        if not topic_input:
            st.warning("⚠️ Please enter a topic first!")
        elif not audio_recording and not uploaded_file:
            st.error("⚠️ Please record or upload your audio!")
        elif not st.session_state.model:
            st.error("⚠️ Model not loaded. Please load it in Settings.")
        else:
            with st.spinner("🔄 Processing your audio..."):
                try:
                    audio_source = uploaded_file if uploaded_file else audio_recording
                    wav_path = convert_audio_to_wav(audio_source)

                    if wav_path:
                        with st.spinner("🎧 Listening to your speaking..."):
                            transcription_result = transcribe_audio(
                                wav_path, st.session_state.model
                            )

                            if transcription_result:
                                transcribed_text, whisper_confidence = (
                                    transcription_result
                                )
                            else:
                                transcribed_text = None
                                whisper_confidence = 0

                        try:
                            os.unlink(wav_path)
                        except:
                            pass

                        if transcribed_text:
                            score, feedback, breakdown = analyze_speech(
                                transcribed_text, topic_input, whisper_confidence
                            )

                            # Show confidence warning if issues detected
                            if (
                                "DetectedWarnings" in breakdown
                                and breakdown["DetectedWarnings"]
                            ):
                                with st.expander(
                                    "⚠️ Quality Warnings Detected - Click to see details"
                                ):
                                    st.warning(
                                        "The system detected some potential audio quality issues:"
                                    )
                                    for warning in breakdown["DetectedWarnings"]:
                                        st.write(f"• {warning}")
                                    st.info(
                                        "💡 These warnings don't mean your speaking is bad! They just mean the microphone might not have captured everything clearly. Try recording again for a better result."
                                    )

                            save_result_to_history(
                                topic_input,
                                transcribed_text,
                                score,
                                feedback,
                                breakdown,
                            )

                            st.success("✅ Analysis complete!")
                            st.balloons()

                            st.divider()

                            # Results
                            col_result1, col_result2 = st.columns(2)

                            with col_result1:
                                st.markdown("**📌 Topic:**")
                                st.info(topic_input)

                            with col_result2:
                                st.markdown("**🗣️ What you said:**")
                                st.info(transcribed_text)

                                # Show confidence indicator
                                if "Confidence" in breakdown:
                                    conf_pct = breakdown["Confidence"]
                                    if conf_pct < 60:
                                        st.error(
                                            f"🔴 Recognition Confidence: {conf_pct:.0f}% - Very Low"
                                        )
                                    elif conf_pct < 70:
                                        st.warning(
                                            f"🟠 Recognition Confidence: {conf_pct:.0f}% - Low"
                                        )
                                    elif conf_pct < 85:
                                        st.info(
                                            f"🟡 Recognition Confidence: {conf_pct:.0f}% - Medium"
                                        )
                                    else:
                                        st.success(
                                            f"🟢 Recognition Confidence: {conf_pct:.0f}% - Good"
                                        )

                            # Detailed scores
                            st.markdown("### 🎯 Your Scores")

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
                                            help="Total Score",
                                        )
                                    else:
                                        st.metric(
                                            f"{emoji} {name[:4]}.",
                                            f"{breakdown.get(name, 0):.1f}/2",
                                            help=name,
                                        )

                            st.divider()

                            # Overall score with color
                            if score >= 8:
                                score_class = "score-excellent"
                                grade = "Excellent!"
                                emoji_grade = "🟢"
                            elif score >= 6:
                                score_class = "score-good"
                                grade = "Good Job!"
                                emoji_grade = "🟡"
                            elif score >= 4:
                                score_class = "score-average"
                                grade = "Keep Trying!"
                                emoji_grade = "🟠"
                            else:
                                score_class = "score-poor"
                                grade = "Keep Practicing!"
                                emoji_grade = "🔴"

                            col_score1, col_score2 = st.columns([1, 2])

                            with col_score1:
                                st.markdown(
                                    f'<div class="{score_class}">{emoji_grade} {score:.1f}/10</div>',
                                    unsafe_allow_html=True,
                                )

                            with col_score2:
                                st.markdown(f"### {grade}")
                                st.progress(score / 10)

                                if score >= 8:
                                    st.success(
                                        "🎉 Excellent! Your speaking is very good!"
                                    )
                                elif score >= 6:
                                    st.info(
                                        "👍 Good job! Keep practicing to get even better!"
                                    )
                                elif score >= 4:
                                    st.warning(
                                        "💪 You're doing okay! Read the feedback below to improve."
                                    )
                                else:
                                    st.info(
                                        "📚 Keep practicing! Every practice makes you better!"
                                    )

                            # Detailed feedback
                            st.markdown("### 💬 Your Feedback")
                            st.markdown(feedback)

                        else:
                            st.error(
                                "❌ Could not understand the audio. Please try again."
                            )
                    else:
                        st.error("❌ Could not process audio file.")

                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # Recent history
    if st.session_state.history:
        st.divider()
        st.subheader("📜 Recent Practice (Last 5)")

        for item in reversed(st.session_state.history[-5:]):
            with st.expander(f"⏰ {item['timestamp']} - Score: {item['score']}/10"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"**📌 Topic:** {item['topic']}")
                    st.write(f"**🗣️ You said:** {item['transcribed'][:100]}...")
                with col_h2:
                    st.metric("Score", f"{item['score']}/10")
                    st.write(f"**👤 Student:** {item['user']}")
                    st.write(f"**📝 Words:** {item['word_count']}")

                if "breakdown" in item and item["breakdown"]:
                    st.write("**📊 Detailed Scores:**")
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

# TAB 2: STATISTICS
with tab2:
    st.title("📊 Your Statistics")

    stats = get_statistics()

    if stats and stats["total_attempts"] > 0:
        # Show streak
        streak = calculate_streak()
        if streak > 0:
            st.markdown(
                f"""
            <div class="streak-badge">
                🔥 {streak} days in a row! Keep going!
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown("")

        # Overview
        st.subheader("📈 Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Practices", stats["total_attempts"])

        with col2:
            st.metric("Average Score", f"{stats['avg_score']:.1f}/10")

        with col3:
            st.metric("Best Score", f"{stats['max_score']}/10")

        with col4:
            st.metric("Today", f"{stats['today_attempts']} times")

        st.divider()

        # Charts
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            progress_chart = create_progress_chart()
            if progress_chart:
                st.plotly_chart(progress_chart, use_container_width=True)

        with col_chart2:
            weekly_chart = create_weekly_chart()
            if weekly_chart:
                st.plotly_chart(weekly_chart, use_container_width=True)

        st.divider()

        # Score categories
        st.subheader("🎯 Score Distribution")

        col_cat1, col_cat2, col_cat3, col_cat4 = st.columns(4)

        with col_cat1:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #00c853;">
                <h3>🟢 Excellent</h3>
                <h2>{stats['excellent_count']}</h2>
                <p>≥ 8 points</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat2:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ffd600;">
                <h3>🟡 Good</h3>
                <h2>{stats['good_count']}</h2>
                <p>6-7 points</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat3:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ff9800;">
                <h3>🟠 OK</h3>
                <h2>{stats['average_count']}</h2>
                <p>4-5 points</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_cat4:
            st.markdown(
                f"""
            <div class="stat-box" style="border-left: 4px solid #ff5252;">
                <h3>🔴 Keep Trying</h3>
                <h2>{stats['poor_count']}</h2>
                <p>< 4 points</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Export data
        st.subheader("💾 Download Your Data")

        col_export1, col_export2, col_export3 = st.columns(3)

        with col_export1:
            csv_data = export_history_to_csv()
            if csv_data:
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"speaking_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with col_export2:
            json_data = export_history_to_json()
            if json_data:
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"speaking_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

        with col_export3:
            if st.button("🗑️ Clear History", use_container_width=True):
                if st.session_state.get("confirm_delete", False):
                    st.session_state.history = []
                    st.session_state.confirm_delete = False
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    st.warning("⚠️ Click again to confirm!")

    else:
        st.info("📊 No statistics yet. Start practicing to see your progress!")

# TAB 3: SETTINGS
with tab3:
    st.title("⚙️ Settings")

    # User info
    st.subheader("👤 Your Information")
    user_name = st.text_input("Your name:", value=st.session_state.user_name)

    if user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        st.success("✅ Name saved!")

    st.divider()

    # Daily goal
    st.subheader("🎯 Daily Goal")
    daily_goal = st.slider(
        "Number of practices per day:",
        min_value=1,
        max_value=20,
        value=st.session_state.daily_goal,
        help="Set your daily practice goal",
    )

    if daily_goal != st.session_state.daily_goal:
        st.session_state.daily_goal = daily_goal
        st.success(f"✅ Goal set to {daily_goal} practices per day!")

    st.divider()

    # Whisper model settings
    st.subheader("🤖 AI Model Settings")

    col_model1, col_model2 = st.columns(2)

    with col_model1:
        model_size = st.selectbox(
            "Choose Whisper model:",
            options=["tiny", "base", "small"],
            index=["tiny", "base", "small"].index(st.session_state.model_size),
            help="""
            - tiny: Fastest, less accurate (39MB)
            - base: Balanced speed and accuracy (74MB) - Recommended
            - small: Slower but more accurate (244MB)
            """,
        )

    with col_model2:
        if st.session_state.model is not None:
            st.success(f"Current model: **{st.session_state.model_size}**")
        else:
            st.warning("Model not loaded")

    if st.button("Load/Reload Model", type="primary", use_container_width=True):
        with st.spinner(f"Loading {model_size} model..."):
            model = load_whisper_model(model_size)
            if model:
                st.session_state.model = model
                st.session_state.model_size = model_size
                st.success(f"✅ Successfully loaded {model_size} model!")
                st.balloons()
            else:
                st.error("❌ Could not load model. Please try again.")

    st.divider()

    # Backup & Restore
    st.subheader("💾 Backup & Restore")

    col_backup1, col_backup2 = st.columns(2)

    with col_backup1:
        st.markdown("**Export Data (Backup)**")
        json_backup = export_history_to_json()
        if json_backup:
            st.download_button(
                label="💾 Download Backup",
                data=json_backup,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("No data to backup")

    with col_backup2:
        st.markdown("**Import Data (Restore)**")
        upload_backup = st.file_uploader(
            "Choose backup file:",
            type=["json"],
            help="Upload your backup JSON file",
        )

        if upload_backup:
            if st.button("📤 Restore Data", use_container_width=True):
                if import_history_from_json(upload_backup):
                    st.success("✅ Data restored successfully!")
                    st.rerun()
                else:
                    st.error("❌ Could not restore data. Invalid file.")

    st.divider()

    # App information
    st.subheader("ℹ️ About This App")

    st.info(
        """
    **🎤 English Speaking Practice for Elementary Students**
    
    **Version:** 4.0 - Elementary Edition
    
    **Features:**
    - AI-powered speech recognition (Whisper)
    - Simple scoring: Pronunciation, Fluency, Grammar, Vocabulary, Communication
    - Encouraging English feedback
    - Progress tracking with fun charts
    - Daily goals and streak tracking
    - Backup and restore your progress
    
    **How to Use:**
    1. Choose a topic you want to talk about
    2. Record your answer (or upload audio)
    3. Get your score and helpful feedback
    4. Practice every day to improve!
    
    **Scoring System:**
    - Each skill: 0-2 points
    - Total: 0-10 points
    - 8-10: Excellent! 🟢
    - 6-7: Good Job! 🟡
    - 4-5: Keep Trying! 🟠
    - 0-3: Keep Practicing! 🔴
    
    **Technology:**
    - Streamlit (Web Interface)
    - OpenAI Whisper (Speech Recognition)
    - Plotly (Charts)
    
    **Remember:** Practice makes perfect! Don't worry about mistakes - they help you learn! 🌈
    """
    )

    st.divider()

    # Reset button
    st.subheader("🚨 Danger Zone")

    if st.button("🗑️ Delete All Data and Settings", type="secondary"):
        if st.session_state.get("confirm_reset_all", False):
            st.session_state.history = []
            st.session_state.user_name = "Student"
            st.session_state.daily_goal = 5
            st.session_state.confirm_reset_all = False
            st.success("✅ All data reset!")
            st.rerun()
        else:
            st.session_state.confirm_reset_all = True
            st.error("⚠️ WARNING: You will lose all your data! Click again to confirm.")

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
    <p><strong>🎤 English Speaking Practice for Elementary Students</strong></p>
    <p>Free • Offline/Online • No API costs</p>
    <p>Powered by: Whisper (OpenAI) + Streamlit</p>
    <p style='margin-top:10px;'>© 2025 
        <a href='https://www.facebook.com/augusttrung1823/' target='_blank' class='footer-link'>
            August Trung
        </a>. All rights reserved.
    </p>
</div>
""",
    unsafe_allow_html=True,
)
