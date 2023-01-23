#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script checks that the sum of the speech and noise signals
in the reverberant LibriCHiME-5 dataset is equal to the mixture signal,
up to the quantization error (PCM 16 wav files)
"""

from paths import reverberant_librichime_5_audio_path
from constants import SR_AUDIO
import glob
import numpy as np
import os
import soundfile as sf
import tqdm
import pandas as pd

df_diff = pd.DataFrame(columns=['file', 'difference'])

for subset in ['dev', 'eval']:
        
    for n_spk in ['1', '2', '3']:
        
        pattern = os.path.join(reverberant_librichime_5_audio_path, 
                                   subset, n_spk, '*_mix.wav')
        
        file_list = glob.glob(pattern)
        
        for file in file_list:
            
            head, tail = os.path.split(file)
            
            basename = tail[:-8]
            
            mix, sr = sf.read(os.path.join(head, basename + '_mix.wav'))
            
            speech, sr = sf.read(os.path.join(head, basename + '_speech.wav'))
            
            noise, sr = sf.read(os.path.join(head, basename + '_noise.wav'))
            
            row = [file, np.mean(mix - (speech + noise))]
            
            df_diff.loc[len(df_diff)] = row
            

print('max error: %.2e' % df_diff['difference'].max())
print('quantization error: %.2e' % (1/(2**16)))