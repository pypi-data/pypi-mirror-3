"""
======================================
Test MxNE with bootstrapping of epochs
======================================

"""
# Authors:   Daniel Strohmeier <daniel.strohmeier@tu-ilmenau.de>
#            Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>

print __doc__

import sys
import multiprocessing

sys.path = sorted(sys.path)[::-1]
import matplotlib
matplotlib.use('Agg')  # avoids to start X

import numpy as np

from joblib import Parallel, delayed

import mne
from mne import fiff
from mne.datasets import sample
from mne.mixed_norm.inverse import mixed_norm
from mne.minimum_norm.inverse import _make_stc
from mne.minimum_norm import make_inverse_operator, apply_inverse

###############################################################################
# Parse command line

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-a", "--alpha", dest="alpha", default=30,
                help="alpha reg param")
parser.add_option("-e", "--event-id", dest="event_id", default=1,
                help="event_id")
parser.add_option("-n", "--n-boostrap", dest="n_bootstrap_iter",
                help="n_bootstrap_iter", default=40)
parser.add_option("-j", dest="n_jobs", default=min(32, multiprocessing.cpu_count()),
                help="n_jobs")
parser.add_option("-i", "--maxit", dest="maxit", default=3000,
                help="max iter in MxNE")
parser.add_option("-w", dest="window_length", default=50,
                help="window in ms")
parser.add_option("-o", dest="overlap", default=0.5,
                help="overlap")

options, args = parser.parse_args()

suffix = 'eventid%d_iter%d_alpha%s_maxit%d_win%s' % (int(options.event_id),
            int(options.n_bootstrap_iter), options.alpha, int(options.maxit),
            str(options.window_length))

event_id = int(options.event_id)
alpha = float(options.alpha)
n_bootstrap_iter = int(options.n_bootstrap_iter)
maxit = int(options.maxit)
n_jobs = int(options.n_jobs)
window_length = float(options.window_length) * 1e-3
overlap = float(options.overlap * window_length)  # 50% overlap
tstep = window_length - overlap

###############################################################################
# code

def run_bst_mxne(src, epochs, random_state, forward, cov,
                 alpha, loose, depth, weights, weights_min, maxit=3000,
                 tol=1e-4, active_set_size=50):
    n_sources_lh = len(forward['src'][0]['inuse'])
    vertnos = np.r_[forward['src'][0]['vertno'],
                    n_sources_lh + forward['src'][1]['vertno']]
    evoked = mne.epochs.bootstrap(epochs, random_state=random_state).average()
    stc = mixed_norm(evoked, forward, cov, alpha, loose=loose, depth=depth,
                     maxit=maxit, tol=tol, active_set_size=active_set_size,
                     weights=weights, weights_min=weights_min, debias=False)
    sel_vertnos = np.r_[stc.vertno[0], n_sources_lh + stc.vertno[1]]
    idx_active = np.searchsorted(vertnos, sel_vertnos)
    res = np.zeros(len(vertnos), dtype=np.int)
    res[idx_active] = 1
    return res

###############################################################################
# Define data paths
data_path = sample.data_path('..')
fwd_fname = data_path + '/MEG/sample/sample_audvis-meg-eeg-oct-6-fwd.fif'
cov_fname = data_path + '/MEG/sample/sample_audvis-cov.fif'
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_raw-eve.fif'

# Define parameters for loading epochs and forward
# event_id, tmin, tmax = 4, -0.1, 0.3
tmin, tmax = -0.1, 0.3
baseline = (None, 0)
# loose, depth = None, 0.8
loose, depth = None, 1.0

# Load raw, events, cov
raw = fiff.Raw(raw_fname, preload=False)
events = mne.read_events(event_fname)
cov = mne.read_cov(cov_fname)

# Define bads and exclude them
raw.info['bads'] = ['MEG 2443', 'EEG 053']
exclude = raw.info['bads']

# Load forward solution with fixed orientation
forward = mne.read_forward_solution(fwd_fname, force_fixed=True,
                                    surf_ori=True, exclude=exclude)

# Define picks and reject
picks = fiff.pick_types(raw.info, meg=True, eeg=True, stim=True,
                        eog=True, exclude=exclude)
reject = dict(grad=200e-12, mag=4e-12, eeg=100e-6, eog=100e-6)

# Read epochs with preload=True
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                    picks=picks, baseline=baseline, preload=True,
                    reject=reject)
tmin = - 0.05
epochs.crop(tmin, None)
evoked = epochs.average()

# Regularize noise covariance matrix
cov = mne.cov.regularize(cov, epochs.info)

# Remove raw and events as they are no longer needed
del raw, events

# Compute dSPM for weighting
inverse_operator = make_inverse_operator(evoked.info, forward, cov,
                                         loose=loose, depth=depth)


# No weighting is applied
weights, weights_min = None, None

# Run sliding window
act_maps = list()
tmin_window = tmin
tmax_window = tmin_window + window_length
while tmax_window <= epochs.tmax:
    epochs_crop = epochs.crop(tmin_window, tmax_window, copy=True)
    tmin_window = tmax_window - overlap
    tmax_window = tmin_window + window_length
    weights = apply_inverse(epochs_crop.average(), inverse_operator,
                            lambda2=1. / 9., method='dSPM')
    weights_min = 0.
    res = Parallel(n_jobs=n_jobs)(delayed(run_bst_mxne)(forward['src'],
                                                    epochs_crop, random_state,
                                                    forward, cov, alpha, loose,
                                                    depth, weights,
                                                    weights_min, maxit=maxit,
                                                    tol=1e-4,
                                                    active_set_size=50)
                            for random_state in range(n_bootstrap_iter))
    act_maps.append(np.mean(res, axis=0))
act_maps = np.vstack(act_maps).T

# Create and save stc file
stc_final = _make_stc(act_maps, tmin + window_length * 0.5, tstep,
                      [forward['src'][0]['vertno'],
                       forward['src'][1]['vertno']])
save_fname = data_path + '/MEG/sample/sample_audvis_bootstrap_' + suffix
stc_final.save(save_fname)
