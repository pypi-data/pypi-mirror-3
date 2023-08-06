"""
==================================================
Common Spatial Pattern Decoding
==================================================

"""

# Author: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

print __doc__

import numpy as np
from scipy import linalg
import pylab as pl
import mne
from mne.datasets import sample
from mne.fiff import Raw, pick_types

data_path = sample.data_path('..')
fname_raw = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
fname_event = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'

event_id, tmin, tmax = 1, -0.2, 0.5
snr = 3.0
lambda2 = 1.0 / snr ** 2
dSPM = True

# Load data
raw = Raw(fname_raw)
events = mne.read_events(fname_event)

# Set up pick list
include = []
exclude = raw.info['bads'] + ['EEG 053']  # bads + 1 more

# pick MEG channels
picks = pick_types(raw.info, meg='grad', eeg=False, stim=False, eog=True,
                                            include=include, exclude=exclude)
# Read epochs
reject = dict(mag=4e-12, grad=4000e-13, eog=150e-6)
epochs0 = mne.Epochs(raw, events, 0, tmin, tmax, picks=picks,
                     baseline=(None, 0), reject=reject)
epochs1 = mne.Epochs(raw, events, 0, tmin, tmax, picks=picks,
                     baseline=(None, 0), reject=reject)

def learn_csp(X, y):
    """
    this function learns the CSP (Common Spatial Patterns) filters to
    discriminate two mental states in EEG signals

    Input:
    EEGSignals: the training EEG signals, composed of 2 classes. These signals
    are a structure such that:
       EEGSignals.x: the EEG signals as a [Ns * Nc * Nt] Matrix where
           Ns: number of EEG samples per trial
           Nc: number of channels (EEG electrodes)
           nT: number of trials
       EEGSignals.y: a [1 * Nt] vector containing the class labels for each trial
       EEGSignals.s: the sampling frequency (in Hz)

    Output:
    csp_matrix: the learnt CSP filters (a [Nc*Nc] matrix with the filters as rows)

    inspired by code from Fabien LOTTE (fabien.lotte@inria.fr)
    """

    #check and initializations
    n_trials, n_sensors, n_times = X.shape
    labels = np.unique(y)
    n_classes = len(labels)
    if n_classes != 2:
        raise ValueError('ERROR! CSP can only be used for two classes');

    cov_matrices = list()  # the covariance matrices for each class

    # computing the normalized covariance matrices for each trial
    trial_cov = np.zeros(n_sensors, n_sensors, n_trials)
    for t in range(n_trials):
        E = X[t,:,:]
        EE = np.dot(E * E.T)
        trial_cov[:,:,t] = EE / np.trace(EE)

    del E
    del EE

    # computing the covariance matrix for each class
    for c in range(n_classes):
        cov_matrices += [np.mean(trial_cov[:,:,y == labels[c]], axis=2)]

    U, D = linalg.eig(cov_matrices[0], cov_matrices[1])  # GEVD
    eigenvalues = np.diag(D)
    idx = np.argsort(eigenvalues)[::-1]
    U = U[:, idx]
    csp_matrix = U.T
    return csp_matrix

def extract_csp_features(X, y, csp_matrix, n_filter_pairs):
    """Extract features from an EEG data set using the Common Spatial Patterns (CSP) algorithm

    Input:
    EEGSignals: the EEGSignals from which extracting the CSP features. These signals
    are a structure such that:
       EEGSignals.x: the EEG signals as a [Ns * Nc * Nt] Matrix where
           Ns: number of EEG samples per trial
           Nc: number of channels (EEG electrodes)
           nT: number of trials
       EEGSignals.y: a [1 * Nt] vector containing the class labels for each trial
       EEGSignals.s: the sampling frequency (in Hz)
    csp_matrix: the CSP projection matrix, learnt previously (see function learnCSP)
    n_filter_pairs: number of pairs of CSP filters to be used. The number of
       features extracted will be twice the value of this parameter. The
       filters selected are the one corresponding to the lowest and highest
       eigenvalues

    Output:
    features: the features extracted from this EEG data set
       as a [Nt * (n_filter_pairs*2 + 1)] matrix, with the class labels as the
       last column

    inspired by Fabien LOTTE (fabien.lotte@inria.fr)
    """
    # initializations
    n_trials = X.shape[0]
    features = np.zeros(n_trials, 2 * n_filter_pairs + 1)
    csp_filter = np.r_[csp_matrix[:n_filter_pairs,:],
                       csp_matrix[-n_filter_pairs:,:]]

    # extracting the CSP features from each trial
    for t in range(n_trials):
        # projecting the data onto the CSP filters
        projected_trial = csp_filter * X[t].T

        # generating the features as the log variance of the projected signals
        variances = np.var(projected_trial, 0, axis=2)
        for f in range(len(variances)):
            features[t, f] = np.log(variances[f])

        features[t, -1] = y[t]
    return features
