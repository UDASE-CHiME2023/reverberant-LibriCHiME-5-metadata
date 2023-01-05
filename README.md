# LibriCHiME

This repository contains instructions for creating the LibriCHiME data (metadata and audio files): synthetic labeled data close to the target CHiME domain. The LibriCHiME data are used for dev and eval only.

**This repository will not be shared with participants**, we will only share the code to create the audio files from the metadata stored in json files that still need to be cleaned.

## Preparation

You must first:

 - Follow the instruction of the [unlabeled_data](https://github.com/UDASE-CHiME2023/unlabeled_data) repository to extract audio segments from the original unlabeled CHiME-5 data. 
    
 - Download the LibriSpeech [dev-clean](https://www.openslr.org/resources/12/dev-clean.tar.gz) and [test-clean](https://www.openslr.org/resources/12/test-clean.tar.gz) data. Put the data in a folder with the following structure:

    ```
    ├── dev-clean
    │   ├── 1272
    │   │   ├── 128104
    │   │   │   ├── 1272-128104-0000.flac
    │   │   │   ├── ...
    ├── test-clean
    │   ├── 1089
    │   │   ├── 134686
    │   │   │   ├── 1089-134686-0000.flac
    │   │   │   ├── ...
    ```

- Download the [VoiceHome](https://zenodo.org/record/1314196) dataset.

## Installation

```
# clone data repository
git clone https://github.com/UDASE-CHiME2023/LibriCHiME.git
cd LibriCHiME

# create CHiME conda environment (if not already existing)
conda env create -f environment.yml
conda activate CHiME
```

## Dataset creation

Set the paths in `paths.py` and run `python create_audio_from_json.py`.

LibriCHiME is split in `dev` and `eval` sets. For each set we have three subsets dependending on the number of overlapping speakers (1, 2 or 3).

At the path defined by the variable `labeled_data_audio_path` in `path.py`, you should obtain: 

```
├── dev
│   ├── 1 (3552 files)
│   │   ├── S02_P05_11b_mix.wav
│   │   ├── S02_P05_11b_noise.wav
│   │   ├── S02_P05_11b_speech.wav
│   │   ├── ...
│   ├── 2 (1683 files)
│   │   ├── S02_P05_10a_mix.wav
│   │   ├── S02_P05_10a_noise.wav
│   │   ├── S02_P05_10a_speech.wav
│   │   ├── ...
│   └── 3 (234 files)
│       ├── S02_P05_5b_mix.wav
│       ├── S02_P05_5b_noise.wav
│       ├── S02_P05_5b_speech.wav
│       ├── ...
├── eval
│   ├── 1 (4386 files)
│   │   ├── S01_P01_0a_mix.wav
│   │   ├── S01_P01_0a_noise.wav
│   │   ├── S01_P01_0a_speech.wav
│   │   ├── ...
│   ├── 2 (1314 files)
│   │   ├── S01_P01_100a_mix.wav
│   │   ├── S01_P01_100a_noise.wav
│   │   ├── S01_P01_100a_speech.wav
│   │   ├── ...
│   └── 3 (153 files)
│       ├── S01_P01_117b_mix.wav
│       ├── S01_P01_117b_noise.wav
│       ├── S01_P01_117b_speech.wav
│       ├── ...


8 directories, 11322 files
```

For each mixture in the dataset:
- `..._mix.wav` is the speech+noise mixture;
- `..._speech.wav` is the reference speech signal;
- `..._noise.wav` is the reference noise signal.

Other files in this repository are:

- `constants.py`: file that contains constants used to create LibriCHiME.
- `paths.py`: file that contains paths to the source datasets used to create LibriCHiME.
- `create_json.py`: script to create the LibriCHiME json metadata files.
- `create_chime_metadata.py`
- `create_librispeech_metadata.py`
- `create_voicehome_metadata.py`
- `utils.py`


## Dataset description

For more information, please refer to [this file](data_creation.md) describing how the dataset is generated. It also includes a TODO list.
