#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import os
import glob
from paths import voicehome_path

dev_set = {'home2': ['room1', 'room2', 'room3'],
           'home3': ['room1', 'room3']}

n_dev = 20 + 15 + 17 + 17 + 15

eval_set = {'home3': ['room2'],
            'home4': ['room1', 'room2', 'room3']}

n_eval = 16 + 18 + 16 + 16


output_dir = 'metadata/voicehome'
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
    
#%%

rir_list = glob.glob(f'{voicehome_path}/audio/rirs/*.wav')
df_rirs_dev = pd.DataFrame(columns=['home', 'room', 'arrayGeo', 'arrayPos', 'speakerPos', 'file'])
df_rirs_eval = pd.DataFrame(columns=['home', 'room', 'arrayGeo', 'arrayPos', 'speakerPos', 'file'])

rir_list.sort()

for rir in rir_list:
    
    head, tail = os.path.split(rir)
    
    [home, room, arrayGeo, arrayPos, speakerPos] = tail[:-4].split('_')
    
    row = [home, room, arrayGeo, arrayPos, speakerPos]
    
    row.extend([os.path.join('audio', 'rirs', tail)])
    
    if home in dev_set.keys():
        if room in dev_set[home]:
            df_rirs_dev.loc[len(df_rirs_dev)] = row
        
    if home in eval_set.keys():
        if room in eval_set[home]:
            df_rirs_eval.loc[len(df_rirs_eval)] = row
        
df_rirs_dev.to_csv(os.path.join(output_dir,'dev.csv'))
assert len(df_rirs_dev) == n_dev
df_rirs_eval.to_csv(os.path.join(output_dir,'eval.csv'))
assert len(df_rirs_eval) == n_eval
#%%

arrayPos_list = glob.glob(f'{voicehome_path}/annotations/rooms/*arrayPos*')

arrayPos_list.sort()


df_arrayPos = pd.DataFrame(columns=['home', 'room', 'arrayPos', 'text', 'x', 'y', 'z', 'azimuth', 'elevation'])

for ar in arrayPos_list:
    
    head, tail = os.path.split(ar)
    
    row = tail[:-4].split('_')
    
    with open(ar) as f:
        lines = f.readlines()
        assert len(lines) == 1
    
    row.extend(lines[0].split('\t'))
    
    df_arrayPos.loc[len(df_arrayPos)] = row
    
df_arrayPos.to_csv(os.path.join(output_dir,'arrayPos.csv'))


#%%

speakerPos_list = glob.glob(f'{voicehome_path}/annotations/rooms/*speakerPos*')

speakerPos_list.sort()

df_speakerPos = pd.DataFrame(columns=['home', 'room', 'speakerPos', 'text', 'x', 'y', 'z', 'azimuth', 'elevation'])

for ar in speakerPos_list:
    
    head, tail = os.path.split(ar)
    
    row = tail[:-4].split('_')
        
    with open(ar) as f:
        lines = f.readlines()
        assert len(lines) == 1
    
    data = lines[0].split('\t')
    if len(data) < 6:
        data.extend([''] * (6-len(data)))
    
    row.extend(data)
    
    df_speakerPos.loc[len(df_speakerPos)] = row

df_speakerPos.to_csv(os.path.join(output_dir,'speakerPos.csv'))

#%%

arrayGeo_list = glob.glob(f'{voicehome_path}/annotations/arrays/arrayGeo*')

arrayGeo_list.sort()

df_arrayGeo = pd.DataFrame(columns=['arrayGeo', 'channel', 'mic', 'x', 'y', 'z'])

for ar in arrayGeo_list:
    
    head, tail = os.path.split(ar)
    
    arrayGeo = tail[:-4]
    
    
            
    with open(ar) as f:
        lines = f.readlines()
    
    channel = 0
    for line in lines:
        data = line.split('\t')
        row = [arrayGeo] + [channel] + data
        df_arrayGeo.loc[len(df_arrayGeo)] = row
        channel += 1
    
df_arrayGeo.to_csv(os.path.join(output_dir,'arrayGeo.csv'))
