from __future__ import annotations
import sys
sys.path.append('singing_transcription')
sys.path.append('midi_backing')
from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, TrackType, InjectSource, Track, Clip, TuneflowPluginTriggerData, ClipAudioDataInjectData, SelectWidgetOption
from typing import Any
from data_utils.seq_dataset import SeqDataset
from predictor import EffNetPredictor
import torch
from pathlib import Path
import tempfile
import traceback
import music_backing
import read_midi_parameter, chord_to_harmony
import midi
import numpy as np
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
predictor = EffNetPredictor(device=device, model_path=str(
    Path(__file__).parent.joinpath("singing_transcription/models").joinpath("1005_e_4").absolute()))


class TranscribeSinging(TuneflowPlugin):
    @staticmethod
    def provider_id():
        return "hellwz"

    @staticmethod
    def plugin_id():
        return "singing-transcription"

    @staticmethod
    def params(song: Song) -> dict[str, ParamDescriptor]:
        return {
            "clipAudioData": {
                "displayName": {
                    "zh": 'Audio',
                    "en": 'Audio',
                },
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                "hidden": True,
                "injectFrom": {
                    "type": InjectSource.ClipAudioData.value,
                    "options": {
                        "clips": "selectedAudioClips",
                        "convert": {
                            "toFormat": "ogg",
                            "options": {
                                "sampleRate": 44100
                            }
                        }
                    }
                }
            },
            "Valence": {
                "displayName": {
                    "zh": 'Emotional Valence',
                    "en": 'Emotional Valence',
                },
                "defaultValue": 0.5,
                "description": {
                    "zh": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                    "en": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0.1,
                        "maxValue": 0.9,
                        "step": 0.1
                    }
                },
            },
            "Arousal": {
                "displayName": {
                    "zh": 'Emotional Arousal',
                    "en": 'Emotional Arousal',
                },
                "defaultValue": 0.5,
                "description": {
                    "zh": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                    "en": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0.1,
                        "maxValue": 0.9,
                        "step": 0.1
                    }
                },
            },
            "Genre": {
                "displayName": {
                    "zh": 'Music Genre',
                    "en": 'Music Genre',
                },
                "defaultValue": 'Pop',
                "description": {
                    "zh": 'Genre',
                    "en": 'Genre',
                },
                "widget": {
                    "type": WidgetType.Select.value,
                    "config": {
                        "label": ['Rock','Jazz'],
                        "value": 'Rock'
                    }
                },
            },
            "Instrument": {
                "displayName": {
                    "zh": 'Instrument',
                    "en": 'Instrument',
                },
                "defaultValue": 'Bass',
                "description": {
                    "zh": 'Instrument',
                    "en": 'Instrument',
                },
                "widget": {
                    "type": WidgetType.InstrumentSelector.value,
                    "config": {
                        "label": ['Rock','Jazz'],
                        "value": 'Rock'
                    }
                },
            },
            "prompt": {
                "displayName": {
                    "en": "Prompt",
                    "zh": "Prompt for Music"
                },
                "description": {
                    "en": "A short sentence to describe the audio you want to generate",
                    "zh": "A short sentence to describe the music you want to generate"
                },
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.TextArea.value,
                    "config": {
                        "placeholder": {
                            "zh": "e.g. A pop alike music in sad emotion",
                            "en": "e.g. A hammer is hitting a tree"
                        },
                        "maxLength": 140
                    }
                }
            },
            "onsetThreshold": {
                "displayName": {
                    "zh": 'Onset threshold',
                    "en": 'Onset threshold',
                },
                "defaultValue": 0.4,
                "description": {
                    "zh": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                    "en": 'The higher the threshold, the lower the number of MIDI notes that will be transcribed',
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0.1,
                        "maxValue": 0.9,
                        "step": 0.1
                    }
                },
            },
            "silenceThreshold": {
                "displayName": {
                    "zh": 'Silence threshold',
                    "en": 'Silence threshold',
                },
                "defaultValue": 0.5,
                "description": {
                    "zh": 'The higher the threshold, the longer the MIDI note transcribed',
                    "en": 'The higher the threshold, the longer the MIDI note transcribed',
                },
                "widget": {
                    "type": WidgetType.Slider.value,
                    "config": {
                        "minValue": 0.1,
                        "maxValue": 0.9,
                        "step": 0.1
                    }
                },
            },
        }

    @staticmethod
    def run(song: Song, params: dict[str, Any]):
        trigger: TuneflowPluginTriggerData = params["trigger"]
        trigger_entity_id = trigger["entities"][0]
        track = song.get_track_by_id(trigger_entity_id["trackId"])
        if track is None:
            raise Exception("Cannot find track")
        clip = track.get_clip_by_id(trigger_entity_id["clipId"])
        if clip is None:
            raise Exception("Cannot find clip")
        clip_audio_data_list: ClipAudioDataInjectData = params["clipAudioData"]
        new_midi_track = song.create_track(type=TrackType.MIDI_TRACK, index=song.get_track_index(
            track_id=track.get_id()),
            assign_default_sampler_plugin=True)

        new_midi_track_2 = song.create_track(type=TrackType.MIDI_TRACK, index=song.get_track_index(
            track_id=track.get_id()),
            assign_default_sampler_plugin=True)
        
        new_midi_track_3 = song.create_track(type=TrackType.MIDI_TRACK, index=song.get_track_index(
            track_id=track.get_id()),
            assign_default_sampler_plugin=True)

        new_midi_track_4 = song.create_track(type=TrackType.MIDI_TRACK, index=song.get_track_index(
            track_id=track.get_id()),
            assign_default_sampler_plugin=True)

        tmp_file = tempfile.NamedTemporaryFile(delete=True, suffix=clip_audio_data_list[0]["audioData"]["format"])
        tmp_file.write(clip_audio_data_list[0]["audioData"]["data"])

        try:
            TranscribeSinging._transcribe_clip(predictor, song,
                                               new_midi_track,
                                               clip,
                                               tmp_file.name,
                                               False,
                                               params["onsetThreshold"],
                                               params["silenceThreshold"])
            TranscribeSinging._midi_back_bass(new_midi_track_2,
                                          clip,
                                          './data/plug_trans.mid',
                                        )
            TranscribeSinging._midi_back_string(new_midi_track_3,
                                          clip,
                                          './data/plug_trans.mid',
                                        )
            TranscribeSinging._midi_back_drum(new_midi_track_4,
                                          clip,
                                          './data/plug_trans.mid',
                                        )
            
        except Exception as e:
            print(traceback.format_exc())
        finally:
            tmp_file.close()

    @staticmethod
    def _transcribe_clip(
        predictor,
        song: Song,
        new_midi_track: Track,
        audio_clip: Clip,
        audio_file_path,
        do_separation=False,
        onset_threshold=0.4,
        silence_threshold=0.5,
    ):
        new_clip = new_midi_track.create_midi_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            insert_clip=True
        )
        audio_clip_start_tick = audio_clip.get_clip_start_tick()
        audio_start_time = song.tick_to_seconds(audio_clip_start_tick)
        test_dataset = SeqDataset(audio_file_path, song_id='1', do_svs=do_separation)

        results = {}
        results = predictor.predict(test_dataset, results=results,
                                    onset_thres=onset_threshold, offset_thres=silence_threshold)
        music_backing.convert_to_midi(results, '1', './data/plug_trans.mid')

        for notes in results['1']:
            note_start_time_within_audio = notes[0]
            note_start_tick = song.seconds_to_tick(note_start_time_within_audio + audio_start_time)
            note_end_time_within_audio = notes[1]
            note_end_tick = song.seconds_to_tick(note_end_time_within_audio + audio_start_time)
            note_pitch = notes[2]

            new_clip.create_note(
                pitch=note_pitch,
                velocity=20,
                start_tick=note_start_tick,
                end_tick=note_end_tick
            )
        new_clip.adjust_clip_left(clip_start_tick=audio_clip.get_clip_start_tick(), resolve_conflict=False)
        new_clip.adjust_clip_right(clip_end_tick=audio_clip.get_clip_end_tick(), resolve_conflict=False)

    @staticmethod
    def _midi_back_bass(
        new_midi_track: Track,
        audio_clip: Clip,
        midi_file='./data/plug_trans.mid'):
        beat, music_key, time_signature, chord, pattern = read_midi_parameter.read_midi_parameter(midi_file)
        print('Beat: ', beat)
        print('Key: ', music_key)
        print('Time Signature: ', time_signature)
        print('Chord Progress: ', chord)

        measure_num = np.size(chord)
        #print  measure_num
        beat_per_measure = time_signature.beatCount
        #print beat_per_measure

        new_midi_track.set_instrument(33, False)#bass
        new_clip = new_midi_track.create_midi_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            insert_clip=True
        )
        audio_clip_start_tick = audio_clip.get_clip_start_tick()
        #bass note
        first = 0
        beat = beat * beat_per_measure
        for i in range(measure_num):
            chord_measure = chord[i]
            #print chord_measure
            root, third, fifth = chord_to_harmony.chord_to_harmony(chord_measure, music_key, midi.C_3)
            #for notes in results['1']:
            #note_start_time_within_audio = notes[0]
            note_start_tick = beat*i + audio_clip_start_tick
            #note_end_time_within_audio = notes[1]
            note_end_tick = beat*i+beat + audio_clip_start_tick
            note_pitch = root

            new_clip.create_note(
                pitch=note_pitch,
                velocity=100,
                start_tick=note_start_tick,
                end_tick=note_end_tick
            )
        new_clip.adjust_clip_left(clip_start_tick=audio_clip.get_clip_start_tick(), resolve_conflict=False)
        new_clip.adjust_clip_right(clip_end_tick=audio_clip.get_clip_end_tick(), resolve_conflict=False)

            # on = midi.NoteOnEvent(tick = 0, velocity = 80, pitch = root)
            # first = 1
            # bass_track.append(on)
            # off = midi.NoteOffEvent(tick = beat*beat_per_measure, velocity = 80, pitch = root)
            # bass_track.append(off)

    def _midi_back_string(
        new_midi_track: Track,
        audio_clip: Clip,
        midi_file='./data/plug_trans.mid'):
        beat, music_key, time_signature, chord, pattern = read_midi_parameter.read_midi_parameter(midi_file)
        # print('Beat: ', beat)
        # print('Key: ', music_key)
        # print('Time Signature: ', time_signature)
        # print('Chord Progress: ', chord)

        measure_num = np.size(chord)
        #print  measure_num
        beat_per_measure = time_signature.beatCount
        #print beat_per_measure

        new_midi_track.set_instrument(48, False)#string
        new_midi_track.set_volume(0.5)
        new_clip = new_midi_track.create_midi_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            insert_clip=True
        )
        audio_clip_start_tick = audio_clip.get_clip_start_tick()
        #bass note
        first = 0
        beat = beat * beat_per_measure
        for i in range(measure_num):
            chord_measure = chord[i]
            #print chord_measure
            root, third, fifth = chord_to_harmony.chord_to_harmony(chord_measure, music_key, midi.C_4)
            #for notes in results['1']:
            #note_start_time_within_audio = notes[0]
            note_start_tick = beat*i + audio_clip_start_tick
            #note_end_time_within_audio = notes[1]
            note_end_tick = beat*i+beat + audio_clip_start_tick
            har = [root, third, fifth]
            har = har[random.randint(0, 2)]
            note_pitch = har

            new_clip.create_note(
                pitch=note_pitch,
                velocity=50,
                start_tick=note_start_tick,
                end_tick=note_end_tick
            )
        new_clip.adjust_clip_left(clip_start_tick=audio_clip.get_clip_start_tick(), resolve_conflict=False)
        new_clip.adjust_clip_right(clip_end_tick=audio_clip.get_clip_end_tick(), resolve_conflict=False)

    def _midi_back_drum(
        new_midi_track: Track,
        audio_clip: Clip,
        midi_file='./data/plug_trans.mid'):
        beat, music_key, time_signature, chord, pattern = read_midi_parameter.read_midi_parameter(midi_file)
        # print('Beat: ', beat)
        # print('Key: ', music_key)
        # print('Time Signature: ', time_signature)
        # print('Chord Progress: ', chord)

        measure_num = np.size(chord)
        #print  measure_num
        beat_per_measure = time_signature.beatCount
        #print beat_per_measure

        new_midi_track.set_instrument(9, True)#drum
        new_midi_track.set_volume(0.5)
        new_clip = new_midi_track.create_midi_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            insert_clip=True
        )
        audio_clip_start_tick = audio_clip.get_clip_start_tick()

        #drum
        HH = 51
        SS = 37
        SD = 38
        BD = 35
        LT = 41
        HT = 48
        first = 0
        first_measure = 0
        beat = beat 
        th_1 = 0.8
        th_2 = 0.6
        th_3 = 0.4


        for i in range(measure_num):
            #first = 0
            if i < 2:
                th = th_1
            elif 2 <= i < 4:
                th = th_2
            else:
                th = th_3
            for j in range(beat_per_measure):
                #if first == 0:
                if j % 4 == 0:
                    hit = BD
                elif j % 4 == 2:
                    hit = SD
                else:
                    if np.random.rand() > th:
                        hit = HH
                    else:
                        hit = 0
                if i == measure_num - 1:
                    # on = midi.NoteOnEvent(tick = beat*first_measure, velocity = 80, pitch = HH)
                    # drum_track.append(on)
                    # on = midi.NoteOnEvent(tick = 0, velocity = 80, pitch = BD)
                    # drum_track.append(on)
                    note_start_tick = beat*j+i*beat_per_measure*beat + audio_clip_start_tick
                    note_end_tick = beat*j+i*beat_per_measure*beat+beat + audio_clip_start_tick
                    new_clip.create_note(
                    pitch=hit,
                    velocity=80,
                    start_tick=note_start_tick,
                    end_tick=note_end_tick
                )
                    break
                else:
                    #on = midi.NoteOnEvent(tick = beat*first_measure, velocity = 80, pitch = hit)
                    note_start_tick = beat*j+i*beat_per_measure*beat + audio_clip_start_tick
                    note_end_tick = beat*j+i*beat_per_measure*beat+beat + audio_clip_start_tick
                    new_clip.create_note(
                    pitch=hit,
                    velocity=80,
                    start_tick=note_start_tick,
                    end_tick=note_end_tick
                )
                #first = 1
                #first_measure = 1

            
        new_clip.adjust_clip_left(clip_start_tick=audio_clip.get_clip_start_tick(), resolve_conflict=False)
        new_clip.adjust_clip_right(clip_end_tick=audio_clip.get_clip_end_tick(), resolve_conflict=False)

         