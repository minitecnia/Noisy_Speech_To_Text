import warnings
import vosk
import pyaudio
import json

warnings.filterwarnings('ignore')

# https://alphacephei.com/vosk/models
# Download model to PC, extract the files 
# and save them in local directory
# Set the model path
model_path = "vosk-model-en-us-0.42-gigaspeech"
model_path = "vosk-model-small-es-0.42"

def listdevices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print (p.get_device_info_by_index(i))

def loadmodel(model, rate=16000):
    rec = vosk.KaldiRecognizer(model, rate)
    return rec

def trans_file(modelo, fichero, idioma='es'):
    result = modelo.transcribe(fichero, language= idioma)
    return result

def transcribe(stream, recognizer, chunks=4096):
    output_file = "vosk_text.txt"
    with open(output_file, "w") as output_file:
        print("Listening for speech. Say 'Termina' to stop.")
        # Start streaming and recognize speech
        while True:
            data = stream.read(chunks)#read in chunks of 4096 bytes
            if recognizer.AcceptWaveform(data):#accept waveform of input voice
                # Parse the JSON result and get the recognized text
                result = json.loads(recognizer.Result())
                recognized_text = result['text']
            
                # Write recognized text to the file
                output_file.write(recognized_text + "\n")
                print(recognized_text)
            
                # Check for the termination keyword
                if "roller" in recognized_text.lower():
                    print("Termination keyword detected. Stopping...")
                    break
    return stream

def listen(channels=1, rate=16000, frames_buffer=8192, inputdev=2):
    # Instantiate the audio module
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, 
                    channels=channels,
                    rate=rate,
                    input=True,
                    input_device_index = inputdev,
                    frames_per_buffer=frames_buffer)
    return stream, p

def close(stream, p):
    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PyAudio object
    p.terminate()

def vosk_start(model):
    modelo = vosk.Model(model)
    rec = loadmodel(modelo)
    stream, p = listen()
    transcribe(stream, rec)


if __name__ == "__main__":

    # Initialize the model with model-path
    modelo = vosk.Model(model_path)
    chunks = 4096
    # Create a recognizer
    reco = vosk.KaldiRecognizer(modelo, 16000)

    # Open the stream
    stream, p = listen()
    # Specify the path for the output text file
    output_file = "recognized_text.txt"

    transcribe(stream, reco, chunks)

    close(stream, p)

