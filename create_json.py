#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

from constants import (SEED, PROBA_SPK, SR_DIARIZATION, SR_AUDIO, 
                    MIN_DURATION_SUBSEG, SNR_MEAN_MIX, SNR_STD_MIX, 
                    SNR_STD_SPK)

import json
import pandas as pd
import numpy as np
np.random.seed(SEED)
import os
import random
random.seed(SEED)
import soundfile as sf
from utils import get_segments_start_end
import copy
from tqdm import tqdm

from paths import (unlabeled_data_audio_path, unlabeled_data_json_path, 
                   voicehome_path, labeled_data_json_path)


VERBOSE = True

def get_file_list(root_path, endswith=None):
    file_list = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if endswith is None:
                file_list.append(os.path.join(root, file))
            elif file.endswith(endswith):
                 file_list.append(os.path.join(root, file))
                 
    return file_list

def list_from_json(json_file_list):
    
    out = []
    for file in json_file_list:
        
        head, filename = os.path.split(file)
        _, subset = os.path.split(head)
        
        with open(file) as f:  
            data = json.load(f)
        
        for d in data:
            d['filename'] = filename[:-5]
            d['subset'] = subset
        
        out.extend(data)
            
    return out

def dataframe_from_list(list_dict, list_type, sessions_speakers):
    
    if list_type == 'speech':
        df = pd.DataFrame(columns=['subset', 'filename', 'id', 'duration',
                                   'length','spk1_active', 'spk1_VA',
                                   'spk2_active', 'spk2_VA', 'spk3_active', 
                                   'spk3_VA'])
    elif list_type == 'noise':
        df = pd.DataFrame(columns=['subset', 'filename', 'id', 'duration', 
                                   'length'])
    else:
        raise Exception('Unknown type of list.')    
    

    for seg in list_dict:
        
        filename = seg['filename']
        session = filename[:3] # session ID
        ref_spk = filename[4:7] # ref speaker
        n_spk = int(filename[8]) # num simultaneaously active speakers
        speakers = sessions_speakers[session]
        
        if list_type == 'speech':
            
            speakers_VA = []
            speakers_active = []
            for spk_ind, spk in enumerate(speakers):
                if spk == ref_spk:
                    continue
                activity = [int(x) for x in list(seg[spk])]
                speakers_VA.append(activity)
                if np.sum(activity) > 0:
                    speakers_active.append(True)
                else:
                    speakers_active.append(False)
    
            num_spk_vs_time_mix = np.zeros_like(speakers_VA[0])
            for VA in speakers_VA:
                num_spk_vs_time_mix += VA
            max_num_active_spk = int(np.max(num_spk_vs_time_mix)) 
            assert max_num_active_spk == n_spk
            
            seg_list = [seg['subset'], 
                        seg['filename'], 
                        seg['mix'], 
                        seg['duration'],
                        int(np.ceil(seg['duration']*SR_AUDIO)),
                        speakers_active[0],
                        speakers_VA[0],
                        speakers_active[1],
                        speakers_VA[1],
                        speakers_active[2],
                        speakers_VA[2],
                        ]
        elif list_type == 'noise':
            
            seg_list = [seg['subset'], 
                        seg['filename'], 
                        seg['mix'], 
                        seg['duration'],
                        int(np.ceil(seg['duration']*SR_AUDIO)),
                        ]
        
        df.loc[len(df)] = seg_list

    return df

def create_seg_df(json_path, subset, sessions_speakers):
    df_seg_all = {}
    for n_spk in [1,2,3]:  
        # get the list of json files with max n_spk simultaneously active 
        # speakers
        segments_file_list = get_file_list(os.path.join(json_path, subset), 
                                           endswith=(str(n_spk)+'.json'))

        # create df of segments
        list_segments = list_from_json(segments_file_list)
        df_seg_all[str(n_spk)] = dataframe_from_list(list_segments, 'speech', 
                                                     sessions_speakers)
        
        
    # discard segments with too short subsegments
    df_seg_all, cpt = filter_df_segments(df_seg_all, MIN_DURATION_SUBSEG)

    # try again to filter segments containing too short subsegments
    # and check that all segments are now ok
    _, cpt = filter_df_segments(df_seg_all, MIN_DURATION_SUBSEG)
    assert cpt == 0
    
    return df_seg_all

