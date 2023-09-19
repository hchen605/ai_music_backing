
import midi
import read_midi_parameter
#from read_midi_parameter import *
import add_bass_track 
import add_drum_track 
import add_string_track

midi_file = "9_Balader.mid"

beat, music_key, time_signature, chord, pattern = read_midi_parameter.read_midi_parameter(midi_file)

print('Beat: ', beat)
print('Key: ', music_key)
print('Time Signature: ', time_signature)
print('Chord Progress: ', chord)


#add bass track
bass_track = midi.Track()
pattern.append(bass_track)
channel_num = 1
add_bass_track.add_bass_track(bass_track, channel_num, beat, music_key, time_signature, chord)

#add drum track
drum_track = midi.Track()
pattern.append(drum_track)

channel_num = 9
add_drum_track.add_drum_track(drum_track, channel_num, beat, time_signature, chord)


#add string track
string_track = midi.Track()
pattern.append(string_track)
channel_num = 2
add_string_track.add_string_track(string_track, channel_num, beat, music_key, time_signature, chord)

midi.write_midifile("test_hh.mid", pattern)
#midi.write_midifile("69.Mother_hh.mid", pattern)


