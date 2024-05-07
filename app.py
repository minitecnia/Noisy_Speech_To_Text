#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Centro de Tecnologías Emergentes del Ejército de Tierra (CTEET)
# Prueba de concepto: App para InSTT
# Created on Tue Jan 23 14:05:47 2024
# @Author: Francisco Jose Ochando Terreros
# @Test: Antonio Mejías Vello, Alejandro Gomez Sierra 
# @Debugging: Francisco Jose Ochando Terreros
#-------------------------------------------------------------------------

from flask import Flask, render_template, request
import logging
import warnings
from werkzeug.utils import secure_filename
import threading
import os
import time
from instt import whisperstt as stt
from instt import voskstt as vos
from instt import assistant
from instt.tts import tts
from instt.recorder import Recorder
#from instt.noisereducer import reducer
#from flask_mysqldb import MySQL


# Settings the warnings to be ignored 
warnings.filterwarnings('ignore')

logging.basicConfig(filename='instt.log', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
# Carpeta de subida
app.config['UPLOAD_FOLDER'] = '.\static\\audiofiles\\'
app.config['DOWNLOAD_FOLDER'] = '\static\\audiofiles\\'
app.config['TRANSCRIPTION_FOLDER'] = '..\static\\audiofiles\\transcription\\'
app.config['STT_FOLDER'] = '.\instt\\'
modelo = stt.load()
stream = []

# Classes ----------------------------------------------------------------

@app.route('/')
def landing():
    #return redirect(url_for('login'))
    return render_template('landing.html')

@app.route('/instt')
def instt():
    respuesta = "Bienvenido a la aplicacion de transcripción de audio a texto de Iberian."
    tts.playvoice(respuesta, 'es')
    return render_template('index.html')

@app.route('/index', methods=['GET','POST'])
def index():
    basedir = os.path.abspath(os.path.dirname(__file__))
    path1 = "./static/audiofiles/"
    audiofile = ''
    if request.method == 'POST':
        #select = request.form.get('myfile')
        f = request.files['myfile']
        audiofile = secure_filename(f.filename)
        #stt.trans(modelo, idioma='en')
    
    path = os.path.join(basedir, app.config['DOWNLOAD_FOLDER']+audiofile)
    #dirs = os.listdir(path)
    #files = []
    #for dir in dirs:
    #    files.append({'name': dir})

    print(path)
    
    return render_template('index.html', message= 'Audio file', file= path1 + audiofile)

@app.route('/audio', methods=['GET','POST'])
def audio():
    if request.method == 'POST':
        f = request.files['myfile']
        audiofile = secure_filename(f.filename)
        #print(audiofile)

    return render_template('audio.html', message= 'Audio file', file= "/audiofiles/" + audiofile)

@app.route('/advanced', methods=['GET'])
def advanced():
    grabar = request.args.get('grabar') # Read the url to get arguments from there
    if grabar == 'True':
        def vosk_start(model):
            modelo = vos.Model(model)
            rec = vos.loadmodel(modelo)
            stream, p = vos.listen()
            output_file = "vosk_text.txt"
            transcribe(stream, rec, output_file)
            #vos.close(stream, p)

        print('Arranca Vosk')
        threading.Thread(target = vosk_start)
        return render_template('advanced.html', segments='Segmentos de audio')
    else:
        print('Para Vosk')
        return render_template('advanced.html', segments='No hay segmentos')

@app.route('/chat', methods=['GET','POST'])
def chat():
    prompt = 'Hola TARS!'
    segmentos = 'No hay segmentos'
    if request.method == 'POST':
        prompt = request.form.get("prompt", "Hola TARS!")
        respuesta = assistant.Completion(prompt)
        tts.playvoice(respuesta, 'es')
        return render_template('Chat.html', prompt=prompt, transcription_text = str(respuesta), segments=segmentos)
    else:
        return render_template('Chat.html', prompt=prompt, transcription_text = "Waiting prompts.", segments=segmentos)
    #return render_template('Chat.html')

@app.route('/config', methods=['GET'])
def config():
    return render_template('configuration.html')

@app.route('/transcribe', methods=['GET'])
def transcribe():
    audiofile = ''
    transcription = 'Aqui la transcripción'
    #return redirect(url_for('audio'))
    return render_template('audio.html', message= 'Audio file', file= "/static/" + audiofile, transcription_text=transcription)

@app.route('/recording', methods=['GET'])
def recording():
    grabar = request.args.get('grabar') # Read the url to get arguments from there
    if grabar == 'True':
        print ('start recording')
        grabadora.init_()
        grabadora.filename = time.strftime("%Y%m%d-%H%M%S")
        threading.Thread(target = grabadora.get_audio, args =(lambda : grabadora.stop_threads, )).start()
        
        return render_template('index.html', info = 'Grabando audio')
    else:
        print ('stop recording')
        grabadora.stop_threads = True
        filename = secure_filename(grabadora.filename + '_audio.wav')
        grabadora.save_audio(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
        return render_template('index.html', info = 'Guardando audio')

if __name__ == '__main__':
    #Asistente = Assistant()
    grabadora = Recorder()
    app.run(host="0.0.0.0", port=5000, debug=True)