from pydub import AudioSegment
sound = AudioSegment.from_mp3("C:\\MAS\\1-second-of-silence.mp3")
sound.export("C:\\MAS\\file.wav", format="wav")