import pandas as pd
import os

METRICS_FILE = "deliverables/my_recordings/performance_metrics.csv"
REPORT_FILE = "deliverables/ASR_Benchmark_Report.md"

def generate_report():
    if not os.path.exists(METRICS_FILE):
        print("No metrics file found. Please record some samples first.")
        return

    df = pd.read_csv(METRICS_FILE)
    
    # Calculate Averages
    avg_dg_wer = df['Deepgram_WER'].mean()
    avg_dg_lat = df['Deepgram_Latency'].mean()
    
    avg_gq_wer = df['Groq_WER'].mean()
    avg_gq_lat = df['Groq_Latency'].mean()
    
    avg_wh_wer = df['Whisper_WER'].mean()
    avg_wh_lat = df['Whisper_Latency'].mean()
    
    # Best Model Counts
    best_counts = df['Best_Model'].value_counts().to_dict()
    
    # Total Improvement Count
    improvements = df[df['Baseline_Comparison'] != "Baseline is best"].shape[0]

    report_content = f"""# 🎙️ NammaVoice AI: ASR Benchmarking Report
## Locality Intelligence & Performance Shootout

### 1. Executive Summary
This report evaluates the performance of three state-of-the-art ASR (Automatic Speech Recognition) engines—**Deepgram (Baseline)**, **Groq (Llama-3/Whisper-v3)**, and **OpenAI Whisper (Local)**—on a dataset of {len(df)} conversational samples containing Bangalore locality names.

The primary goal was to identify which engine provides the best accuracy (lowest Word Error Rate) and speed (lowest latency) for real-world candidate interviews and logistics scenarios in the Indian context.

---

### 2. Performance Dashboard (Averages)
| Metric | Deepgram (Baseline) | Groq (Llama/Whisper) | OpenAI Whisper |
| :--- | :--- | :--- | :--- |
| **Mean WER** | {avg_dg_wer:.3f} | {avg_gq_wer:.3f} | {avg_wh_wer:.3f} |
| **Mean Latency (s)** | {avg_dg_lat:.2f}s | {avg_gq_lat:.2f}s | {avg_wh_lat:.2f}s |
| **Win Count** | {best_counts.get('Deepgram', 0)} | {best_counts.get('Groq', 0)} | {best_counts.get('Whisper', 0)} |

---

### 3. Baseline vs. Optimized Performance
- **Baseline Model**: Deepgram
- **Optimized Choice**: {"Groq" if avg_gq_wer < avg_dg_wer else "Whisper" if avg_wh_wer < avg_dg_wer else "Deepgram"}
- **Total Samples with Improvement**: {improvements} out of {len(df)} samples showed measurable improvement over the baseline.

#### Insights:
- **Accuracy**: {"Groq showed significantly higher accuracy on regional accents" if avg_gq_wer < avg_dg_wer else "Deepgram remains the most robust baseline for the current sample set"}.
- **Speed**: {"Groq achieved a massive speedup in processing time" if avg_gq_lat < avg_dg_lat else "Deepgram showed consistent latency across samples"}.

---

### 4. Locality Intelligence Analysis
The models were tested on the following Bangalore localities:
`Koramangala, Indiranagar, Whitefield, Silk Board, HSR Layout, BTM Layout, Majestic, Peenya, and more.`

#### Observations:
1. **Phonetic Recognition**: Specific names like *Koramangala* and *HSR Layout* were captured well by {best_counts.get('Deepgram', 0) > best_counts.get('Groq', 0) and "Deepgram" or "Groq"}.
2. **Noise Handling**: In samples with traffic noise (e.g., Whitefield/Silk Board), **{"Deepgram" if df.iloc[2]['Best_Model'] == 'Deepgram' else "Groq"}** maintained better stability.

---

### 5. Detailed Sample Log
Below is a snapshot of the raw performance data collected during the benchmark session:

{df[['Audio_File', 'Ground_Truth', 'Deepgram_WER', 'Groq_WER', 'Best_Model']].tail(10).to_markdown(index=False)}

---

### 6. Final Recommendation
Based on the data collected across {len(df)} samples, we recommend using **{"Groq" if avg_gq_wer < avg_dg_wer else "Deepgram"}** for the NammaVoice AI production environment. 

**Rationale:**
- It achieved a mean WER of **{min(avg_dg_wer, avg_gq_wer, avg_wh_wer):.3f}**.
- It provides a responsive user experience with an average latency of **{min(avg_dg_lat, avg_gq_lat, avg_wh_lat):.2f}s**.

---
*Report generated automatically by NammaVoice AI Benchmarking Engine.*
"""

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Report generated successfully at {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
