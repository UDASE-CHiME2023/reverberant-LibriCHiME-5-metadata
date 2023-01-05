#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import os
import json

def create_list_sessions_speakers(chime_dir, output_file):
    
    # get list of transcription files (1 per session)
    file_list = []
    for root, dirs, files in os.walk(os.path.join(chime_dir, 'transcriptions')):
        for file in files:
            if file.endswith('.json'):
                 file_list.append(os.path.join(root, file))
                 
    file_list = sorted(file_list)
    
    # for each session, get list of speakers
    speakers_per_session = {}         
    for file_path in file_list:
        
        session = os.path.basename(file_path)[:-5]
        
        df = pd.read_json(file_path)
        
        # df_len = len(df)
        
        speakers = list(df['speaker'].unique())
        speakers = [sp for sp in speakers if str(sp) != 'nan']
        speakers_per_session[session] = speakers
    
    
    with open(output_file, "w") as f:
        json.dump(speakers_per_session, f, indent=1)
        
chime_dir = '/data/datasets/CHiME5' 
output_file = os.path.join('metadata/chime', 'sessions_speakers.json')
create_list_sessions_speakers(chime_dir, output_file)