def create_noise_df(noise_file_list, subset):

    df_noise = pd.DataFrame(columns=['subset', 'filename', 'length', 
                                     'duration'])
    
    for noise_file in noise_file_list:
        
        filename = os.path.basename(noise_file)[:-4]
        
        f = sf.SoundFile(noise_file)
        
        assert f.samplerate==SR_AUDIO
        
        length = f.frames
        duration = length/SR_AUDIO
        
        df_noise.loc[len(df_noise)] = [subset, filename, length, duration]
    
    return df_noise

def check_subseg_duration(seg, subseg_min_duration):
    """ 
    returns true if seg contains a subsegment of duration
    smaller than subseg_min_duration, false otherwise
    """
        
    for spk_ind in [1, 2, 3]:
        
        is_active = seg['spk' + str(spk_ind) + '_active']
        
        if is_active:
            
            # get speaker activity
            activity = seg['spk' + str(spk_ind) + '_VA']
            
            # get list of subsegments where speaker is active
            subseg_start, subseg_end = get_segments_start_end(activity)
            
            # for each subsegment
            for (start, end) in zip(subseg_start, subseg_end):
                
                # compute duration
                subseg_duration = (end - start)/SR_DIARIZATION
                
                # if duration too small, remove the segment
                if subseg_duration < subseg_min_duration:
                    return True
                
    return False

def filter_df_segments(df_seg_all, subseg_min_duration):
    
    cpt = 0
    
    for n_spk in [1,2,3]:  
        
        df_seg = df_seg_all[str(n_spk)]
        
        ind_to_remove = []
        
        for index, seg in df_seg.iterrows():
            
            if check_subseg_duration(seg, subseg_min_duration):
                
                ind_to_remove.append(index)
                cpt += 1
        
        df_seg_all[str(n_spk)] = df_seg.drop(index=df_seg.index[ind_to_remove])      
        
    return df_seg_all, cpt

def get_seg(df_seg_all, seg_len, proba_spk, n_trials=200, remove=True):
    
    """
    find the CHiME segment in df_seg_all whose length is closest to seg_len 
    and at least equal to seg_len
    """
    
    seg = None
    
    cpt_try = 0
    while cpt_try < n_trials:
    
        cpt_try += 1
        
        # sample a max number of simultaneously active speakers
        n_spk = np.random.choice([1,2,3], p=proba_spk)    
        
        # extract corresponding dataframe
        df_seg = df_seg_all[str(n_spk)]
        
        # find the CHiME segment whose duration is closest to noise_dur 
        # and at least equal to noise_dur
        df_seg_filt = df_seg[df_seg['length'] >= seg_len]
        
        if len(df_seg_filt) != 0:            
            ind_seg = (df_seg_filt['length'] - seg_len).argmin()
            idx = df_seg_filt.index[ind_seg]
            seg = df_seg_filt.iloc[ind_seg]
            
            if remove:
                df_seg = df_seg.drop(index=idx)
                df_seg_all[str(n_spk)] = df_seg
            
            break
    
    if cpt_try == n_trials:
        success = False
    else:
        success = True
    
        assert not check_subseg_duration(seg, MIN_DURATION_SUBSEG)
    
    return seg, n_spk, df_seg_all, success

