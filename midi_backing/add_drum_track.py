import midi
import numpy as np
#from chord_to_harmony import *

def add_drum_track(drum_track, channel_num, beat, time_signature, chord):

    drum = midi.ProgramChangeEvent(tick=0, channel=channel_num, data=[0])
    drum_track.append(drum)

    measure_num = np.size(chord)
    beat_per_measure = time_signature.beatCount
    #print beat_per_measure

    #drum
    HH = 51
    SS = 37
    SD = 38
    BD = 35
    LT = 41
    HT = 48
    first = 0
    first_measure = 0
    for i in range(measure_num):
        first = 0
        for j in range(beat_per_measure):
            if first == 0:
                if i % 2 == 0:
                    hit = BD
                else:
                    hit = SD
            else:
                hit = HH
            if i == measure_num - 1:
                on = midi.NoteOnEvent(tick = beat*first_measure, velocity = 80, pitch = HH)
                drum_track.append(on)
                on = midi.NoteOnEvent(tick = 0, velocity = 80, pitch = BD)
                drum_track.append(on)
                break
            else:
                on = midi.NoteOnEvent(tick = beat*first_measure, velocity = 80, pitch = hit)
            first = 1
            first_measure = 1
            drum_track.append(on)




