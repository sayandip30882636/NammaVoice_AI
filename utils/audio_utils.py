import os
import numpy as np
import soundfile as sf
import plotly.graph_objects as go
from scipy import signal

def load_audio_file(filepath):
    """
    Loads an audio file and returns the sample rate, duration, and audio array.
    """
    data, sample_rate = sf.read(filepath)
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    duration = len(data) / sample_rate
    return data, sample_rate, duration

def estimate_snr_and_noise(audio_data, sample_rate):
    """
    Estimates the Signal-to-Noise Ratio (SNR) in dB and classifies the noise level.
    Uses the quietest segments (lowest 10% energy frames) to estimate noise floor.
    """
    if len(audio_data) == 0:
        return 0, "Unknown"
    
    # Calculate frame energies (frame size ~ 25ms)
    frame_size = int(0.025 * sample_rate)
    hop_size = int(0.010 * sample_rate)
    
    if len(audio_data) < frame_size:
        return 30.0, "Low"
        
    frames = [audio_data[i:i+frame_size] for i in range(0, len(audio_data)-frame_size, hop_size)]
    frame_energies = np.array([np.sum(f**2) / frame_size for f in frames])
    
    # Avoid zero energies
    frame_energies = np.clip(frame_energies, 1e-10, None)
    
    # Noise floor is the average of the lowest 10% energy frames (representing silences)
    sorted_energies = np.sort(frame_energies)
    noise_idx = max(1, int(len(sorted_energies) * 0.10))
    noise_floor_energy = np.mean(sorted_energies[:noise_idx])
    
    # Signal energy is the average of the highest 20% energy frames (representing active speech)
    signal_idx = max(1, int(len(sorted_energies) * 0.20))
    signal_energy = np.mean(sorted_energies[-signal_idx:])
    
    snr_db = 10 * np.log10(signal_energy / noise_floor_energy)
    
    # Clamp SNR to realistic bounds
    snr_db = max(0.0, min(50.0, snr_db))
    
    # Classify noise level
    if snr_db >= 30:
        noise_level = "Low (Quiet Room)"
    elif snr_db >= 18:
        noise_level = "Medium (Moderate/Ambient Noise)"
    else:
        noise_level = "High (Heavy Noise/Traffic)"
        
    return round(snr_db, 1), noise_level

def create_waveform_plotly(audio_data, sample_rate):
    """
    Generates a stunning interactive Plotly Waveform chart.
    Optimizes rendering by downsampling if the audio is long.
    """
    duration = len(audio_data) / sample_rate
    times = np.linspace(0, duration, len(audio_data))
    
    # Downsample for smooth plotting (max 4000 points)
    max_pts = 4000
    if len(audio_data) > max_pts:
        step = len(audio_data) // max_pts
        times = times[::step]
        audio_data = audio_data[::step]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=audio_data,
        mode='lines',
        name='Waveform',
        line=dict(color='#00F2FE', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.08)'
    ))
    
    fig.update_layout(
        title=dict(text="Audio Waveform (Amplitude vs Time)", font=dict(color="#FFFFFF", size=14)),
        xaxis=dict(title="Time (seconds)", color="#8E9AA6", gridcolor="rgba(255, 255, 255, 0.05)"),
        yaxis=dict(title="Amplitude", color="#8E9AA6", gridcolor="rgba(255, 255, 255, 0.05)", range=[-1.1, 1.1]),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=220,
        showlegend=False
    )
    return fig

def create_spectrogram_plotly(audio_data, sample_rate):
    """
    Generates an advanced interactive spectrogram plot using Short-Time Fourier Transform (STFT).
    """
    # Calculate spectrogram
    frequencies, times, spectrogram = signal.spectrogram(
        audio_data, 
        fs=sample_rate, 
        nperseg=int(0.02 * sample_rate),  # 20ms window
        noverlap=int(0.01 * sample_rate)  # 10ms overlap
    )
    
    # Convert spectrogram to log scale (dB)
    spectrogram_db = 10 * np.log10(spectrogram + 1e-10)
    
    # Downsample time/freq bins for smooth rendering
    if len(times) > 300:
        step_t = len(times) // 300
        times = times[::step_t]
        spectrogram_db = spectrogram_db[:, ::step_t]
    if len(frequencies) > 150:
        step_f = len(frequencies) // 150
        frequencies = frequencies[::step_f]
        spectrogram_db = spectrogram_db[::step_f, :]
        
    fig = go.Figure(data=go.Heatmap(
        z=spectrogram_db,
        x=times,
        y=frequencies,
        colorscale='Viridis',
        colorbar=dict(title="dB", titlefont=dict(color="#8E9AA6"), tickfont=dict(color="#8E9AA6")),
    ))
    
    fig.update_layout(
        title=dict(text="Spectrogram (Frequency vs Time)", font=dict(color="#FFFFFF", size=14)),
        xaxis=dict(title="Time (seconds)", color="#8E9AA6", gridcolor="rgba(255, 255, 255, 0.05)"),
        yaxis=dict(title="Frequency (Hz)", color="#8E9AA6", gridcolor="rgba(255, 255, 255, 0.05)", range=[0, 8000]),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=220
    )
    return fig