def get_speaker_activity(seg, seg_len):

    """
    spks_activity is dictionary with three entries, one for each potential 
    speaker in the current segment.
    
    spks_activity{'i'} contains information about the i-th speaker:
        - is_active: boolean indicating if the speaker is active
        if speaker is active:
        - activity: list of binary values indicating the speaker's activity 
            (SR_DIARIZATION)
        - subseg_starts: list of starting indices for subsegments where speaker 
            is active (SR_AUDIO)
        - subseg_ends: list of ending indices for subsegments where speaker 
            is active (SR_AUDIO)
        
    """
    
    # resample to SR_DIARIZATION 
    target_len = int(np.floor(seg_len/SR_AUDIO*SR_DIARIZATION)) 
    
    spks_activity = {'1': {}, '2': {}, '3': {}}
    
    num_spk_vs_time_mix = None

    for spk_ind in [1, 2, 3]:
        
        # is speaker active
        spks_activity[str(spk_ind)]['is_active'] = seg['spk' + str(spk_ind) + '_active']
        
        # if speaker is active
        if spks_activity[str(spk_ind)]['is_active']:
            
            # get speaker's full activity
            spks_activity[str(spk_ind)]['activity'] = seg['spk' + str(spk_ind) + '_VA']
            
            # cut segment to match noise duration
            spks_activity[str(spk_ind)]['activity'] = spks_activity[str(spk_ind)]['activity'][:target_len]
            
            # update number of speakers vs time
            if num_spk_vs_time_mix is None:
                num_spk_vs_time_mix = np.zeros_like(np.array(spks_activity[str(spk_ind)]['activity']))
            num_spk_vs_time_mix += np.array(spks_activity[str(spk_ind)]['activity'])
            
            # get list of subsegments where speaker is active
            subseg_start, subseg_end = get_segments_start_end(spks_activity[str(spk_ind)]['activity'])
                        
            subseg_start_rs = [int(np.floor(x/SR_DIARIZATION*SR_AUDIO)) for x in subseg_start]
            subseg_end_rs = [int(np.floor(x/SR_DIARIZATION*SR_AUDIO)) for x in subseg_end]
            
            # if the subsegment is at the end of the segment, fix subseg_end_rs[-1] 
            # such that it remains at the end 
            if (len(subseg_end) > 0) and (subseg_end[-1] == target_len):
                    subseg_end_rs[-1] = int(seg_len)
            
            spks_activity[str(spk_ind)]['subseg_starts'] = subseg_start_rs # sampling rate is SR_AUDIO
            spks_activity[str(spk_ind)]['subseg_ends'] = subseg_end_rs # sampling rate is SR_AUDIO
    
    # new max number of simultaneously active speakers
    n_spk_new = int(np.max(num_spk_vs_time_mix))
    
    return spks_activity, n_spk_new

def select_utterance(df_librispeech, utt_len, gender=None, speaker_id=None):
    
    if gender is None:
        gender = np.random.choice(['M','F'], p=[0.5, 0.5])
    
    possible_utt = df_librispeech[df_librispeech['sex'] == gender]
    
    possible_speakers = possible_utt['speaker_ID'].unique()
    
    if speaker_id is None:
        speaker_id = random.choice(possible_speakers)
            
    possible_utt = possible_utt[possible_utt['speaker_ID']==speaker_id]
    possible_utt = possible_utt[possible_utt['length']>= utt_len]
    
    if len(possible_utt) > 0:
        ind_utt = (possible_utt['length']).argmin()
        selected_idx = possible_utt.index[ind_utt]
        selected_utt = possible_utt.iloc[ind_utt]
        df_librispeech = df_librispeech.drop(index=selected_idx)
    else:
        selected_utt = None
    
    return df_librispeech, selected_utt

def cut_utterance(seg_len, start_mix, end_mix, libri_utt):
    
    utt_len = end_mix - start_mix
    
    if start_mix==0 and end_mix!=seg_len:
        # subsegment is at the beginning
        end_librispeech = libri_utt['end']
        start_librispeech = end_librispeech - utt_len
    elif start_mix!= 0 and end_mix==seg_len:
        # subsegment is at the end
        start_librispeech = libri_utt['start']
        end_librispeech = start_librispeech + utt_len
    else:
        # subsegment is in the middle or spans entire segment
        start_librispeech = libri_utt['start']
        end_librispeech = start_librispeech + utt_len
        
    assert end_librispeech <= libri_utt['end']
    assert end_librispeech - start_librispeech == utt_len
                        
    return start_librispeech, end_librispeech

