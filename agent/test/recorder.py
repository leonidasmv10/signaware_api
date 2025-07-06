import sounddevice as sd
import soundfile as sf
import os
import datetime

class AudioRecorder:
    def __init__(self, duration=3, samplerate=16000, channels=1, save_dir="audio_fragments"):
        self.duration = duration
        self.samplerate = samplerate
        self.channels = channels
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def _generate_filename(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.save_dir, f"fragmento_{timestamp}.wav")

    def record_fragment(self):
        print("🎙️ Grabando...")
        audio = sd.rec(int(self.duration * self.samplerate), samplerate=self.samplerate, channels=self.channels)
        sd.wait()
        filename = self._generate_filename()
        sf.write(filename, audio, self.samplerate)
        print(f"✅ Guardado: {filename}")
        print(f"DEBUG: Returning filename: {filename} (Type: {type(filename)})")
        print(f"DEBUG: Returning audio: (Type: {type(audio)}, Shape: {audio.shape if hasattr(audio, 'shape') else 'N/A'})")
        return filename, audio

    def record_loop(self, n=5):
        for i in range(n):
            print(f"\n🔄 Fragmento {i + 1} de {n}")
            self.record_fragment()
