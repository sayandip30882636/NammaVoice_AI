import os
import random
# pyrefly: ignore [missing-import]
import soundfile as sf
# pyrefly: ignore [missing-import]
from datasets import load_dataset

def fetch_dataset_samples(dataset_name="fleurs", language="hi_in", num_samples=5):
    """
    Fetches a small number of random samples from a specified Hugging Face dataset.
    Supported: 'fleurs' (google/fleurs), 'kathbath' (AI4Bharat/Kathbath)
    """
    samples = []
    
    try:
        if dataset_name == "fleurs":
            # google/fleurs uses language codes like hi_in, kn_in
            ds = load_dataset("google/fleurs", language, split="test", streaming=True, trust_remote_code=True)
        elif dataset_name == "kathbath":
            # AI4Bharat/Kathbath uses language codes like hi, kn
            lang_code = language.split("_")[0] if "_" in language else language
            ds = load_dataset("AI4Bharat/Kathbath", lang_code, split="test", streaming=True, trust_remote_code=True)
        else:
            return {"success": False, "error": f"Dataset {dataset_name} not supported."}

        # Take random samples from the streaming dataset
        # Since it's streaming, we'll skip a random number of items first
        iter_ds = iter(ds)
        skip = random.randint(0, 50)
        for _ in range(skip):
            next(iter_ds, None)
            
        count = 0
        while count < num_samples:
            sample = next(iter_ds, None)
            if not sample:
                break
                
            # Extract audio and transcription
            # fleurs: {'audio': {'array': ..., 'sampling_rate': ...}, 'transcription': ...}
            # kathbath: {'audio': {'array': ..., 'sampling_rate': ...}, 'sentence': ...}
            
            audio_array = sample["audio"]["array"]
            sampling_rate = sample["audio"]["sampling_rate"]
            transcript = sample.get("transcription") or sample.get("sentence") or sample.get("text")
            
            if not transcript:
                continue
                
            # Save audio to a temporary file for the ASR engines to process
            temp_dir = "outputs/dataset_samples"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"sample_{count}.wav")
            sf.write(temp_path, audio_array, sampling_rate)
            
            samples.append({
                "audio_path": temp_path,
                "ground_truth": transcript,
                "metadata": {
                    "dataset": dataset_name,
                    "language": language,
                    "sampling_rate": sampling_rate
                }
            })
            count += 1
            
        return {"success": True, "samples": samples}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test fetch
    print("Testing dataset fetch...")
    res = fetch_dataset_samples(num_samples=2)
    if res["success"]:
        for i, s in enumerate(res["samples"]):
            print(f"Sample {i}: {s['ground_truth'][:50]}... Path: {s['audio_path']}")
    else:
        print(f"Error: {res['error']}")