def get_spk_utterances(spks_activity, spk_ind, seg_len, df_librispeech, 
                       n_trials=200):
    
    cpt = 0
    
    success = False
    
    while cpt < n_trials:
        
        cpt += 1
    
        # sample speaker gender
        gender = np.random.choice(['M','F'], p=[0.5, 0.5])   
        possible_speakers = df_librispeech[df_librispeech['sex'] == gender]['speaker_ID'].unique()
        speaker_id = random.choice(possible_speakers)
                
        utt_list = []
        success_list = []
        for (start, end) in zip(spks_activity[str(spk_ind)]['subseg_starts'], 
                                spks_activity[str(spk_ind)]['subseg_ends']):

            utt_len = end - start # utterance length = subsegment length
            
            # get librispeech utterance for the speaker spk_ind
            df_librispeech, selected_utt = select_utterance(df_librispeech, 
                                                            utt_len, 
                                                            gender=gender, 
                                                            speaker_id=speaker_id)
            
            # check if an utterance was found for this subsegment
            if selected_utt is not None:
                success_list.append(True)
            else:
                success_list.append(False)
            
            # if an utterance was found
            if success_list[-1]:
                
                # cut the utterance to match the subsegment length
                start_librispeech, end_librispeech = cut_utterance(seg_len, start, end, selected_utt)
                
                # save info
                utt_infos = {}
                utt_infos['file'] = selected_utt['origin_path']
                utt_infos['start_librispeech'] = int(start_librispeech)
                utt_infos['end_librispeech'] = int(end_librispeech)
                utt_infos['start_mix'] = start
                utt_infos['end_mix'] = end
                
                # append the utterance to the list of utterance 
                # whose length equals the number of subsegments for the current speaker)
                utt_list.append(utt_infos)        
        
        # if success for all sugsegments, break the loop
        if all(success_list):
            success = True
            break
    
    if not success:
        raise Exception('Utterance selection failed.')
    
    return str(gender), speaker_id, utt_list, df_librispeech

def remove_duplicates(datasets):
    
    n_mix_orig = np.sum([len(x) for x in datasets])
    
    cpt = 0
    for n in range(len(datasets)):
        
        dataset = datasets[n]
        dataset_others = [x for i,x in enumerate(datasets) if i!=n]
            
        for m, mix_infos in enumerate(dataset):
            for dataset_other in dataset_others:
                for mix_infos_other in dataset_other:        
                    if mix_infos == mix_infos_other:
                        cpt += 1
                        dataset.remove(mix_infos)

    if VERBOSE:
        print('%d duplicated mixture(s) removed among %d' % (cpt, n_mix_orig))
        
    return datasets, cpt

def check_speakers_activity(spks_activity):
    
    for spk_ind in [1, 2, 3]:
        
        if spks_activity[str(spk_ind)]['is_active']:
            
            if np.sum(spks_activity[str(spk_ind)]['activity']) == 0:
                
                return False
    
    return True
    

def create_dry_mixtures(df_noise, df_seg_all, df_librispeech, subset):
    
    df_seg_all_copy = copy.deepcopy(df_seg_all)
    
    dataset = []
    
    for ind in tqdm(range(len(df_noise)), total=len(df_noise)):
            
        noise_ex = df_noise.iloc[ind]
            
        noise_filename = noise_ex['filename']
        seg_len = noise_ex['length']
        seg_dur = noise_ex['duration']
        
        mix_infos = {}
        mix_infos['length'] = int(seg_len)
        mix_infos['duration'] = seg_dur
        mix_infos['noise'] = {'subset': subset,
                              'filename': noise_filename
                              }
        
        cpt = 0
        while cpt < 200:
                       
            seg, n_spk, df_seg_all, success = get_seg(df_seg_all, seg_len, 
                                                      PROBA_SPK, n_trials=200, 
                                                      remove=True)
            
            if not success:
                if VERBOSE:
                    print('reset dataframe of segments')
                df_seg_all = copy.deepcopy(df_seg_all_copy)
                seg, n_spk, df_seg_all, success = get_seg(df_seg_all, seg_len, 
                                                          PROBA_SPK, 
                                                          n_trials=200, 
                                                          remove=True)
                
                if not success:
                    raise Exception('Segment selection failed.')
            
            # mix_infos['diarization_id'] = seg['filename'] + '_' + seg['id']
            
            spks_activity, n_spk_new = get_speaker_activity(seg, seg_len)
            
            # the activity in seg is trimmed to seg_len
            # we need to check that speakers supposed to be active 
            # remain active after trimming
            if check_speakers_activity(spks_activity):
                break
            cpt += 1
         
        if cpt==200:
            raise Exception('Trimming segment to match noise length gave an'
                            'inactive speaker who should be active.')
        
        if n_spk_new != n_spk:
            n_spk = n_spk_new
        
        # build mix of utterances from librispeech
        mix_infos['max_num_sim_active_speakers'] = n_spk_new
        
        # find librispeech utterances for each speaker and each subsegment
        spk_cpt = 1
        spk_list = []
        for spk_ind in [1, 2, 3]:
            
            if spks_activity[str(spk_ind)]['is_active']:
                
                mix_infos['speaker_' + str(spk_cpt)] = {}
                
                cpt = 0
                while cpt < 20:
                    cpt += 1
                    (gender, 
                     speaker_id, 
                     utt_list, 
                     df_librispeech) = get_spk_utterances(spks_activity,
                                                          spk_ind, 
                                                          seg_len, 
                                                          df_librispeech, 
                                                          n_trials=200)
                    if speaker_id not in spk_list:
                        break
                
                if len(utt_list) == 0:
                    raise Exception('Utterance list is empty.')
                
                spk_list.append(speaker_id)
                
                mix_infos['speaker_' + str(spk_cpt)]['gender'] = gender
                mix_infos['speaker_' + str(spk_cpt)]['ID'] = int(speaker_id)
                mix_infos['speaker_' + str(spk_cpt)]['utterances'] = utt_list
                
                spk_cpt += 1
            
        dataset.append(mix_infos)
    
    return dataset

