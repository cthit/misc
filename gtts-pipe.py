import sys
from gtts import gTTS
from tempfile import TemporaryFile

if len(sys.argv) < 2:
    print("Requires an argument to output")
    exit(1)

tts = gTTS(text=sys.argv[1], lang='en')
tts.write_to_fp(sys.stdout.buffer)


