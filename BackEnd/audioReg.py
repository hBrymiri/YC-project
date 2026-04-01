import numpy as np
from scipy.io import wavfile
import os

def generate_audio_file(filename, duration=3, person_type="unknown", sample_rate=16000):
    """
    Generate synthetic audio files for training audio recognition model.
    
    Args:
        filename: Output filename for the audio file
        duration: Duration of audio in seconds
        person_type: "known" or "unknown" to create different audio patterns
        sample_rate: Sample rate in Hz
    """
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    if person_type.lower() == "known":
        # Known people: stable, consistent frequencies
        frequency1 = 440  # A note
        frequency2 = 550  # C# note
        audio = 0.3 * np.sin(2 * np.pi * frequency1 * t)
        audio += 0.2 * np.sin(2 * np.pi * frequency2 * t)
        
    else:  # unknown
        # Unknown people: varied, random frequencies
        audio = np.zeros_like(t)
        for i in range(5):
            random_freq = np.random.randint(200, 800)
            random_amplitude = np.random.rand() * 0.2
            audio += random_amplitude * np.sin(2 * np.pi * random_freq * t)
    
    # Add slight noise
    audio += np.random.normal(0, 0.02, len(audio))
    
    # Normalize
    audio = np.int16(audio / np.max(np.abs(audio)) * 32767)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write to WAV file
    wavfile.write(filename, sample_rate, audio)
    print(f"Generated: {filename}")


def save_known_audio_file(src_path, person_name, known_root="SubDocu/KnownFolder"):
    """Copy a WAV file from src_path into a known-person folder.

    This is the core helper used by drag-and-drop frontends (or CLI scripts).
    """
    import shutil

    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")

    ext = os.path.splitext(src_path)[1].lower()
    if ext not in (".wav", ".flac", ".mp3"):
        raise ValueError("Only .wav, .flac, .mp3 audio files are supported")

    person_dir = os.path.join(known_root, person_name)
    os.makedirs(person_dir, exist_ok=True)

    dst = os.path.join(person_dir, os.path.basename(src_path))
    shutil.copy2(src_path, dst)
    print(f"Saved known audio: {dst}")
    return dst


def save_known_audio_bytes(file_bytes, filename, person_name, known_root="SubDocu/KnownFolder"):
    """Save uploaded audio bytes into known-person folder (for web upload endpoints)."""
    person_dir = os.path.join(known_root, person_name)
    os.makedirs(person_dir, exist_ok=True)

    if not filename.lower().endswith(('.wav', '.flac', '.mp3')):
        raise ValueError("Filename must end with .wav, .flac or .mp3")

    dst = os.path.join(person_dir, filename)
    with open(dst, 'wb') as f:
        f.write(file_bytes)

    print(f"Saved known audio bytes: {dst}")
    return dst


def register_dragged_known_audio(file_paths, person_name, known_root="SubDocu/KnownFolder"):
    """Process a list of local file paths (drag & drop) and save into known folder."""
    saved = []
    for p in file_paths:
        try:
            saved_path = save_known_audio_file(p, person_name, known_root=known_root)
            saved.append(saved_path)
        except Exception as e:
            print(f"Failed to save {p}: {e}")
    return saved


# Generate training datasets
if __name__ == "__main__":
    base_path = "./audio_training_data/"
    
    # Generate known people audio files
    for i in range(5):
        generate_audio_file(f"{base_path}known/person_{i}.wav", person_type="known")
    
    # Generate unknown people audio files
    for i in range(5):
        generate_audio_file(f"{base_path}unknown/person_{i}.wav", person_type="unknown")
    
    print("Audio generation complete!")