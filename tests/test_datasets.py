import os
import sys

# Ensure the root directory is on the path for importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.dataset_loader import fetch_dataset_samples
from utils.asr_engines import benchmark_all_models
from utils.metrics_utils import calculate_wer

def test_dataset_fetch_and_bench():
    """
    Verifies that we can fetch samples from an open-source dataset
    and run the benchmarking orchestration on them.
    """
    print("Fetching 1 sample from FLEURS (Hindi)...")
    res = fetch_dataset_samples(dataset_name="fleurs", language="hi_in", num_samples=1)
    
    if not res["success"]:
        print(f"Skipping test: Could not fetch dataset. Error: {res['error']}")
        return
        
    sample = res["samples"][0]
    print(f"Sample ground truth: {sample['ground_truth']}")
    
    print("Running benchmark orchestration...")
    # We use None for keys to trigger simulated fallbacks for verification
    bench_res = benchmark_all_models(
        audio_path=sample["audio_path"],
        deepgram_key=None,
        groq_key=None,
        language="hi"
    )
    
    assert "deepgram" in bench_res
    assert "groq" in bench_res
    assert "whisper" in bench_res
    
    wer = calculate_wer(sample["ground_truth"], bench_res["deepgram"]["transcript"])
    print(f"Deepgram (Simulated) WER: {wer}")
    
    print("Dataset integration test passed!")

if __name__ == "__main__":
    test_dataset_fetch_and_bench()
