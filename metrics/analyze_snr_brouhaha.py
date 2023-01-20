#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 15:40:41 2023

@author: sleglaive
"""

import numpy as np
import matplotlib.pyplot as plt
import os


root_path = './brouhaha'

plt.close('all')

for mu in ['10', '5']:

    for subset in ['dev', 'eval']:
        
        
        fig, ax = plt.subplots(2,1)
        plt.title(subset)
        
        #%%
        
        file = os.path.join(root_path, 'CHiME-5', subset, '1', 'mean_snr_labels.txt')
        
        chime = {'file': [], 'snr': []}
        with open(file) as f:
            lines = f.readlines()
        
        for line in lines:
            (file, snr) = line.split(' ')
            (snr, _) = snr.split('\n')
            snr = float(snr)
            chime['file'].append(file)
            chime['snr'].append(snr)
        
        ax[0].hist(chime['snr'], density=True, bins=50, alpha=1)
        ax[0].set_xlim([-10,50])
        ax[0].set_title('CHiME-5 - ' + subset + ' set')
        
        #%%
        
        file = os.path.join(root_path, 'reverberant-LibriCHiME-5-' + mu + 'dB-mean-snr', 
                            subset, '1', 'mean_snr_labels.txt')
        
        librichime = {'file': [], 'snr': []}
        with open(file) as f:
            lines = f.readlines()
        
        for line in lines:
            (file, snr) = line.split(' ')
            (snr, _) = snr.split('\n')
            snr = float(snr)
            librichime['file'].append(file)
            librichime['snr'].append(snr)
        
        ax[1].hist(librichime['snr'], density=True, bins=50, alpha=1)
        ax[1].set_xlim([-10,50])
        ax[1].set_title('Reverberant LibriCHiME-5 - ' + mu + ' dB mean SNR - ' + subset + ' set')
        
        
        plt.tight_layout()
        
        plt.savefig(mu + subset + '.png')