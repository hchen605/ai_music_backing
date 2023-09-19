# ai_music_backing

Singing transcription command example:
python sing2midi.py ./data/nothing.wav ./data/nothing.mid -p models/1005_e_4 -on 0.4 -off 0.5

MIDI accompaniment generation command:
python auto_comp.py

Singing to full accompaniment:
python music_backing.py ./data/nothing_short.wav ./data/nothing.mid -p singing_transcription/models/1005_e_4 -on 0.4 -off 0.5