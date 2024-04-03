# Reverberant LibriCHiME-5 dataset

This document describes how the labeled data close to the target CHiME domain are generated. The reverberant LibriCHiME-5 data are used for dev and eval only.

## Create metadata for the mixtures without reverberation

 - Build a dataframe for the utterances in LibriSpeech. I used a script from LibriMix, which was modified to add the possibility of trimming leading and trailing silences. I did not force the min duration of 3 seconds as in conversational speech we might have short utterances.
- Build dataframes for the segments in CHiME-5 data with maximum 1, 2 and 3 simultaneously-active speakers (we here use the json files created when preparing the unlabeled in-domain data). Each segment contains the speakers' voice activity as provided by the diarization labels. We only consider segments with subsegments of duration higher than 1.5 seconds.
- Build a dataframe for the noise files (segments without active speaker) in CHiME-6 data.

- Repeat twice (to reach a sufficient amount of data):
    - Shuffle the noise dataframe.
    - For each noise file of length $\ell_m$:
        - Draw a number of speakers $n_{spk} \in \{1,2,3\}$ with probabilities $[0.6, 0.35, 0.05]$.
        - Find the CHiME segment with maximum  $n_{spk}$ whose length is closest (and at least equal) to $\ell_m$ and remove it from the list of available segments. 
        - Trim the segment if necessary (we take the first $\ell_m$ samples). Check that the number of simultaneously-active speakers is still equal to $n_{spk}$ and that all speakers supposed to be active are still active.
        - For each active speaker in the segment of length $\ell_m$
            - Get the list of subsegments (start and end indices) where the speaker is active.
            - Sample a speaker from LibriSpeech with equal probability to be a male or female.
            - For each subsegment of length $\ell_u$ in the list:
                - If the subsegment is at the beginning of the segment, then use the last $\ell_u$ samples of the utterance with length that is closest (and at least equal) to $\ell_u$. 
                - If the subsegment is at the end of the segment, then use the first $\ell_u$ samples of the utterance with length that is closest (and at least equal) to $\ell_u$.
                - If the subsegment starts and ends in the middle of the segment, or if it spans the entire segment, then use the first $\ell_u$ samples of the utterance with length that is closest (and at least equal) to $\ell_u$.
                - Remove the utterance from the list of available utterances.
        - Add entry to the mixtures dataset.
    - Reset the dataframes of segments and utterances.
- Remove duplicates

This process results in more than three hours of data for dev (about 1800 mixtures) and for eval (about 1900 mixtures).

## Add reverberation to metadata

[VoiceHome](https://zenodo.org/record/1314196) contains RIRs recorded in 12 different rooms of 3 real homes, with 4 rooms per home: living room (room 1), kitchen (room 2), bedroom (room 3), bathroom (room 4). In each room, recordings were performed for 2 different positions and geometries of an 8-channel microphone array and 7 to 9 different positions of the loudspeaker. These positions span a range of angles and are distributed logarithmically across distance. 

For more information, refer to corresponding publication:

> N. Bertin, E. Camberlein, E. Vincent, R. Lebarbenchon, S. Peillon, E. Lamandé, S. Sivasankaran, F. Bimbot, I. Illina, A. Tom, S. Fleury and E. Jamet, [A French corpus for distant-microphone speech processing in real homes](https://hal.inria.fr/hal-01343060), Interspeech, 2016.

We choose not to use the RIRs recorded in bathrooms.

VoiceHome RIRs are split in dev and eval sets:

- Dev (84 8-channel RIRs):
    - Home 2 (room 1, room 2 and room 3)
    - Home 3 (room 1, room 3)

- Eval (66 8-channel RIRs):
    - Home 3 (room 2)
    - Home 4 (room 1, room 2 and room 3)

We add the reverberation metadata as follows:

- For each mixture in the dataset:
    - Sample a home, a room, and an array position/geometry.
    - Sample $n_{spk}$ speaker positions without replacement, where $n_{spk}$ is equal to the number of speakers in the mixture.
    - Sample a channel.
    - For each speaker, add to the metadata the selected single-channel RIR.

## Create mixtures

Speech+noise mixtures are created such that per-speaker SNR is Gaussian with a mean and a standard deviation chosen to match the SNR distribution of the CHiME-5 data as estimated by [Brouhaha](https://github.com/marianne-m/brouhaha-vad) (see [this document](./Reverberant%20LibriCHiME-5%20-%20input%20SNR%20study.pdf) for more details). This is done by first sampling a global (per-mixture) SNR $x \sim \mathcal{N}(\mu, \sigma_1^2)$ and then sampling a local per-speaker SNR $y \sim \mathcal{N}(x, \sigma_2^2)$ with $\mu = 5$, $\sigma_2 = 2$, and $\sqrt{\sigma_1^2 + \sigma_2^2} = 7 \Leftrightarrow \sigma_1 = 6.7082$. The value of $\sigma_2$ is chosen such that the loudness difference between multiple speakers remains reasonable, to simulate a conversation. 

More precisely, the mixtures are created as follows.

- For each mixture in the dataset:
    - Sample $x \sim \mathcal{N}(\mu, \sigma_1^2)$
    - For each speaker:
        - For each utterance (subsegment)
            - Convolve the "dry" utterance with the corresponding RIR.
            - If the utterance is at the beginning of the mixture, clip the beginning of the reverberant signal so that the reverberant tail is preserved and the reverberant signal fits in the subsegment.
            - If the utterance is at the end of the mixture or if it spans the entire mixture, clip the end of the reverberant signal so that it fits in the subsegment.
            - If the utterance starts and ends in the middle of the mixture, do not clip and allow the unintelligible reverberant tail to extend beyond initial utterance length.
        - Sample an SNR from $\mathcal{N}(x, \sigma_2^2)$.
        - Compute the gain for scaling the reverberant speech signal to reach the above-sampled SNR. 
        - Scale the reverberant speech signal.
    - Sum the scaled reverberant speech signals and the noise signal.
    - In case of clipping, normalize speech, noise and mixture by the same factor to avoid clipping and preserve SNR.




