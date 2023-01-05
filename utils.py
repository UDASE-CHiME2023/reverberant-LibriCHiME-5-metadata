#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import os
import json
import matplotlib.pyplot as plt


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
                
        speakers = list(df['speaker'].unique())
        speakers = [sp for sp in speakers if str(sp) != 'nan']
        speakers_per_session[session] = speakers
    
    
    with open(output_file, "w") as f:
        json.dump(speakers_per_session, f, indent=1)


def get_segments_start_end(segmentation):
    """
    Given a list of binary values, returns the lists of starting and ending 
    indices of the segments with elements equal to one.
    """
    starts = []
    ends = []
    
    start_bool = True
    end_bool = False
    
    for i, val in enumerate(segmentation):
        if start_bool and val==1:
            starts.append(i)
            start_bool = False
            end_bool = True
        elif end_bool and val==0:
            ends.append(i)
            end_bool = False
            start_bool = True
    
    if len(ends) < len(starts):
        ends.append(len(segmentation))
        
    assert len(ends) == len(starts)
    
    for (start, end) in zip(starts, ends):
        assert all(x==1 for x in segmentation[start:end])
    
    return starts, ends
        

def test_start_end_seg():

    seg_1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    seg_2 = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    seg_3 = [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    seg_4 = [x*-1 + 1 for x in seg_1]
    seg_5 = [x*-1 + 1 for x in seg_2]
    seg_6 = [x*-1 + 1 for x in seg_3]
    
    segs = [seg_1, seg_2, seg_3, seg_4, seg_5, seg_6]
    
    plt.close('all')
    fig, ax = plt.subplots(6,1)
    
    for i, seg in enumerate(segs):
        
        starts, ends = get_segments_start_end(seg)
                
        ax[i].plot(seg)
        for (start, end) in zip(starts, ends):
            ax[i].plot((start, start), (0, 1), '--g')
            ax[i].plot((end-1, end-1), (0, 1), '-.r')
            



