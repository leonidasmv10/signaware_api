import os
from pyannote.audio import Pipeline


class SpeakerDiarizer:
    def __init__(
        self,
        audio_folder: str,
        model_name: str = "pyannote/speaker-diarization-3.1",
        verbose: bool = False,
    ):
        self.audio_folder = audio_folder
        self.verbose = verbose
        self.pipeline = Pipeline.from_pretrained(model_name)

    def process_audio_files(self):
        results = {}
        for file in os.listdir(self.audio_folder):
            if file.endswith(".wav"):
                audio_path = os.path.join(self.audio_folder, file)
                segments = self.extract_segments(audio_path)
                results[file] = segments
        return results

    def extract_segments(self, audio_path: str, verbose: bool = None):
        diarization = self.pipeline(audio_path)
        segments = [
            (turn.start, turn.end, speaker)
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]

        if verbose is None:
            verbose = self.verbose

        if verbose:
            print(
                f"\n🔍 Resultados de diarización para {os.path.basename(audio_path)}:"
            )
            for start, end, speaker in segments:
                print(f"  {start:.2f}s → {end:.2f}s: {speaker}")

        return segments


# Ejemplo de uso:
# diarizer = SpeakerDiarizer(audio_folder="audio_fragments", verbose=True)
# resultados = diarizer.process_audio_files()
