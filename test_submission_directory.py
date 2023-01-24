#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 14:43:49 2023

@author: simon
"""

from paths import reverberant_librichime_5_audio_path, udase_chime_5_audio_path

from constants import SR_AUDIO
import glob
import numpy as np
import os
import soundfile as sf
import tqdm
import pandas as pd
import shutil


root_dir = '/data/tmp/submission_test'

subset = 'eval'
        

pattern = os.path.join(reverberant_librichime_5_audio_path, 
                           'eval', '*', '*_mix.wav')

reverberant_librichime_5_file_list = glob.glob(pattern)

pattern = os.path.join(udase_chime_5_audio_path, 
                           'eval', '[1-3]', '*.wav')

chime_5_file_list = glob.glob(pattern)


# file_list = reverberant_librichime_5_file_list + chime_5_file_list

file_list = []
file_list.extend(chime_5_file_list)
file_list.extend(reverberant_librichime_5_file_list)

for file in file_list:
    
    file_split = file.split(sep='/')
    
    
    file_name = file_split[-1]
    n_spk = file_split[-2]
    dataset = file_split[-4]
    
    output_dir = os.path.join(root_dir, dataset, n_spk)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, file_name)
    
    shutil.copy(file, output_path)
    