def create_dry_dataset(librispeech_csv_file, noise_audio_path, 
                       unlabeled_data_json_path, subset, sessions_speakers, 
                       n_subsets=2):
    """
    each CHiME noise file will be used n_subsets times
    """

    subsets = []
    
    noise_file_list = get_file_list(noise_audio_path, endswith='.wav')
    df_noise_orig = create_noise_df(noise_file_list, subset)
    df_seg_all_orig = create_seg_df(unlabeled_data_json_path, subset, sessions_speakers)
    
    for n in range(n_subsets):
    
        # create dataframe of librispeech utterances
        df_librispeech = pd.read_csv(librispeech_csv_file, engine='python')
        
        # create dataframe of noises
        df_noise = copy.deepcopy(df_noise_orig)
        df_noise = df_noise.sample(frac=1, random_state=1)    
        assert len(df_noise) == len(df_noise_orig)
        
        # create dataframe of segments (diarization)
        df_seg_all = copy.deepcopy(df_seg_all_orig)
        assert len(df_seg_all) == len(df_seg_all_orig)
        
        # create dataset of mixtures
        ds = create_dry_mixtures(df_noise, df_seg_all, df_librispeech, subset)
        
        subsets.append(ds)
    
    # remove duplicates
    subsets, num_duplicates = remove_duplicates(subsets)
    _, num_duplicates = remove_duplicates(subsets)
    assert num_duplicates == 0
    
    # give a name to each mixture
    ab = ['a', 'b']
    for m, subset in enumerate(subsets):
        for n, mix in enumerate(subset):
            mix['name'] = mix['noise']['filename'] + ab[m]
    
    # concatenate created subsets
    dataset = []
    for subset in subsets: dataset.extend(subset) 
    
    # # give a name to each mixture
    # for n, mix in enumerate(dataset):
    #     mix['name'] = 'mix_' + str(n+1)
        
    return dataset

