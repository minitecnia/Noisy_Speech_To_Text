# pip install faster-whisper
from faster_whisper import WhisperModel
import os
import sys


os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

model_size = "small"

# Run on GPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")
# or run on GPU with INT8 FP16
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

def loadmodel(model_size, device='cpu', type='int8'):
    rec = WhisperModel(model_size, device=device, compute_type=type)
    return rec

def segmentos(segmentos):
    for segment in segmentos:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

def transcribe(modelo, fichero, beam_size=5):
    segments, info = modelo.transcribe(fichero, beam_size=beam_size, language='en')
    return segments, info

if __name__=='__main__':

    #fichero = sys.argv[1]
    #PORT = sys.argv[2]

    fichero = "2-3B-ENG-NS_cutted.wav"
    fichero = "Apollo_11_launch_day_communication_relayed_through_Canary_Station.wav"
    
    model = loadmodel(model_size)
    segments, info = transcribe(model, fichero)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    
    segmentos(segments)

