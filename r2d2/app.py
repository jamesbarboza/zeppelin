
import vosk
import pyaudio
import json

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)

model_path = "vosk-model-small-en-us-0.15"
model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, 16000)


while True:
    data = stream.read(4096, exception_on_overflow=False)
    _text = ""
    if rec.AcceptWaveform(data):
        result = rec.Result()
        result = json.loads(result)

        _text = result["text"]
        print(_text)


        # get a response here


        # add integration
    else:
        partial_result = rec.PartialResult()
        partial_result = json.loads(partial_result)
        _text = partial_result["partial"]
    