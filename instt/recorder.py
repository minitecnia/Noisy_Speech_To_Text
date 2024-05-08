# Thanks to Kevin Ponce
# https://kevinponce.com/blog/python/record-audio-on-detection/

import pyaudio
import wave
import audioop
import math
from collections import deque

# Silence limit in seconds. The max ammount of seconds where
# only silence is recorded. When this time passes the
# recording finishes and the file is delivered.

# The silence threshold intensity that defines silence
# and noise signal (an int. lower than THRESHOLD is silence).

# Previous audio (in seconds) to prepend. When noise
# is detected, how much of previously recorded audio is
# prepended. This helps to prevent chopping the beggining
# of the phrase.

def record_on_detect(file_name, silence_limit=1, silence_threshold=1800, chunk=512, rate=22050, prev_audio=1.5):
    CHANNELS = 1
    FORMAT = pyaudio.paInt16

    p = pyaudio.PyAudio()
    # Open stream
    stream = p.open(format=p.get_format_from_width(2),
                  channels=CHANNELS,
                  rate=rate,
                  input=True,
                  output=False,
                  frames_per_buffer=chunk)

    listen = True
    started = False
    rel = rate/chunk
    frames = []

    prev_audio = deque(maxlen=int(prev_audio * rel))
    slid_window = deque(maxlen=int(silence_limit * rel))

    while listen:
        data = stream.read(chunk)
        slid_window.append(math.sqrt(abs(audioop.avg(data, 4))))

        if(sum([x > silence_threshold for x in slid_window]) > 0):
            if(not started):
                print("Starting record.")
                started = True
        elif (started is True):
            started = False
            listen = False
            prev_audio = deque(maxlen=int(0.5 * rel))

        if (started is True):
            frames.append(data)
        else:
            prev_audio.append(data)

    # Close stream and terminate
    stream.stop_stream()
    stream.close()
    p.terminate()


    wf = wave.open(f'{file_name}.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(rate)

    wf.writeframes(b''.join(list(prev_audio)))
    wf.writeframes(b''.join(frames))
    wf.close()

class Recorder:

    def __init__(self):

        self.stream = []
        self.frames = []
        self.channels = 1
        self.frecuencia = 16000
        self.formato = pyaudio.paInt16
        self.p = None
        self.chunk = 1024
        self.stop_threads = True
        self.filename = 'grabacion'

    def init_(self, canales=1, frecuencia=16000, entrada=True, chunk=512):
        '''
        Inicia la grabación de un audio

        Returns None.
        '''
        self.stop_threads = False
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=canales, rate=frecuencia, input=entrada, output=False, frames_per_buffer=chunk)
        return

    def stop_(self):
        '''
        Detiene la grabación de un audio

        Returns None.
        '''
        self.stop_threads = True
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
    
    def get_audio(self, stop):
        while True:
            
            if stop():
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
                break
            else:
                data = self.stream.read(self.chunk)
                self.frames.append(data)
    
    def save_audio(self, path_grabacion):
        '''
        Guarda el audio en un archivo

        Returns None.
        '''
        wf = wave.open(path_grabacion, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.formato))
        wf.setframerate(self.frecuencia)
        wf.writeframes(b"".join(self.frames))
        wf.close()
        
        self.frames = []

    def record_on_detect(file_name, silence_limit=1, silence_threshold=1800, chunk=512, rate=22050, prev_audio=1.5):
        CHANNELS = 1
        FORMAT = pyaudio.paInt16

        p = pyaudio.PyAudio()
        # Open stream
        stream = p.open(format=p.get_format_from_width(2),
                  channels=CHANNELS,
                  rate=rate,
                  input=True,
                  output=False,
                  frames_per_buffer=chunk)

        listen = True
        started = False
        rel = rate/chunk
        frames = []

        prev_audio = deque(maxlen=int(prev_audio * rel))
        slid_window = deque(maxlen=int(silence_limit * rel))

        while listen:
            data = stream.read(chunk)
            slid_window.append(math.sqrt(abs(audioop.avg(data, 4))))

            if(sum([x > silence_threshold for x in slid_window]) > 0):
                if(not started):
                    print("Starting record.")
                    started = True
            elif (started is True):
                started = False
                listen = False
                prev_audio = deque(maxlen=int(0.5 * rel))

            if (started is True):
                frames.append(data)
            else:
                prev_audio.append(data)

        # Close stream and terminate
        stream.stop_stream()
        stream.close()
        p.terminate()


        wf = wave.open(f'{file_name}.wav', 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(rate)

        wf.writeframes(b''.join(list(prev_audio)))
        wf.writeframes(b''.join(frames))
        wf.close()


if __name__ == "__main__":

    recorder = Recorder()
    i=0
    while(i<10):
        recorder.record_on_detect('sample'+str(i))
        i+=1