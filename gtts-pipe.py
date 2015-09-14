#!/usr/bin/python3
import sys
from gtts import gTTS
import argparse


def main():
	desc = "Creates an stdout stream with audio data from spoken text via the Google Text-to-Speech API"
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-t', '--text', required=True, help="text to speak")
	parser.add_argument('-l', '--lang', default='en', help="Language tag to speak in")
	args = parser.parse_args()

	tts = gTTS(text=args.text, lang=args.lang)
	tts.write_to_fp(sys.stdout.buffer)

if __name__ == "__main__":
    main()
