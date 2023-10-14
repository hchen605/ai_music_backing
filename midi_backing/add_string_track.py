import midi
import numpy as np
from chord_to_harmony import *
#import random

def add_string_track(string_track, channel_num, beat, music_key, time_signature, chord):

    string = midi.ProgramChangeEvent(tick=0, channel=channel_num, data=[48])
    string_track.append(string)

    measure_num = np.size(chord)
    #print  measure_num
    beat_per_measure = time_signature.beatCount
    #print beat_per_measure

    #bass note
    first = 0
    for i in range(measure_num):
        chord_measure = chord[i]
        #print chord_measure
        root, third, fifth = chord_to_harmony(chord_measure, music_key, midi.C_4)
        # har = [root, third, fifth]
        # har = har[random.randint(0, 2)]
        on = midi.NoteOnEvent(tick = 0, velocity = 80, pitch = root)
        #first = 1
        string_track.append(on)
        off = midi.NoteOffEvent(tick = beat*beat_per_measure, velocity = 80, pitch = root)
        string_track.append(off)


