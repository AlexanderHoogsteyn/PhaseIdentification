import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from PhaseIdentification.integratedPhaseIdentification import *
import pickle
import numpy as np

"""
##################################################
DEMO 4
Influence of voltage assist ratio on accuracy of load based methods
but results get stored in pickle file

I can improve this by making shure an additional 10 of missing is added in stead of all new devices
##################################################
"""
accuracy_class = 0.01   #pu
include_three_phase = False
length = 24*15

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1132967_1400879", "65025_80035", "1076069_1274125"]

ratio_range = np.arange(0,1.2,0.20)
length_range = np.arange(1, 15)
missing_range = np.arange(0, 1.00, 0.10)
reps = 1

data = {}

for g,feeder_id in enumerate(included_feeders):
    for h, ratio in enumerate(ratio_range):
        tot_scores = np.zeros([len(missing_range), len(length_range)])
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        error = ErrorClass(accuracy_class)
        for rep in range(0, reps):
            scores = []
            error.reroll_noise()
            phase_identification = IntegratedMissingPhaseIdentification(feeder, error)
            for i, value in enumerate(missing_range):
                col = []
                for j, days in enumerate(length_range):
                    phase_identification.reset_partial_phase_identification()
                    phase_identification.reset_load_features_transfo(feeder)
                    phase_identification.add_missing(value)
                    phase_identification.voltage_assisted_load_correlation(sal_treshold_load=0.4, sal_treshold_volt=0.0,
                                                             corr_treshold=0.1, volt_assist=ratio,
                                                             length=24 * days, salient_components=4, printout_level=0)
                    col += [phase_identification.accuracy()]
                scores.append(col)
            tot_scores += np.array(scores)
            #print(round(rep / reps * 100), "% complete")
        tot_scores = tot_scores / reps
        #print("TOTAL SCORE ", np.mean(tot_scores))

        data[(h,g)] = tot_scores

results = {"corr_treshold_range":ratio_range,"corr_treshold_range":length_range,"salient_comp_range":missing_range,
           "reps":reps, "included_feeders":["Case A"],"data":data}

with open('results_'+str(reps)+'reps_local.pickle', 'wb') as handle:
    pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)