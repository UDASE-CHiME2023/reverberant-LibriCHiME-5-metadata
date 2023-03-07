#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 15:58:42 2023

@author: simon
"""

import numpy as np
import soundfile as sf
import os
import librosa
from tqdm import tqdm
import matplotlib.pyplot as plt

def compute_si_sdr(s_hat, s_orig):
    """
    Scale Invariant SDR as proposed in
    https://www.merl.com/publications/docs/TR2019-013.pdf
    """
    eps = np.finfo(s_hat.dtype).eps
    alpha = (s_hat.T @ s_orig + eps) / (np.sum(np.abs(s_orig)**2) + eps)
    sisdr = 10*np.log10((np.sum(np.abs(alpha*s_orig)**2) + eps)/
                        (np.sum(np.abs(alpha*s_orig - s_hat)**2) + eps))
    return sisdr

for subset in ['dev', 'eval']:

    root_path = os.path.join('/data2/datasets/UDASE-CHiME2023/reverberant-LibriCHiME-5-5dB-mean-snr', subset)
    mix_file_list = librosa.util.find_files(root_path, ext='wav')
    mix_file_list = [f for f in mix_file_list if 'mix' in f]
    
    sisdr = {'1' : [], '2': [], '3': []}
    for mix_file in tqdm(mix_file_list, total=len(mix_file_list)):
        
        n_spk = os.path.split(mix_file)[0][-1]
        
        speech_file = mix_file[:-7] + 'speech.wav'
        
        s_hat, sr = sf.read(mix_file)
        s_orig, sr = sf.read(speech_file)
        
        sisdr[n_spk].append(compute_si_sdr(s_hat, s_orig))
            
    print('si-sdr on ' + subset)
    for n_spk in ['1', '2', '3']:
        print(n_spk + ' speaker(s): %.2f' % np.mean(sisdr[n_spk]))
