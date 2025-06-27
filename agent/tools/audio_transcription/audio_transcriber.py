import os
from faster_whisper import WhisperModel


class AudioTranscriber:
    def __init__(
        self,
        model_size: str = "large",
        device: str = "cuda",
        compute_type: str = "float16",
        language: str = "es",
        verbose: bool = False,
    ):
        self.verbose = verbose
        self.language = language
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_file(self, audio_path: str):
        segments, _ = self.model.transcribe(audio_path, language=self.language)
        transcript = [
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
            for segment in segments
        ]

        if self.verbose:
            print(f"📝 Transcripción de {os.path.basename(audio_path)}:")
            for seg in transcript:
                print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s]: {seg['text']}")
            print("-" * 50)

        return transcript

    def transcribe_folder(self, folder_path: str):
        results = {}
        for file in os.listdir(folder_path):
            if file.endswith(".wav"):
                audio_path = os.path.join(folder_path, file)
                transcript = self.transcribe_file(audio_path)
                results[file] = transcript
        return results


# Ejemplo de uso:
# transcriber = AudioTranscriber(verbose=True)
# resultados = transcriber.transcribe_folder("audio_fragments")
