import sys
from gtts import gTTS
from tempfile import TemporaryFile
tts = gTTS(text='Hello', lang='en')
tts.write_to_fp(sys.stdout.buffer)
