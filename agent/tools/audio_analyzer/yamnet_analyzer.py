import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
import os
from typing import List, Tuple, Dict

# --- Custom Logging Function ---
# You can easily turn this off or redirect its output.
_ENABLE_DEBUG_PRINTS = False  # Set to False to disable all custom debug prints


def custom_logger(message: str, level: str = "INFO"):
    """
    A custom logging function to control print statements.
    Set _ENABLE_DEBUG_PRINTS to False to suppress all messages.
    """
    if _ENABLE_DEBUG_PRINTS:
        # For a real application, you'd use Python's 'logging' module here
        # logging.getLogger(__name__).log(level, message)
        print(f"[{level}] {message}")


class YAMNetAudioAnalyzer:
    def __init__(self, model_url: str = "https://tfhub.dev/google/yamnet/1"):
        custom_logger("📥 Loading YAMNet model...")
        self.model = hub.load(model_url)
        self.classes = self._load_class_map()
        custom_logger(f"✅ Model loaded with {len(self.classes)} classes")

    def _load_class_map(self) -> List[str]:
        """Loads the YAMNet class map from a CSV file."""
        class_map_path = tf.keras.utils.get_file(
            "yamnet_class_map.csv",
            "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv",
        )
        with open(class_map_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[1:]
        return [line.split(",")[2].strip().strip('"') for line in lines]

    def analyze_file(self, filepath: str) -> List[Tuple[str, float]]:
        """
        Analyzes a single audio file using YAMNet.
        Returns a list of tuples, where each tuple contains (class_name, score).
        Uses custom_logger for controlled printing.
        """
        waveform, sr = librosa.load(filepath, sr=16000)
        if waveform.ndim > 1:
            waveform = librosa.to_mono(waveform)

        scores, embeddings, spectrogram = self.model(
            tf.constant(waveform, dtype=tf.float32)
        )
        mean_scores = tf.reduce_mean(scores, axis=0).numpy()

        top_classes_indices = np.argsort(mean_scores)[-3:][::-1]
        detailed_results = [
            (self.classes[i], mean_scores[i]) for i in top_classes_indices
        ]

        custom_logger(f"🔎 Results for {os.path.basename(filepath)}:")
        for clase, score in detailed_results:
            custom_logger(f"   → {clase}: {score:.3f}")
        custom_logger("")

        return detailed_results

    def analyze_directory(self, folder_path: str) -> List[List[Tuple[str, float]]]:
        """
        Analyses all .wav files in the given directory.
        Returns a list of lists of detailed analysis results for each file.
        Uses custom_logger for controlled printing.
        """
        all_files_results = []
        custom_logger(f" Initiating directory analysis: {folder_path}")

        if not os.path.exists(folder_path):
            custom_logger(
                f"   Warning: Directory '{folder_path}' does not exist. Returning empty results.",
                level="WARN",
            )
            return []

        for archivo in os.listdir(folder_path):
            if archivo.endswith(".wav"):
                full_filepath = os.path.join(folder_path, archivo)
                detailed_file_result = self.analyze_file(full_filepath)
                all_files_results.append(detailed_file_result)

        custom_logger(f" Directory analysis completed.")
        return all_files_results
