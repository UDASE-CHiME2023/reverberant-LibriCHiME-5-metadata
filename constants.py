#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

SEED = 1

# target distribution of max number of simultaneously-active speakers
# follows CHiME distribution
PROBA_SPK = [0.6, 0.35, 0.05] 

SR_DIARIZATION = 100 # sampling rate for the diarization is 1/(0.01 second)
SR_AUDIO = 16000 # sampling rate for audio files
MIN_DURATION_SUBSEG = 1.5 # min duration of speakers' activity subsegments in seconds

SNR_MEAN_MIX = 10 # per-mixture SNR mean
SNR_STD_MIX = 6.7082 # per-mixture SNR standard deviation # 5
SNR_STD_SPK = 2 # per-speaker SNR standard deviation

MAX_AMP = 0.9 # max amplitude in case of clipping


