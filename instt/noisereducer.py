##-------------------------------------------------------------------------
# Centro de Tecnologías Emergentes del Ejército de Tierra (CTEET)
# Prueba de concepto: Instrucción por voz con whisper
# @Author: Francisco Jose Ochando Terreros
# @Test: Antonio Mejías Vello, Alejandro Gomez Sierra
# @Debugging: Francisco Jose Ochando Terreros
# version 0.1
#-------------------------------------------------------------------------
import wave
import io
from recorder import Record as rec
import noisereduce as nr # https://pypi.org/project/noisereduce/
import librosa
from noisereduce.generate_noise import band_limited_noise
import soundfile as sf
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write
from pydub import AudioSegment
import xml.etree.ElementTree as et

class reducer():

    def __init__(self, configfile):

        stationary, prop_decrease, hz, ms, s, fft = self.getparams(configfile)
        self.stationary = stationary
        self.prop_decrease = float(prop_decrease)
        self.freq_mask_smooth_hz = int(hz)
        self.time_mask_smooth_ms = int(ms)
        self.time_constant_s = float(s)
        self.n_fft = int(fft)

    def getparams(self, config):
        tree = et.parse(config)
        root = tree.getroot()
        for reducer in root.findall('reducer'):
            stationary = reducer.find('stationary').text
            prop_decrease = reducer.find('prop_decrease').text
            hz = reducer.find('freq_mask_smooth_hz').text
            ms = reducer.find('time_mask_smooth_ms').text
            s = reducer.find('time_constant_s').text
            fft = reducer.find('n_fft').text
        return stationary, prop_decrease, hz, ms, s, fft

    def S_noise_reducer(data,length,rate):
        noise_len = int(length) # seconds
        noise = band_limited_noise(min_freq=10000, max_freq = 20000, samples=len(data), samplerate=rate)*10
        noise_clip = noise[:rate*noise_len]
        audio_clip_band_limited = data+noise

        return(audio_clip_band_limited)
    
    def noise_avg_reducer(entrada, noise):
        audio, audiorate = sf.read(entrada)
        noise, noiserate = sf.read(noise)
        audio = np.subtract(audio, np.average(noise))
        return audio
    
    def read_file(self, file_path):
        rate, data = rec.read_audio(file_path)
        return rate, data
    
    def read_wav(self, file_path):
        rate, data = wavfile.read(file_path)
        print(data)
        return rate, data
    
    def volumen(self, fichero, volumen):
        song = AudioSegment.from_wav(fichero)
        song_db = song + volumen
        song_db.export(fichero, "wav")
        return song_db
    
    def write_wav(self, wavfile, framerate, data):
        with wave.open(wavfile, mode="wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(framerate)
            wav_file.writeframes(data)
            wav_file.close()

    def reduce_ruido(self,
                      data,
                      rate,
                      clean_file_path: str = "./clean_path/clean_file.wav",
                      stationary: bool = False,
                      prop_decrease: float = 1.0, 
                      time_constant_s: float = 2.0,
                      freq_mask_smooth_hz: int = 500,
                      time_mask_smooth_ms: int = 50,
                      thresh_n_mult_nonstationary: int = 1,
                      sigmoid_slope_nonstationary: int = 10,
                      n_std_thresh_stationary: float = 1.5,
                      tmp_folder: [type] = None,
                      chunk_size: int = 60000,
                      padding: int = 30000,
                      n_fft: int = 1024,
                      win_length: [type] = None,
                      hop_length: [type] = None,
                      clip_noise_stationary: bool = True, 
                      use_tqdm: bool = False, 
                      n_jobs: int = 1,
                      use_torch: bool = False,
                      device: bool = "cuda"):
        '''
        Reduce el ruido de un audio y lo guarda en un archivo en formato WAV

        Parameters
        ----------
        stationary: bool, optional
            Whether to perform stationary, or non-stationary noise reduction, by default False
            
        prop_decrease: float, optional
            The proportion to reduce the noise by (1.0 = 100%), by default 1.0
            
        time_constant_s: float, optional
            The time constant, in seconds, to compute the noise floor in the non-stationary algorithm, by default 2.0
            
        freq_mask_smooth_hz: int, optional
            The frequency range to smooth the mask over in Hz, by default 500
            
        time_mask_smooth_ms: int, optional
            The time range to smooth the mask over in milliseconds, by default 50
            
        thresh_n_mult_nonstationary: int, optional
            Only used in nonstationary noise reduction., by default 1
            
        sigmoid_slope_nonstationary: int, optional
            Only used in nonstationary noise reduction., by default 10
            
        n_std_thresh_stationary: int, optional
            Number of standard deviations above mean to place the threshold between signal and noise., by default 1.5
            
        tmp_folder: [type], optional
            Temp folder to write waveform to during parallel processing. Defaults to default temp folder for python., by default None
        
        chunk_size: int, optional
            Size of signal chunks to reduce noise over. Larger sizes will take more space in memory, smaller sizes can take longer to compute. , by default 60000 padding : int, optional How much to pad each chunk of signal by. Larger pads are needed for larger time constants., by default 30000
            
        padding : int, optional 
            How much to pad each chunk of signal by. Larger pads are needed for larger time constants., by default 30000
            
        n_fft: int, optional
            length of the windowed signal after padding with zeros. The number of rows in the STFT matrix D is (1 + n_fft/2). The default value, n_fft=2048 samples, corresponds to a physical duration of 93 milliseconds at a sample rate of 22050 Hz, i.e. the default sample rate in librosa. This value is well adapted for music signals. However, in speech processing, the recommended value is 512, corresponding to 23 milliseconds at a sample rate of 22050 Hz. In any case, we recommend setting n_fft to a power of two for optimizing the speed of the fast Fourier transform (FFT) algorithm., by default 1024
            
        win_length: [type], optional
            Each frame of audio is windowed by window of length win_length and then padded with zeros to match n_fft. Smaller values improve the temporal resolution of the STFT (i.e. the ability to discriminate impulses that are closely spaced in time) at the expense of frequency resolution (i.e. the ability to discriminate pure tones that are closely spaced in frequency). This effect is known as the time-frequency localization trade-off and needs to be adjusted according to the properties of the input signal y. If unspecified, defaults to win_length = n_fft., by default None
            
        hop_length: [type], optional
            number of audio samples between adjacent STFT columns. Smaller values increase the number of columns in D without affecting the frequency resolution of the STFT. If unspecified, defaults to win_length // 4 (see below)., by default None
            
        use_tqdm: bool, optional
            Whether to show tqdm progress bar, by default False
            
        n_jobs: int, optional
            Number of parallel jobs to run. Set at -1 to use all CPU cores, by default 1
            
        use_torch: bool, optional
            Whether to use the torch version of spectral gating, by default False
            
        device: str, optional
            A device to run the torch spectral gating on, by default "cuda"
        Returns
        -------
        None.

        '''

        # perform noise reduction
        reduced_noise = nr.reduce_noise(y = data, 
                                        sr = rate, 
                                        stationary = self.stationary,
                                        prop_decrease = self.prop_decrease, 
                                        time_constant_s = self.time_constant_s,
                                        freq_mask_smooth_hz = self.freq_mask_smooth_hz,
                                        time_mask_smooth_ms = self.time_mask_smooth_ms,
                                        thresh_n_mult_nonstationary = thresh_n_mult_nonstationary,
                                        sigmoid_slope_nonstationary = sigmoid_slope_nonstationary,
                                        n_std_thresh_stationary = n_std_thresh_stationary,
                                        tmp_folder = tmp_folder,
                                        chunk_size = chunk_size,
                                        padding = padding,
                                        n_fft = self.n_fft,
                                        win_length = win_length,
                                        hop_length = hop_length,
                                        clip_noise_stationary = clip_noise_stationary, 
                                        use_tqdm = use_tqdm, 
                                        n_jobs = n_jobs,
                                        use_torch = use_torch,
                                        device = device)
        
        print(reduced_noise)
        # save audio file
        rec.write_audio(self, reduced_noise, rate, clean_file_path)
        framerate = 22050
        audio = AudioSegment.from_file(clean_file_path, format="wav", frame_rate=44100)
        resample_audio = audio.set_frame_rate(framerate)
        resample_audio.export(clean_file_path, format='wav')

if __name__=='__main__':

    entrada = '../audiofiles/Apollo_11_launch_day_communication_relayed_through_Canary_Station.wav'
    salida = '../audiofiles/cleaned/clean_Apollo_11_launch_day_communication_relayed_through_Canary_Station.wav'
    #entrada = '../audiofiles/websdr_recording_2024-05-03T12_06_47Z_7175.0kHz.wav'
    entrada = '../audiofiles/websdr_recording_2024-05-03T20_15_23Z_7123.0kHz.wav'
    #salida = '../audiofiles/cleaned/websdr_recording_2024-05-03T12_06_47Z_7175.0kHz.wav'
    salida = '../audiofiles/cleaned/websdr_recording_2024-05-03T20_15_23Z_7123.0kHz.wav'
    #noise = '../audiofiles/noise/websdr_recording_2024-05-03T12_06_47Z_7175.0kHz_noise.wav'
    noise = '../audiofiles/noise/websdr_recording_2024-05-03T20_15_23Z_7123.0kHz_noise.wav'
    reduce = reducer('../config.xml')
    print('Stationary: ' + reduce.stationary)
    print('Proportion decrease: ' + str(reduce.prop_decrease))
    print('Frequency mask: ' + str(reduce.freq_mask_smooth_hz))

    
    audio, audiorate = sf.read(entrada)
    noise, noiserate = sf.read(noise)
    #audio = np.subtract(audio, np.average(noise))
    reduced_noise = nr.reduce_noise(y = audio, sr = audiorate, y_noise=noise, prop_decrease=0.8)
    #reduce.write_wav(salida, audiorate, audio)
    sf.write(salida, reduced_noise, audiorate)
    #write(salida, audiorate, audio.astype(np.int16))
    #audio.export(salida, "wav")
    print(noise)
    print(noiserate)
    print(audio)

    #rate, data = wavfile.read(entrada)
    #reduce.reduce_ruido(data, rate, salida, True)

    #audio = reduce.volumen(salida, 6)
