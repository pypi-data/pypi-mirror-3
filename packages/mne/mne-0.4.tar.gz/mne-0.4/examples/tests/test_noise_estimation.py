import numpy as np
import pylab as pl
from scipy import signal, linalg, optimize
import mne
from mne import fiff
from mne.datasets import sample
data_path = sample.data_path('.')

# # simu
# n_trials, n_sensors, n_times = 200, 30, 20
# rng = np.random.RandomState(0)
# g = rng.randn(n_sensors)
# x = signal.gaussian(n_times, std=1.)
# GX = np.dot(g[:, None], x[None, :])
# std = 10
# M = GX[None, :, :] + std * rng.randn(n_sensors, n_times, n_trials)
# norm_GX = linalg.norm(GX.ravel())


###############################################################################
# Set parameters
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_raw-eve.fif'
cov_fname = data_path + '/MEG/sample/sample_audvis-cov.fif'
# raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
# event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'
event_id, tmin, tmax = 1, -0.2, 0.5

# Setup for reading the raw data
raw = fiff.Raw(raw_fname)
events = mne.read_events(event_fname)
cov = mne.read_cov(cov_fname)

# Set up pick list: EEG + MEG - bad channels (modify to your needs)
exclude = raw.info['bads'] + ['MEG 2443', 'EEG 053']  # bads + 2 more
picks = fiff.pick_types(raw.info, meg='grad', eeg=False, stim=True, eog=True,
                            exclude=exclude)

# Read epochs
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                    picks=picks, baseline=(None, 0), preload=True,
                    reject=dict(grad=4000e-13, eog=150e-6))
idx = mne.fiff.pick_types(epochs.info, meg='grad')
ch_names = [epochs.ch_names[k] for k in idx]
cov_idx = [cov.ch_names.index(c) for c in ch_names]
cov_diag = cov.data[cov_idx, cov_idx]
std = np.sqrt(np.mean(cov_diag))
# std = 0.8e-11

M = epochs.get_data()[:, idx, :]
M = M[:, :, ::20]
n_trials, n_sensors, n_times = M.shape

norm_GX = linalg.norm(np.mean(M, axis=0).ravel())

norms = np.empty(n_trials)
K = np.arange(1, n_trials + 1)
for k in K:
    norms[k - 1] = linalg.norm(np.mean(M[:k], axis=0)) 

f = lambda k, n, s: n ** 2 + n_sensors * n_times * s ** 2 / k
(norm_GX_, std_), _ = optimize.curve_fit(f, K, norms ** 2, p0=[norm_GX, std])

pl.close('all')
pl.plot(K, norms ** 2, 'b')
pl.plot(K, norm_GX ** 2 + n_sensors * n_times * std ** 2 / K, 'r')
pl.plot(K, norm_GX_ ** 2 + n_sensors * n_times * std_ ** 2 / K, 'g')
pl.axhline(norm_GX ** 2)
pl.show()