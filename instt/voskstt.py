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


def loadmodel(model, rate=16000):
    rec = vosk.KaldiRecognizer(model, rate)
    return rec

def trans_file(modelo, fichero, idioma='es'):
    result = modelo.transcribe(fichero, language= idioma)
    return result

def transcribe(stream, recognizer, ):
    output_file = "vosk_text.txt"
    with open(output_file, "w") as output_file:
        print("Listening for speech. Say 'Termina' to stop.")
        # Start streaming and recognize speech
        while True:
            data = stream.read(4096)#read in chunks of 4096 bytes
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

    reference = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc efficitur dui sapien, vitae consequat diam vulputate eget. Quisque mollis dui varius mi hendrerit blandit. In pretium consectetur erat, nec pellentesque nunc pharetra vitae. Morbi tincidunt, velit at rhoncus finibus, diam justo pellentesque felis, vitae congue velit libero sed dolor. Sed condimentum venenatis volutpat. Ut tincidunt mauris vel leo vulputate, in elementum neque viverra. Morbi tincidunt felis diam, sit amet tincidunt risus vulputate at. Vivamus at fringilla massa. Sed iaculis, leo ac lacinia malesuada, orci ex pretium dolor, non fringilla orci est non metus. Praesent tempus egestas lectus at dictum. Donec sit amet ornare felis. Donec libero dolor, fermentum et tortor porta, molestie tempus lorem. Morbi sit amet erat vel quam pretium dictum. Donec lacinia, turpis cursus ornare ultrices, ligula arcu tincidunt lacus, ac dignissim erat mauris ut ex"
    reference = 'La idea de emprender me rondaba por la cabeza desde mi etapa universitaria, cuando estuve a punto de crear una empresa de diseño de joyas con un compañero. Al terminar mis estudios, encontré trabajo en el sector de la comunicación. Aunque seguía con mi sueño en mente, no me atrevía a dar el salto y montar mi agencia. Pero varios años después, con un dinero que me prestó un familiar, monté Pide la Luna, una agencia especializada en el diseño, la producción y la gestión de eventos empresariales e institucionales. Como me daba miedo que la agencia no funcionara bien, durante un año estuve compaginando mi actividad como autónoma con la de relaciones públicas en un hotel. Montar un negocio sin disponer de muchos recursos es un poco temerario, pero te empuja a pelear por sacar adelante tu proyecto, a estar siempre alerta buscando acuerdos de intercambios, colaboraciones…'


    # Initialize the model with model-path
    modelo = vosk.Model(model_path)
    # Create a recognizer
    rec = vosk.KaldiRecognizer(modelo, 16000)

    #for i in range(p.get_device_count()):
    #    print (p.get_device_info_by_index(i))

    # Open the stream
    stream, p = listen()
    # Specify the path for the output text file
    output_file = "recognized_text.txt"

    transcribe(stream, rec, )

    close(stream, p)

