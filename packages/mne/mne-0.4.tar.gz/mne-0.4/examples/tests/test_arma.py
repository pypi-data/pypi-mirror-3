import numpy as np
from scipy import signal, linalg
import pylab as pl

from nitime import utils
from nitime import algorithms as alg
from nitime.timeseries import TimeSeries
from nitime.viz import plot_tseries

from mne import fiff
from mne.datasets import sample
data_path = sample.data_path('..')

fname = data_path + '/MEG/sample/sample_audvis_raw.fif'

raw = fiff.Raw(fname)

# Set up pick list: MEG + STI 014 - bad channels
include = ['STI 014']
exclude = raw.info['bads'] + ['MEG 2443', 'EEG 053']  # bad channels + 2 more

picks = fiff.pick_types(raw.info, meg='grad', eeg=False,
                                  stim=False, include=include,
                                  exclude=exclude)

some_picks = picks[:5]
start, stop = raw.time_to_index(60, 180)
data, times = raw[some_picks, start:(stop + 1)]

drop_transients = 128
Fs = raw.info['sfreq']


from statsmodels.regression import yule_walker

rho, sigma = sm.regression.yule_walker(d, order=order, method="mle")
def yullwalker(x, order, rxx=None):
    if rxx is not None and type(rxx) == np.ndarray:
        r_m = rxx[:order + 1]
    else:
        r_m = utils.autocorr(x)[:order + 1]

    Tm = linalg.toeplitz(r_m[:order])
    y = r_m[1:]
    ak = linalg.solve(Tm, y)
    sigma_v = r_m[0].real - np.dot(r_m[1:].conj(), ak).real
    return ak, sigma_v

order = 5
coefs_est = np.empty((len(data), order))
for k, d in enumerate(data):
    # coefs, sigma = alg.AR_est_YW(d, order=order)
    coefs, sigma = yullwalker(d, order=order)
    coefs_est[k, :] = coefs

mean_coefs_est = np.mean(coefs_est, axis=0)

filt = np.concatenate([[1], - mean_coefs_est])

d = data[0]
innovation = signal.convolve(d, filt, 'valid')
d_, _, _ = utils.ar_generator(N=len(d), sigma=1., coefs=mean_coefs_est, v=innovation)
d_ = np.concatenate([d_[0] * np.ones(order), d_])

pl.close('all')
pl.psd(d, Fs=raw.info['sfreq'], NFFT=2048)
pl.psd(innovation, Fs=raw.info['sfreq'], NFFT=2048)
pl.psd(d_, Fs=raw.info['sfreq'], NFFT=2048)

pl.figure()
pl.plot(d[:100])
pl.plot(d_[:100])
pl.show()
