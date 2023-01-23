#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:21:19 2023

@author: sleglaive
"""

from paths import reverberant_librichime_5_audio_path
from constants import SR_AUDIO
import glob
import numpy as np
import os
import soundfile as sf
import tqdm
import pandas as pd

def time_sec_to_str(sec, n_msec=2):
    ''' 
    Convert seconds to 'D days, HH:MM:SS.FFF' 
    https://stackoverflow.com/a/33504562
    '''

    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    if n_msec > 0:
        pattern = '%%01d:%%02d:%%0%d.%df' % (n_msec+3, n_msec)
    else:
        pattern = r'%01d:%02d:%02d'
        
    if d == 0:
        return pattern % (h, m, s)
    
    return ('%d days, ' + pattern) % (d, h, m, s)

dataset = {'dev': {'1': [], '2': [], '3': []}, 
           'eval': {'1': [], '2': [], '3': []}}


for subset in list(dataset.keys()):
        
    for n_spk in list(dataset[subset].keys()):
        
        pattern = os.path.join(reverberant_librichime_5_audio_path, 
                                   subset, n_spk, '*_mix.wav')
        
        file_list = glob.glob(pattern)
        
        for file in file_list:
            
            f = sf.SoundFile(file)
            dataset[subset][n_spk].append(f.frames)
            
            

df_dict = {'dev': pd.DataFrame(columns=['n_spk', 'n_seg', 'mean_dur', 'std_dur', 'tot_dur']),
           'eval': pd.DataFrame(columns=['n_spk', 'n_seg', 'mean_dur', 'std_dur', 'tot_dur'])}


for subset in list(dataset.keys()):
        
    for n_spk in list(dataset[subset].keys()):    
    
        lengths = dataset[subset][n_spk]
        
        mean_dur = np.mean(lengths)/SR_AUDIO
        std_dur = np.std(lengths)/SR_AUDIO
        tot_dur = np.sum(lengths)/SR_AUDIO
        
        row = [n_spk, len(lengths), np.round(mean_dur, 2), 
               np.round(std_dur, 2), time_sec_to_str(tot_dur, n_msec=0)]
        
        df_dict[subset].loc[len(df_dict[subset])] = row
    
    # df_dict[subset].to_csv(subset + '.csv')
        
        