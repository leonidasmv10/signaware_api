import os
import subprocess


class DemucsSeparator:
    def __init__(
        self,
        output_dir: str = "demucs_output",
        stems: str = "vocals",
        verbose: bool = False,
    ):
        self.output_dir = output_dir
        self.stems = stems
        self.verbose = verbose

    def separate(self, input_audio: str):
        cmd = [
            "demucs",
            input_audio,
            "--two-stems",
            self.stems,
            "--out",
            self.output_dir,
        ]

        if self.verbose:
            print(f"🎧 Separando pistas con Demucs para: {input_audio}...")
        subprocess.run(cmd, check=True)

        track_name = os.path.splitext(os.path.basename(input_audio))[0]
        path_vocals = os.path.join(
            self.output_dir, "htdemucs", track_name, f"{self.stems}.wav"
        )

        if self.verbose:
            print(f"✅ '{self.stems}' separada guardada en: {path_vocals}")

        return path_vocals


# Ejemplo de uso:
# separator = DemucsSeparator(verbose=True)
# ruta_vocals = separator.separate("audio_fragments/fragmento_20250620_181110.wav")
