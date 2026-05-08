import os
import json
import csv
import shutil
from datetime import datetime

DELIVERABLES_DIR = "deliverables/my_recordings"
LOG_FILE = os.path.join(DELIVERABLES_DIR, "metadata.csv")

from utils.metrics_utils import calculate_wer

DELIVERABLES_DIR = "deliverables/my_recordings"
LOG_FILE = os.path.join(DELIVERABLES_DIR, "performance_metrics.csv")

def ensure_deliverables_dir():
    if not os.path.exists(DELIVERABLES_DIR):
        os.makedirs(DELIVERABLES_DIR)
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Audio_File", "Ground_Truth", 
                "Deepgram_WER", "Deepgram_Latency", 
                "Groq_WER", "Groq_Latency", 
                "Whisper_WER", "Whisper_Latency",
                "Best_Model", "Baseline_Comparison"
            ])

def save_to_deliverables(audio_path, ground_truth, bench_results):
    ensure_deliverables_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_gt = "".join([c if c.isalnum() else "_" for c in ground_truth[:20]])
    new_audio_name = f"sample_{timestamp}_{safe_gt}.wav"
    dest_audio_path = os.path.join(DELIVERABLES_DIR, new_audio_name)
    
    # Copy audio file
    shutil.copy(audio_path, dest_audio_path)
    
    # Extract metrics
    dg_wer = calculate_wer(ground_truth, bench_results.get("deepgram", {}).get("transcript", ""))
    dg_lat = bench_results.get("deepgram", {}).get("latency", 0)
    
    gq_wer = calculate_wer(ground_truth, bench_results.get("groq", {}).get("transcript", ""))
    gq_lat = bench_results.get("groq", {}).get("latency", 0)
    
    wh_wer = calculate_wer(ground_truth, bench_results.get("whisper", {}).get("transcript", ""))
    wh_lat = bench_results.get("whisper", {}).get("latency", 0)
    
    # Determine if any model beat the baseline
    wers = {"Deepgram": dg_wer, "Groq": gq_wer, "Whisper": wh_wer}
    best_model = min(wers, key=wers.get)
    
    improvement = "Baseline is best"
    if dg_wer > 0:
        if gq_wer < dg_wer:
            improvement = f"Groq improved over Deepgram by {((dg_wer - gq_wer)/dg_wer)*100:.1f}%"
        elif wh_wer < dg_wer:
            improvement = f"Whisper improved over Deepgram by {((dg_wer - wh_wer)/dg_wer)*100:.1f}%"

    # Append to CSV
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            new_audio_name,
            ground_truth,
            dg_wer, dg_lat,
            gq_wer, gq_lat,
            wh_wer, wh_lat,
            best_model,
            improvement
        ])
    
    return dest_audio_path
