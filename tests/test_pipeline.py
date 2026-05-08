import os
import sys
import numpy as np

# Ensure the root directory is on the path for importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.metrics_utils import (
    calculate_wer, 
    calculate_cer, 
    extract_localities_fuzzy, 
    calculate_entity_accuracy
)
from utils.audio_utils import estimate_snr_and_noise

def test_wer_cer_calculation():
    """
    Verifies that WER and CER metrics are computed correctly.
    """
    ground_truth = "Hi my name is Rahul"
    hypothesis_perfect = "hi my name is rahul"
    hypothesis_error = "hi my name is raj"
    
    # Perfect match (normalized) should yield 0.0 WER and CER
    assert calculate_wer(ground_truth, hypothesis_perfect) == 0.0
    assert calculate_cer(ground_truth, hypothesis_perfect) == 0.0
    
    # Substitution error
    wer_err = calculate_wer(ground_truth, hypothesis_error)
    assert wer_err > 0.0
    assert wer_err <= 1.0

def test_locality_fuzzy_extraction():
    """
    Verifies that the Locality Intelligence Layer fuzzy matches misspelled
    or code-switched Bangalore locality strings correctly.
    """
    # Misspelled Koramangala
    text_1 = "I am staying in Koramangal near the main street"
    detected_1 = extract_localities_fuzzy(text_1)
    assert "Koramangala" in detected_1
    
    # Two-word and lowercase matching
    text_2 = "please deliver the food to silk board signal"
    detected_2 = extract_localities_fuzzy(text_2)
    assert "Silk Board" in detected_2
    
    # Empty or unrelated text should return no localities
    text_3 = "hello this is some general text without any location names"
    detected_3 = extract_localities_fuzzy(text_3)
    assert len(detected_3) == 0

def test_entity_accuracy():
    """
    Verifies that F1 Entity Accuracy behaves correctly.
    """
    expected = ["Koramangala", "Indiranagar"]
    detected_perfect = ["Koramangala", "Indiranagar"]
    detected_partial = ["Koramangala"]
    
    assert calculate_entity_accuracy(expected, detected_perfect) == 100.0
    assert calculate_entity_accuracy(expected, detected_partial) == 66.7  # TP=1, FP=0, FN=1 -> Prec=1.0, Rec=0.5 -> F1=0.667

def test_snr_estimation():
    """
    Verifies that SNR estimation functions correctly with synthetic audio patterns.
    """
    # Create clean synthetic conversational signal (active first half, silent second half)
    sample_rate = 16000
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)
    signal[8000:] = 0.0  # Introduce silence for the second half
    
    noise_clean = np.random.normal(0, 0.001, sample_rate)
    clean_audio = signal + noise_clean
    
    snr_clean, level_clean = estimate_snr_and_noise(clean_audio, sample_rate)
    assert snr_clean > 20.0
    
    # Create noisy synthetic signal (low SNR)
    noise_heavy = np.random.normal(0, 0.1, sample_rate)
    noisy_audio = signal + noise_heavy
    
    snr_noisy, level_noisy = estimate_snr_and_noise(noisy_audio, sample_rate)
    assert snr_noisy < snr_clean



if __name__ == "__main__":
    print("Running tests locally...")
    test_wer_cer_calculation()
    test_locality_fuzzy_extraction()
    test_entity_accuracy()
    test_snr_estimation()
    print("All tests passed successfully!")
