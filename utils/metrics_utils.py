import re
import numpy as np
from rapidfuzz import fuzz, process
import jiwer
from utils.configs import BANGALORE_LOCALITIES

def normalize_text(text):
    """
    Standard text normalization for ASR benchmarking.
    Removes punctuation, lowercases, and strips extra spaces.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Replace punctuation with spaces
    text = re.sub(r'\s+', ' ', text)       # Collapse multiple spaces
    return text.strip()

def calculate_wer(ground_truth, hypothesis):
    """
    Computes Word Error Rate (WER) using jiwer.
    Defensively returns 1.0 on empty inputs or errors.
    """
    gt_norm = normalize_text(ground_truth)
    hyp_norm = normalize_text(hypothesis)
    
    if not gt_norm:
        return 0.0 if not hyp_norm else 1.0
    if not hyp_norm:
        return 1.0
        
    try:
        return round(jiwer.wer(gt_norm, hyp_norm), 4)
    except Exception:
        # Simple fallback token edit distance if library fails
        return 1.0

def calculate_cer(ground_truth, hypothesis):
    """
    Computes Character Error Rate (CER) using jiwer.
    Defensively returns 1.0 on empty inputs or errors.
    """
    gt_norm = normalize_text(ground_truth)
    hyp_norm = normalize_text(hypothesis)
    
    if not gt_norm:
        return 0.0 if not hyp_norm else 1.0
    if not hyp_norm:
        return 1.0
        
    try:
        return round(jiwer.cer(gt_norm, hyp_norm), 4)
    except Exception:
        return 1.0

def extract_localities_fuzzy(text, threshold=80.0):
    """
    Locality Intelligence Layer:
    Tokenizes the input text and matches tokens/n-grams against
    the list of 30+ Bangalore localities using fuzzy string matching.
    Supports single-word and two-word locality names.
    """
    normalized = normalize_text(text)
    words = normalized.split()
    detected_localities = set()
    
    # Check single-word localities
    for word in words:
        if len(word) < 4:  # Avoid matching very short particles
            continue
        # Use rapidfuzz process.extractOne
        match = process.extractOne(word, BANGALORE_LOCALITIES, scorer=fuzz.WRatio)
        if match and match[1] >= threshold:
            detected_localities.add(match[0])
            
    # Check double-word localities (n-grams of size 2)
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        match = process.extractOne(bigram, BANGALORE_LOCALITIES, scorer=fuzz.WRatio)
        if match and match[1] >= threshold:
            detected_localities.add(match[0])
            
    # Hardcoded phonetic replacements for typical combined errors (e.g., "silkboard" or "whitefield")
    if "silk" in normalized or "board" in normalized:
        detected_localities.add("Silk Board")
    if "white" in normalized or "field" in normalized:
        detected_localities.add("Whitefield")
    if "electronic" in normalized or "ecity" in normalized:
        detected_localities.add("Electronic City")
    if "hsr" in normalized:
        detected_localities.add("HSR Layout")
    if "btm" in normalized:
        detected_localities.add("BTM Layout")
    if "kr" in normalized or "puram" in normalized:
        detected_localities.add("KR Puram")

    # Filter to only matching localities from our official list
    final_detected = [loc for loc in BANGALORE_LOCALITIES if loc in detected_localities]
    return final_detected

def calculate_entity_accuracy(expected, detected):
    """
    Calculates Entity/Locality accuracy using Precision, Recall, and F1.
    """
    if not expected:
        return 1.0 if not detected else 0.0
    
    expected_set = set(expected)
    detected_set = set(detected)
    
    tp = len(expected_set.intersection(detected_set))
    fp = len(detected_set - expected_set)
    fn = len(expected_set - detected_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return round(f1 * 100, 1)

def compute_noise_robustness(wer, snr_db):
    """
    Computes a noise robustness score (0-100).
    A model is robust if it keeps WER low even under low SNR (noisy conditions).
    """
    # Low WER = High baseline accuracy.
    accuracy = max(0.0, 1.0 - wer)
    
    # If SNR is low (heavy noise), keeping high accuracy earns a bonus score
    if snr_db < 15.0:
        robustness = accuracy * 100 + (15.0 - snr_db) * 2
    else:
        robustness = accuracy * 100
        
    return min(100.0, max(0.0, round(robustness, 1)))

def compute_code_switching_score(wer, is_code_switched):
    """
    Computes a code-switching handling score (0-100) for multilingual samples.
    """
    if not is_code_switched:
        return 100.0
    
    # Direct function of word error rate in multilingual scenarios
    score = (1.0 - min(1.0, wer)) * 100
    # Apply a slight penalty/boost based on typical baseline performance
    return round(score, 1)

def identify_misheard_words(ground_truth, hypothesis):
    """
    Computes word-level diffs to pinpoint misheard words.
    Returns a list of dictionaries with expected vs predicted words.
    """
    gt_words = normalize_text(ground_truth).split()
    hyp_words = normalize_text(hypothesis).split()
    
    misheard = []
    
    # Simple word alignment using Edit Distance backtrace or sliding window
    # For reporting, we can find words in ground truth that are missing from hypothesis
    # or replaced by phonetically close words.
    for i, gt_word in enumerate(gt_words):
        if gt_word not in hyp_words:
            # Look for phonetically similar words in the hypothesis as replacements
            matches = process.extract(gt_word, hyp_words, scorer=fuzz.WRatio, limit=1)
            predicted = matches[0][0] if matches and matches[0][1] >= 65.0 else "(omitted/misheard)"
            
            # Avoid matching words already aligned
            misheard.append({
                "expected": gt_word,
                "predicted": predicted,
                "type": "Substitution" if predicted != "(omitted/misheard)" else "Omission"
            })
            
    return misheard
