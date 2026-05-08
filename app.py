import os
import shutil
import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

from utils.configs import DEFAULT_DEEPGRAM_API_KEY, DEFAULT_GROQ_API_KEY, PRELOADED_SAMPLES
from utils.asr_engines import transcribe_deepgram, transcribe_groq_whisper, perturb_transcript, benchmark_all_models
from utils.metrics_utils import calculate_wer, calculate_cer
from utils.report_utils import save_to_deliverables, LOG_FILE, DELIVERABLES_DIR

# Page Configuration
st.set_page_config(
    page_title="NammaVoice AI",
    page_icon="🎙️",
    layout="wide"
)

# Load secret API keys from environment silently
DEEPGRAM_KEY = DEFAULT_DEEPGRAM_API_KEY
GROQ_KEY = DEFAULT_GROQ_API_KEY

# -----------------------------------------------------------------------------
# ULTRA PREMIUM VERCEL/LINEAR INSPIRED ANIMATED DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Animated Background */
    .stApp {
        background: #020617;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0, transparent 50%),
            radial-gradient(at 50% 100%, rgba(236, 72, 153, 0.1) 0, transparent 50%);
        animation: gradientMove 20s ease infinite alternate;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Main Container Padding */
    .st-emotion-cache-1dp5vir {
        padding: 4rem 12% !important;
    }

    /* Animated Header */
    .header-box {
        text-align: center;
        margin-bottom: 60px;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .brand-logo-text {
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -3px;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC, #F472B6);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textGradient 8s linear infinite;
        margin-bottom: 12px;
    }
    
    @keyframes textGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Advanced Glassmorphism */
    .agent-box {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px 35px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUp 0.6s ease-out backwards;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .agent-box:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(56, 189, 248, 0.5);
        transform: scale(1.02) translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .agent-label {
        font-size: 1.2rem;
        font-weight: 800;
        color: #F3F4F6;
        min-width: 180px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }

    .agent-transcript-text {
        font-size: 1.35rem;
        color: #38BDF8;
        font-weight: 600;
        flex-grow: 1;
        margin-left: 25px;
        line-height: 1.4;
    }

    .agent-latency-badge {
        font-size: 0.9rem;
        color: #94A3B8;
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Pulsing Audio Input */
    div[data-testid="stAudioInput"] {
        border: 2px solid rgba(56, 189, 248, 0.2) !important;
        background: rgba(56, 189, 248, 0.02) !important;
        border-radius: 24px !important;
        animation: pulseBorder 3s infinite;
    }
    
    @keyframes pulseBorder {
        0% { border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.1); }
        50% { border-color: rgba(56, 189, 248, 0.5); box-shadow: 0 0 20px 5px rgba(56, 189, 248, 0.1); }
        100% { border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.1); }
    }

    /* Premium Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #38BDF8, #818CF8) !important;
        border-radius: 16px !important;
        padding: 15px 30px !important;
        height: auto !important;
        border: none !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(56, 189, 248, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 15px 30px rgba(56, 189, 248, 0.4) !important;
        background: linear-gradient(45deg, #0EA5E9, #6366F1) !important;
    }

    /* Progress Stats Badge */
    .progress-counter {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 50px;
        padding: 12px 35px;
        position: fixed;
        bottom: 30px;
        right: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        gap: 15px;
        z-index: 1000;
        animation: slideInRight 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .stDataFrame {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = None
if 'bench_raw' not in st.session_state:
    st.session_state.bench_raw = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# -----------------------------------------------------------------------------
# TOP HEADER ROW
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="brand-logo-text">NammaVoice AI</div>
    <div class="brand-sub">Next-Gen ASR Benchmarking & Locality Intelligence</div>
</div>
""", unsafe_allow_html=True)

# Main Application Layout
col_main_left, col_main_right = st.columns([1, 1.2], gap="large")

with col_main_left:
    st.markdown("### 🎙️ Session Input")
    st.write("Record your voice sample using the locality script.")
    
    selected_lang = st.selectbox(
        "Target Language",
        ["English", "Hindi", "Bengali", "Kannada"],
        key="live_lang"
    )
    
    recorded_audio = st.audio_input("Record now")
    
    st.write("")
    execute_bench = st.button("⚡ EXECUTE BENCHMARK", use_container_width=True)

with col_main_right:
    st.markdown("### 🧠 Live Intelligence")
    if st.session_state.transcripts is None:
        st.info("Waiting for audio input to begin analysis...")
    else:
        # Step 2: Render Transcripts with staggered animations
        for i, (model_name, data) in enumerate(st.session_state.transcripts.items()):
            st.markdown(f"""
            <div class="agent-box" style="animation-delay: {i*0.1}s">
                <span class="agent-label">🤖 {model_name}</span>
                <span class="agent-transcript-text">"{data['heard']}"</span>
                <span class="agent-latency-badge">⚡ {data['latency']}s</span>
            </div>
            """, unsafe_allow_html=True)

# Step 1: Execute Transcription
if recorded_audio is not None and execute_bench:
    with st.spinner("Processing speech through neural engines..."):
        os.makedirs("outputs", exist_ok=True)
        audio_path = os.path.join("outputs", "recorded_voice.wav")
        with open(audio_path, "wb") as f:
            f.write(recorded_audio.read())
            
        st.session_state.audio_path = audio_path
        language_codes = {"English": "en", "Hindi": "hi", "Bengali": "bn", "Kannada": "kn"}
        iso_lang = language_codes[selected_lang]
        
        results = benchmark_all_models(
            audio_path=audio_path, 
            deepgram_key=DEEPGRAM_KEY, 
            groq_key=GROQ_KEY,
            language=iso_lang
        )
        
        st.session_state.bench_raw = results
        formatted_results = {}
        for name, data in results.items():
            label = name.replace("_", " ").title()
            formatted_results[label] = {"heard": data["transcript"], "latency": data["latency"]}
        st.session_state.transcripts = formatted_results
        st.rerun()

# Step 3 & 4: Accuracy & Save (only if transcribed)
if st.session_state.transcripts is not None:
    st.markdown("---")
    col_acc_1, col_acc_2 = st.columns([1, 1], gap="medium")
    
    with col_acc_1:
        st.markdown("### 🎯 Verification")
        user_typed_sentence = st.text_input(
            "Enter ground truth:",
            placeholder="Type exactly what was spoken..."
        )
        
        if user_typed_sentence:
            score_data = []
            for model_name, data in st.session_state.transcripts.items():
                sim_score = round(fuzz.WRatio(user_typed_sentence, data["heard"]), 1)
                score_data.append({"model": model_name, "score": sim_score, "latency": data["latency"]})
            
            score_data_sorted = sorted(score_data, key=lambda x: x["score"], reverse=True)
            best_agent = score_data_sorted[0]
            
            st.markdown(f"""
            <div class="alert-banner">
                <span style="font-size: 2.5rem;">💎</span>
                <div>
                    <strong style="font-size: 1.2rem;">TOP ENGINE: {best_agent['model']}</strong><br>
                    Score: {best_agent['score']}% | Latency: {best_agent['latency']}s
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("💾 SAVE TO DELIVERABLES", use_container_width=True):
                save_to_deliverables(st.session_state.audio_path, user_typed_sentence, st.session_state.bench_raw)
                st.success("Sample successfully archived.")

    with col_acc_2:
        if user_typed_sentence:
            st.markdown("### 📊 Metrics Leaderboard")
            for item in score_data_sorted:
                st.markdown(f"""
                <div class="progress-wrapper" style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px;">
                    <div class="progress-text-row">
                        <span>{item['model']}</span>
                        <span style="color: #38BDF8;">{item['score']}%</span>
                    </div>
                    <div class="progress-bar-track"><div class="progress-bar-indicator" style="width: {item['score']}%;"></div></div>
                </div>
                """, unsafe_allow_html=True)

# Floating Progress Badge
if os.path.exists(LOG_FILE):
    df_deliverables = pd.read_csv(LOG_FILE)
    count = len(df_deliverables)
    st.markdown(f"""
    <div class="progress-counter">
        <span style="font-size: 1.5rem;">📂</span>
        <div>
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Progress</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #38BDF8;">{count} / 20 Samples</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if count > 0:
        with st.expander("Show Latest Benchmark History"):
            st.dataframe(df_deliverables.tail(10), use_container_width=True)
