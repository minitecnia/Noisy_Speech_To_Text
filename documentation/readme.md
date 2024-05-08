# InSTT documentation
Documentation

## Installing modules
We opted to install PyTorch via the official website rather than utilizing the pip package manager, in order to mitigate potential compatibility issues across different operating systems and Python versions. Use:

https://pytorch.org/get-started/locally/

## Audio treatment
Audio files can be encoded in various formats such as .wav, .mp3, .mp4, etc. To prevent incompatibilities within the audio dataflow, files are encoded in the .wav format. Converter function can be added to audio tools.

# Transcription and translation
We use the followed models:
- Vosk (only transcription)
- Whisper (transcription and translation)
Both models are called from the voskstt and whisperstt python modules.

