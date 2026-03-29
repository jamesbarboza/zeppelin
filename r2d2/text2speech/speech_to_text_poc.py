import vosk
import pyaudio
import json

model_path = "vosk-model-small-en-us-0.15"

model = vosk.Model(model_path)


rec = vosk.KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)

while True:
    data = stream.read(4096, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result = rec.Result()
        print(result)
    else:
        partial_result = rec.PartialResult()
        print(partial_result)
