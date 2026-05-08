import os
import wave
import numpy as np
import struct

def generate_sample_wav(filepath, duration=4.0, sample_rate=16000, condition="Quiet Room"):
    """
    Generates a valid mono WAV file with synthesized audio representing the specified condition.
    Uses numpy and wave to avoid external binary dependencies like ffmpeg.
    """
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Base signal: voice-like frequency range (fundamental around 120Hz-250Hz, plus harmonics)
    signal = 0.4 * np.sin(2 * np.pi * 150 * t) + 0.2 * np.sin(2 * np.pi * 300 * t) + 0.1 * np.sin(2 * np.pi * 450 * t)
    
    # Introduce amplitude modulation to simulate spoken words (pulsing)
    modulator = 0.5 * (1 + np.sin(2 * np.pi * 1.5 * t))  # 1.5 Hz modulation
    signal = signal * modulator
    
    # Apply conditions
    if condition == "Traffic Noise":
        # Add significant random noise (traffic rumble + horn-like frequencies)
        noise = np.random.normal(0, 0.25, num_samples)
        horn = 0.15 * np.sin(2 * np.pi * 800 * t) * (np.sin(2 * np.pi * 0.2 * t) > 0.5)
        signal = signal + noise + horn
    elif condition == "Phone-call Quality":
        # Narrower frequency range (telephony bandpass 300-3400Hz) and slightly higher noise
        noise = np.random.normal(0, 0.08, num_samples)
        signal = signal + noise
        # Apply a simple bandpass simulation (attenuate low and high frequencies)
        signal = np.clip(signal, -0.6, 0.6)
    elif condition == "Rushed Speech":
        # Faster modulation representing rapid phrasing
        modulator_fast = 0.5 * (1 + np.sin(2 * np.pi * 4.0 * t))
        signal = signal * modulator_fast
        noise = np.random.normal(0, 0.02, num_samples)
        signal = signal + noise
    elif condition == "Whispered Speech":
        # Faint signal dominated by white noise (unvoiced sounds)
        noise = np.random.normal(0, 0.12, num_samples)
        signal = 0.05 * signal + noise
    else:  # Quiet Room
        # Clean signal with minor noise
        noise = np.random.normal(0, 0.005, num_samples)
        signal = signal + noise

    # Normalize to fit in 16-bit integer range (-32768 to 32767)
    signal = signal / np.max(np.abs(signal)) * 0.9
    signal_int = (signal * 32767).astype(np.int16)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Write WAV file
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Pack raw data
        data = struct.pack('<' + 'h' * len(signal_int), *signal_int)
        wav_file.writeframes(data)

def ensure_all_preloaded_samples(target_dir):
    """
    Ensures all preloaded audio sample files exist, generating them if necessary.
    """
    from utils.configs import PRELOADED_SAMPLES
    os.makedirs(target_dir, exist_ok=True)
    
    for key, info in PRELOADED_SAMPLES.items():
        filepath = os.path.join(target_dir, info["filename"])
        if not os.path.exists(filepath):
            generate_sample_wav(
                filepath=filepath,
                duration=5.0 if "sample_2" in key or "sample_3" in key else 4.0,
                condition=info["condition"]
            )
            print(f"Generated preloaded sample audio: {info['filename']}")