def get_rir(voicehome_path, df_voicehome, n_spk):
    
    possible_rirs = df_voicehome
    
    # draw home
    homes = possible_rirs['home'].unique()  
    home = homes[np.random.randint(0,homes.shape[0])]
    possible_rirs = possible_rirs[possible_rirs['home'] == home]
    
    # draw room
    rooms = possible_rirs['room'].unique()  
    room = rooms[np.random.randint(0,rooms.shape[0])]
    possible_rirs = possible_rirs[possible_rirs['room'] == room]
    
    # draw arrayPos
    arrayPoss = possible_rirs['arrayPos'].unique()  
    arrayPos = arrayPoss[np.random.randint(0,arrayPoss.shape[0])]
    possible_rirs = possible_rirs[possible_rirs['arrayPos'] == arrayPos]
    
    assert len(possible_rirs['arrayGeo'].unique()) == 1
    
    # draw n_spk speakerPos without replacement
    speakerPoss = possible_rirs['speakerPos'].unique()
    speakerPoss = random.sample(list(speakerPoss), n_spk)
    
    selected_rirs = []
    for speakerPos in speakerPoss:
        rir = possible_rirs[possible_rirs['speakerPos'] == speakerPos]
        assert len(rir) == 1
        selected_rirs.append(rir['file'].iloc[0])
    
    # draw a channel 
    channel = np.random.randint(0,8)
    
    # get rir length
    rir_len = []
    for rir in selected_rirs:
        f = sf.SoundFile(os.path.join(voicehome_path, rir))
        assert f.samplerate==SR_AUDIO        
        rir_len.append(f.frames)
    
    return selected_rirs, rir_len, channel

def create_reverb_dataset(dataset, voicehome_path, df_voicehome):
    
    for mix_infos in tqdm(dataset, total=len(dataset)):
        
        speakers = [x for x in list(mix_infos.keys()) if 'speaker_' in x]
        
        selected_rirs, rir_len, channel = get_rir(voicehome_path, df_voicehome, 
                                                  len(speakers))
            
        for spk_ind, spk in enumerate(speakers):
            
            spk_infos = mix_infos[spk]
            
            rir_infos = {}
            rir_infos['file'] = selected_rirs[spk_ind]
            rir_infos['length'] = rir_len[spk_ind]
            rir_infos['channel'] = channel    
            spk_infos['RIR'] = rir_infos
    
    return dataset


def sample_gaussian(mean, std):
    return mean + std*np.random.randn()

def add_SNR(dataset):
    
    for mix_infos in tqdm(dataset, total=len(dataset)):

        speakers = [x for x in list(mix_infos.keys()) if 'speaker_' in x]
        
        # sample per-mixture SNR        
        snr_mix = sample_gaussian(SNR_MEAN_MIX, SNR_STD_MIX)
        
        # for each speaker
        for spk_ind, spk in enumerate(speakers):
            
            # get speaker's infos
            spk_infos = mix_infos[spk]
            
            # sample per-speaker SNR        
            snr_spk = sample_gaussian(snr_mix, SNR_STD_SPK)
            
            # add to metadata
            spk_infos['SNR'] = snr_spk
    
    return dataset


def main():


    for subset in ['dev', 'eval']:
        
        # paths
        noise_audio_path = os.path.join(unlabeled_data_audio_path, subset, '0')
        output_path = labeled_data_json_path
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        
        # get list of speakers per session in CHiME metadata
        sessions_speakers_file ='metadata/chime/sessions_speakers.json'
        assert os.path.isfile(sessions_speakers_file)
        with open(sessions_speakers_file) as f:  
            sessions_speakers = json.load(f)
        
        # librispeech metadata csv file
        if subset == 'dev':
            librispeech_csv_file = 'metadata/librispeech/dev-clean.csv'
        elif subset == 'eval':
            librispeech_csv_file = 'metadata/librispeech/test-clean.csv'
        assert os.path.isfile(librispeech_csv_file)
        
        # create voicehome dataframe
        voicehome_csv_file = os.path.join('metadata', 'voicehome', subset + '.csv')   
        assert os.path.isfile(voicehome_csv_file)
        df_voicehome = pd.read_csv(voicehome_csv_file, engine='python')
    

        # create metadata for the "dry" mixtures
        print('initializing metadata')
        dataset = create_dry_dataset(librispeech_csv_file, noise_audio_path, 
                                     unlabeled_data_json_path, subset, sessions_speakers,
                                     n_subsets=2)
        
        # add reverberation information
        print('adding reverberation metadata')
        dataset = create_reverb_dataset(dataset, voicehome_path, df_voicehome)
        
        # add SNR information for the mixtures
        print('adding SNR metadata')
        dataset = add_SNR(dataset)
        
        output_file = os.path.join(output_path, subset + '.json')
        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=4)

if __name__ == "__main__":
   main()