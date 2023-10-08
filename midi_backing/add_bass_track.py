import midi
import numpy as np
from chord_to_harmony import *

def add_bass_track(bass_track, channel_num, beat, music_key, time_signature, chord):

    bass = midi.ProgramChangeEvent(tick=0, channel=channel_num, data=[33])
    bass_track.append(bass)

    measure_num = np.size(chord)
    #print  measure_num
    beat_per_measure = time_signature.beatCount
    #print(beat_per_measure)

    #bass note
    first = 0
    for i in range(measure_num):
        chord_measure = chord[i]
        #print chord_measure
        root, third, fifth = chord_to_harmony(chord_measure, music_key, midi.C_3)
        on = midi.NoteOnEvent(tick = 0, velocity = 80, pitch = root)
        first = 1
        bass_track.append(on)
        off = midi.NoteOffEvent(tick = beat*beat_per_measure, velocity = 80, pitch = root)
        bass_track.append(off)


