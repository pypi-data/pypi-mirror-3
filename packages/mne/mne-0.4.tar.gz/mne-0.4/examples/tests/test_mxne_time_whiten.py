"""
================================================================
Compute sparse inverse solution based on L1/L2 mixed norm (MxNE)
================================================================

See
Gramfort A., Kowalski M. and Hamalainen, M,
Mixed-norm estimates for the M/EEG inverse problem using accelerated
gradient methods, Physics in Medicine and Biology, 2012
http://dx.doi.org/10.1088/0031-9155/57/7/1937
"""
# Author: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

print __doc__

import numpy as np
from scipy import signal
import mne
from mne import fiff
from mne.time_frequency import ar_raw
from mne.viz import plot_cov
from mne.datasets import sample
from mne.minimum_norm import apply_inverse, make_inverse_operator
from mne.mixed_norm import mixed_norm
from mne.viz import plot_sparse_source_estimates, plot_evoked
data_path = sample.data_path('..')

###############################################################################
# Set parameters
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
fwd_fname = data_path + '/MEG/sample/sample_audvis-meg-eeg-oct-6-fwd.fif'
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

whiten = False
whiten = True

picks = mne.fiff.pick_types(raw.info, meg='grad', exclude=raw.info['bads'])
order = 5  # define model order
picks = picks[:5]
coefs = ar_raw(raw, order=order, picks=picks, tmin=60, tmax=180)
mean_coefs = np.mean(coefs, axis=0)  # mean model accross channels
filt = np.r_[1, -mean_coefs]  # filter coefficient

# pick EEG channels
picks = fiff.pick_types(raw.info, meg=True, eeg=False, stim=False, eog=True,
                                            include=include, exclude=exclude)
# Read epochs
reject = dict(grad=4000e-13, mag=4e-12, eog=150e-6)
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                    baseline=(None, 0), reject=reject, preload=True)
tmp = epochs.average()
tmp.crop(0, 0.3)
times_init = tmp.times

if whiten:
    n_epochs, n_channels, n_times = epochs._data.shape
    data = np.empty((n_epochs, n_channels, n_times - len(filt) + 1))
    for d_, d in zip(data, epochs._data):
        d_[:] = signal.convolve2d(d, filt[None, :], 'valid')
    epochs.times = epochs.times[len(mean_coefs):]

baselines = epochs.crop(None, 0, copy=True)
evoked = epochs.average()  # average epochs and get an Evoked dataset.

cov = mne.compute_covariance(baselines, keep_sample_mean=True)

plot_cov(cov, raw.info, exclude=raw.info['bads'], colorbar=True,
             proj=True)  # try setting proj to False to see the effect

evoked.crop(tmin=0, tmax=0.3)

# Handling forward solution
forward = mne.read_forward_solution(fwd_fname, force_fixed=True,
                                    surf_ori=True)
# cov = mne.cov.regularize(cov, evoked.info)

import pylab as pl
pl.figure(-2)
ylim = None
# ylim = dict(eeg=[-10, 10], grad=[-300, 300], mag=[-600, 600])
plot_evoked(evoked, ylim=ylim, proj=True)

###############################################################################
# Run solver
alpha = 30  # regularization parameter between 0 and 100 (100 is high)
loose, depth = 0.2, 0.9  # loose orientation & depth weighting

# Compute dSPM solution to be used as weights in MxNE
inverse_operator = make_inverse_operator(evoked.info, forward, cov,
                                         loose=loose, depth=depth)
stc_dspm = apply_inverse(evoked, inverse_operator, lambda2=1. / 9.,
                         method='dSPM')

# Compute MxNE inverse solution
stc, residual = mixed_norm(evoked, forward, cov, alpha, loose=loose,
                 depth=depth, maxit=3000, tol=1e-4, active_set_size=10,
                 debias=True, weights=stc_dspm, weights_min=3.,
                 return_residual=True)

if whiten:
    d_ = signal.lfilter([1], filt, stc.data, axis=1)  # regenerate the signal
    # d_ = np.c_[d_[:, :1] * np.ones((1, order)), d_]  # dummy samples to keep signal length
    stc.data = d_
    stc.times = times_init
    stc.save('mxne_whiten')
else:
    stc.save('mxne')

pl.figure(-3)
plot_evoked(residual, ylim=ylim, proj=True)

###############################################################################
# View in 2D and 3D ("glass" brain like 3D plot)
plot_sparse_source_estimates(forward['src'], stc, bgcolor=(1, 1, 1),
                             opacity=0.1, fig_name="MxNE (cond %s)" % event_id,
                             fig_number=event_id)
