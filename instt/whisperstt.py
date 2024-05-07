#-------------------------------------------------------------------------
# CTEET
# whisperstt; text to speech using whisper
# @Author: Francisco Jose Ochando Terreros
# @Test: 
# @Debugging: Francisco Jose Ochando Terreros
# version 0.1
#
# Transcribe ficheros .wav en un bucle utilizando whisper. El modelo por defecto es SMALL
#-------------------------------------------------------------------------

import warnings
import whisper
import os
import glob

warnings.filterwarnings('ignore')

def load(sizemodel='small'):
    model = whisper.load_model(sizemodel)
    return model

def trans_file(modelo, fichero, idioma='en'):
    result = modelo.transcribe(fichero, language= idioma)
    return result

def trans_audio(modelo, audio, idioma='es'):
    result = modelo.transcribe(audio, language= idioma)
    return result

if __name__ == "__main__":

    modelo = load('small')

    #dir = '../audiofiles/cleaned/*.wav'
    dir = '../static/audiofiles/cleaned/websdr_recording_2024-05-03T20_15_23Z_7123.0kHz.wav'
    #dir = '../audiofiles/textoC*.*'
    #dir = '../audiofiles/cleaned/spanish*.wav'


    for path in glob.glob(dir, recursive=True):
        result = trans_file(modelo, path)
        print(result["text"])