"""
========================================================
Extract epochs, average and save evoked response to disk
========================================================

This script shows how to read the epochs from a raw file given
a list of events. The epochs are averaged to produce evoked
data and then saved to disk.

"""
# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

print __doc__

import numpy as np
import mne
from mne import fiff
from mne.viz import plot_cov
from mne.datasets import sample
from mne.minimum_norm import apply_inverse, make_inverse_operator
data_path = sample.data_path('..')

###############################################################################
# Set parameters
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_raw-eve.fif'
fname_fwd = data_path + '/MEG/sample/sample_audvis-meg-oct-6-fwd.fif'

event_id, tmin, tmax = 1, -0.2, 0.5

#   Setup for reading the raw data
raw = fiff.Raw(raw_fname)
events = mne.read_events(event_fname)
forward = mne.read_forward_solution(fname_fwd, surf_ori=True)

#   Set up pick list: EEG + STI 014 - bad channels (modify to your needs)
include = []  # or stim channels ['STI 014']
exclude = raw.info['bads']

diff = False
diff = True

# pick EEG channels
picks = fiff.pick_types(raw.info, meg=True, eeg=False, stim=False, eog=True,
                                            include=include, exclude=exclude)
# Read epochs
reject = dict(grad=4000e-13, mag=4e-12, eog=150e-6)
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                    baseline=(None, 0), reject=reject, preload=True)
baselines = epochs.crop(None, 0)

if diff:
    epochs._data = np.diff(epochs._data, axis=2)
    epochs.times = epochs.times[1:]

evoked = epochs.average()  # average epochs and get an Evoked dataset.

if diff:
    baselines._data = np.diff(baselines._data, axis=2)
    baselines.times = baselines.times[1:]

noise_cov = mne.compute_covariance(baselines, keep_sample_mean=True)

plot_cov(noise_cov, raw.info, exclude=raw.info['bads'], colorbar=True,
             proj=True)  # try setting proj to False to see the effect

# inverse_operator = make_inverse_operator(evoked.info, forward, noise_cov,
#                                     loose=0.2, depth=0.8)
# 
# snr = 3.0
# lambda2 = 1.0 / snr ** 2
# dSPM = True
# stc = apply_inverse(evoked, inverse_operator, lambda2, dSPM, pick_normal=True)
# 
# if diff:
#     stc.data = np.cumsum(stc.data, axis=1)
#     stc.save('pouet_diff')
# else:
#     stc.save('pouet')
