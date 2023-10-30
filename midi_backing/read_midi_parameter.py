
#import midi
from music21 import converter, corpus, instrument, midi, note, chord, pitch, stream, roman
from music21_add import *
from music21 import *
import midi
import numpy as np

def read_midi_parameter(midi_file):
    
    #print(midi)
    pattern_read = midi.read_midifile(midi_file)
    #print(pattern_read)
    beat = pattern_read.resolution
    #pattern = open_midi("hh.mid", True)
    pattern = open_midi(midi_file, True)

    temp_midi = stream.Score()
    #print(temp_midi)
    temp_midi_chords = pattern.chordify()
    # print(temp_midi_chords[3])#<music21.chord.Chord F4>
    # print(temp_midi_chords[4])
    # print(temp_midi_chords[5])

    temp_midi.insert(0, temp_midi_chords)
    music_key = temp_midi.analyze('key')
    #print('Key: ', music_key)
    time_signature = temp_midi_chords.getTimeSignatures()[0]
    max_notes_per_chord = 4
    #temp_midi_chords.show("text")
    #print(temp_midi_chords[4])
    total_beat = np.size(temp_midi_chords) + 1 - 4
    total_measure = total_beat / time_signature.beatCount

    fp = open("chord.txt", "w")
    for thisChord in temp_midi_chords.recurse().getElementsByClass(chord.Chord):
        #print(thisChord)
        #print(thisChord.measureNumber, thisChord.beatStr, thisChord)
        note_beat = str(thisChord).strip('<>')
        fp.write(note_beat)
        fp.write("\n")
    # i = 4
    # offset = 0
    # while i < total_beat + 3:
        
    #     beat_offset = int(temp_midi_chords[i].offset)
    #     if beat_offset > offset:
    #         hold = beat_offset - offset
    #         for k in range(hold):
    #             note_beat = str(temp_midi_chords[i-1]).strip('<>')
    #             #print(note_beat)
    #             fp.write(note_beat)
    #             fp.write("\n")
    #             offset = offset + 1

    #     note_beat = str(temp_midi_chords[i]).strip('<>')
    #     #print(note_beat)
    #     fp.write(note_beat)
    #     fp.write("\n")

        
    #     i = i + 1
    #     offset = offset + 1
    fp.close()
    
    
    
    count = 1
    ret = []
    note_list = []
    fp = open("chord.txt", "r")
    while True:
        read = fp.readline()
        read_size = np.size(read.split())
        #print read_size
        if not read:
            #print('end note: ', note_list)
            if not note_list:
                break
            measure_chord = chord.Chord(note_list)
            roman_numeral = roman.romanNumeralFromChord(measure_chord, music_key)
            ret.append(simplify_roman_name(roman_numeral))
            break
        #print(read)
        #i = 1
        
        for i in range(1, read_size):
            note1 = read.split()[i]
            if note1 == 'rest':
                note1 = note1_pre
                note_list.append(note1)
            else:
                note_list.append(note1)
                note1_pre = note1
        i = i + 1
        #print(note_list)
        if count % time_signature.beatCount == 0: #or count == total_measure:
            #print(note_list)
            measure_chord = chord.Chord(note_list)
            #print(measure_chord)
            roman_numeral = roman.romanNumeralFromChord(measure_chord, music_key)
            #print(roman_numeral)
            ret.append(simplify_roman_name(roman_numeral))
            note_list = []
        
        count = count + 1
    fp.close()
    
#print(ret)
    return beat, music_key, time_signature, ret, pattern_read
