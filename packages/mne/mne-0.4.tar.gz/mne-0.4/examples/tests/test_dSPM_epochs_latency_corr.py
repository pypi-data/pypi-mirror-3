"""
==============================================================================
Compute TF-based sparse solver based on L1 + L1/L2 mixed norm on single epochs
==============================================================================

See
D. Strohmeier et al.
to be written :)
"""
# Authors:   Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#            Daniel Strohmeier <daniel.strohmeier@tu-ilmenau.de>
#
# License: BSD (3-clause)

print __doc__

import pylab as pl
import numpy as np
import mne

from mne import fiff
from mne.datasets import sample
from mne.minimum_norm import make_inverse_operator, apply_inverse_epochs

###############################################################################
# Set parameters
data_path = sample.data_path('.')
fwd_fname = data_path + '/MEG/sample/sample_audvis-meg-eeg-oct-6-fwd.fif'
cov_fname = data_path + '/MEG/sample/sample_audvis-cov.fif'
# raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
# event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'
# raw_fname = data_path + '/MEG/sample/sample_audvis_filt-1-80_raw.fif'
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_raw-eve.fif'

label_name = 'Aud-lh'
fname_label_lh = data_path + '/MEG/sample/labels/%s.label' % label_name
label_name = 'Aud-rh'
fname_label_rh = data_path + '/MEG/sample/labels/%s.label' % label_name

event_id, tmin, tmax = 1, -0.0, 0.2
# event_id, tmin, tmax = 2, -0.0, 0.2
tbaseline_start = -0.220
# tbaseline_start = None
baseline = (None, 0)
# baseline = None  # valid if prior highpass
# tbaseline_start = None

# Setup for reading the raw data
raw = fiff.Raw(raw_fname, preload=True)
events = mne.read_events(event_fname)

# Set up pick list: EEG + MEG - bad channels (modify to your needs)
exclude = raw.info['bads'] + ['MEG 2443', 'EEG 053']  # bads + 2 more
picks = fiff.pick_types(raw.info, meg=True, eeg=True, stim=True, eog=True,
                        exclude=exclude)

raw.band_pass_filter(picks, 1, 30)

## picks = fiff.pick_types(raw.info, meg='grad', eeg=True, stim=True, eog=True,
##                         exclude=exclude)

ecg_proj = mne.read_proj(data_path + '/MEG/sample/ecg_proj.fif')
# ecg_proj = mne.read_proj(data_path + \
#         '/MEG/sample/sample_audvis_ecg_proj.fif')
raw.info['projs'] += ecg_proj  # add ecg_proj to the list of projection vectors

# Read epochs
if tbaseline_start is not None:
    epochs = mne.Epochs(raw, events, event_id, tbaseline_start, tmax, proj=True,
                        picks=picks, baseline=baseline, preload=False,
                        reject=dict(grad=4000e-13, eog=150e-6))
else:
    epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                        picks=picks, baseline=baseline, preload=False,
                        reject=dict(grad=4000e-13, eog=150e-6))

# Read noise covariance matrix
cov = mne.read_cov(cov_fname)
cov = mne.cov.regularize(cov, epochs.info)

# Handling forward solution
# forward = mne.read_forward_solution(fwd_fname, force_fixed=True)
forward = mne.read_forward_solution(fwd_fname, force_fixed=False,
                                   surf_ori=True)
label_lh = mne.read_label(fname_label_lh)
label_rh = mne.read_label(fname_label_rh)

###############################################################################
# Run solver

# Compute dSPM solution to be used as weights in MxNE
loose, depth = 0.2, 0.8  # loose orientation & depth weighting
inverse_operator = make_inverse_operator(epochs.info, forward, cov,
                                         loose=loose, depth=depth)

# Compute inverse solution and stcs for each epoch
snr = 1.0
lambda2 = 1.0 / snr ** 2
dSPM = False

def epochs_label_mean(label):
    stcs = apply_inverse_epochs(epochs, inverse_operator, lambda2, dSPM, label,
                                pick_normal=False)
                                # pick_normal=True)
    [s.crop(0, 0.150) for s in stcs]
    data = np.array([stc.data for stc in stcs]) / len(stcs)
    # compute sign flip to avoid signal cancelation when averaging signed values
    # flip = mne.label_sign_flip(label_lh, inverse_operator['src'])
    # label_lh_mean = np.mean(flip[np.newaxis, :, np.newaxis] * data, axis=1)
    label_mean = np.mean(data, axis=1)
    return label_mean, stcs

label_lh_mean, stcs = epochs_label_mean(label_lh)
label_rh_mean, stcs = epochs_label_mean(label_rh)

pl.figure(3)
pl.clf()
times = 1e3 * stcs[0].times
for k in range(label_lh_mean.shape[0]):
    pl.plot(times, label_lh_mean[k], 'b', linewidth=2)
    pl.plot(times, label_rh_mean[k], 'r', linewidth=2)
pl.xlabel('Time (ms)', fontsize=18)
pl.ylabel('Source amplitude (nAm)', fontsize=18)
pl.show()

# scatter plot of latencies
idx0 = np.argmax(label_lh_mean, axis=1)
idx1 = np.argmax(label_rh_mean, axis=1)
times0 = times[idx0]
times1 = times[idx1]

n_trials = len(label_lh_mean)
amps0 = label_lh_mean[np.arange(n_trials), idx0]
amps1 = label_rh_mean[np.arange(n_trials), idx1]

inliers = np.where((times0 > 60) & (times0 < 130)
                   & (times1 > 60) & (times1 < 130))[0]
times0 = times0[inliers]
times1 = times1[inliers]
amps0 = amps0[inliers]
amps1 = amps1[inliers]

from scipy import stats

def corr_analysis(x_coords, y_coords, label, fignumber=None):
    r_from_corr, p_from_corr = stats.pearsonr(x_coords, y_coords)
    slope, y_intercept, r_from_regression, p_from_regression, std_err = \
                               stats.linregress(x_coords, y_coords)
    pl.figure(fignumber)
    pl.clf()
    pl.scatter(x_coords, y_coords)
    xlim = np.array(pl.xlim())
    pl.plot(xlim, y_intercept + slope * xlim,'r-')
    pl.xlabel(label)
    pl.ylabel(label)
    pl.title('R2=%2.2f - p=%1.3f' % (r_from_corr, p_from_corr))
    print "r_from_corr, p_from_corr"
    print r_from_corr, p_from_corr


corr_analysis(1e9 * amps0, 1e9 * amps1, label='Amp. (nAm)', fignumber=10)
corr_analysis(times0, times1, label='T (ms)', fignumber=11)

pl.show()
