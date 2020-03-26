"""
=================
04. Plot contrast
=================

Grand-average group contrasts for dSPM
"""
import os
import json
import pprint
import os.path as op
import numpy as np
from mayavi import mlab
import mne


# Relative path
rel_path = op.split(op.realpath(__file__))[0]
print(rel_path)

# Read experiment params as json
params = json.load(open(op.join(rel_path, "params.json")))
pprint.pprint({'parameters': params})

data_type = params["data_type"]
subject_ids = params["subject_ids"]
NJOBS = params["NJOBS"]
session_ids = params["session_ids"]
conditions = params["conditions"]
exclude_subjects = params["exclude_subjects"]

if "data_path" in params.keys():
    data_path = op.join(params["data_path"], "data_demo")
else:
    data_path = op.join(op.expanduser("~"), "data_demo")
print(data_path)

subjects_dir = op.join(data_path, params["subjects_dir"])

morph_stc_path = \
    op.join(data_path, 'source_dsamp_full_reconstruction_dSPM_aparc',
            '_subject_id_{sbj}', 'morph_stc')

os.environ['ETS_TOOLKIT'] = 'qt4'
os.environ['QT_API'] = 'pyqt5'

fig_path = op.join(data_path, 'figures')
if not os.path.isdir(fig_path):
    os.mkdir(fig_path)
# PLot
stc_condition = list()
for cond in conditions:
    stcs = list()
    for subject_id in range(1, 20):
        if subject_id not in exclude_subjects:
            subject = "sub%03d" % subject_id
            out_path = morph_stc_path.format(sbj=subject)
            stc = mne.read_source_estimate(
                    op.join(out_path, 'mne_dSPM_inverse_morph-%s' % (cond)))
            stcs.append(stc)

    data = np.average([np.abs(s.data) for s in stcs], axis=0)
    stc = mne.SourceEstimate(data, stcs[0].vertices,
                             stcs[0].tmin, stcs[0].tstep, 'fsaverage')
    del stcs
    stc_condition.append(stc)

data = stc_condition[0].data/np.max(stc_condition[0].data) + \
        stc_condition[2].data/np.max(stc_condition[2].data) - \
        stc_condition[1].data/np.max(stc_condition[1].data)
data = np.abs(data)
stc_contrast = mne.SourceEstimate(
        data, stc_condition[0].vertices, stc_condition[0].tmin,
        stc_condition[0].tstep, 'fsaverage')
# stc_contrast.save(op.join(fig_path, 'stc_dspm_difference_norm'))

lims = (0.25, 0.75, 1)
clim = dict(kind='value', lims=lims)
brain_dspm = stc_contrast.plot(
    views=['ven'], hemi='both', subject='fsaverage', subjects_dir=subjects_dir,
    initial_time=0.17, time_unit='s', background='w',
    clim=clim, foreground='k', backend='auto')

mlab.view(90, 180, roll=180, focalpoint=(0., 15., 0.), distance=500)
brain_dspm.save_image(op.join(fig_path, 'dspm-contrast'))
