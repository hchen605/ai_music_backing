# ai_music_backing

Singing transcription command example:
python sing2midi.py ./data/nothing.wav ./data/nothing.mid -p models/1005_e_4 -on 0.4 -off 0.5

MIDI accompaniment generation command:
python auto_comp.py

Singing to full accompaniment:
python music_backing.py ./data/nothing_short.wav ./data/nothing.mid -p singing_transcription/models/1005_e_4 -on 0.4 -off 0.5

Plugin debug:
python debug

Flask demo: python app.py

Note:
music_back py3.6 runnable conda env for Singing to full accompaniment
music_back_plugin py3.7 for plugin test, will fail! Resolved by replacing chord.txt write method
