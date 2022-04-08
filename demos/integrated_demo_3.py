import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from PhaseIdentification.integratedPhaseIdentification import *
from PhaseIdentification.common import *
import seaborn as sns

"""
##################################################
DEMO 3
Influence of voltage assist ratio on accuracy of load based methods
For multiple feeders

I can improve this by making shure an additional 10 of missing is added in stead of all new devices
##################################################
"""
include_A = True
include_B = True
include_C = True
load_noise = 0.01   #pu
include_three_phase = False
length = 24*15

included_feeders = []
if include_A:
    included_feeders.append("86315_785383")
if include_B:
    included_feeders.append("65028_84566")
if include_C:
    included_feeders.append("1830188_2181475")

ratio_range = np.arange(0,1.5,.5)
length_range = np.arange(1, 15)
missing_range = np.arange(0, 1.00, 0.10)
reps = 1

fig, axs = plt.subplots(len(ratio_range), len(included_feeders), figsize=(24, 20), dpi=80)
fig.suptitle('Percentage of customers that are allocated correctly')

for g,feeder_id in enumerate(included_feeders):
    for h, ratio in enumerate(ratio_range):
        tot_scores = np.zeros([len(missing_range), len(length_range)])
        for rep in range(0, reps):
            scores = []

            feeder = IntegratedMissingPhaseIdentification(measurement_error=load_noise, feederID=feeder_id,
                                                          include_three_phase=include_three_phase, length=15 * 24,
                                                          missing_ratio=0)
            for i, value in enumerate(missing_range):
                col = []
                for j, days in enumerate(length_range):
                    feeder.reset_partial_phase_identification()
                    feeder.reset_load_features_transfo()
                    feeder.add_missing(value)
                    feeder.voltage_assisted_load_correlation(sal_treshold_load=0.4, sal_treshold_volt=0.0,
                                                             corr_treshold=0.1, volt_assist=ratio,
                                                             length=24 * days)
                    col += [feeder.accuracy()]
                scores.append(col)
            tot_scores += np.array(scores)
            print(round(rep / reps * 100), "% complete")
        tot_scores = tot_scores / reps
        print("TOTAL SCORE ", np.mean(tot_scores))

        # Plot
        #plt.figure(figsize=(12, 10), dpi=80)
        y = [str(i) + "%" for i in list(np.arange(100, 0, -10))]
        x = length_range
        sns.heatmap(tot_scores, ax=axs[h,g], xticklabels=x, yticklabels=y, cmap='RdYlGn', center=0.7,
                    annot=False)

        # Decorations
        axs[h,g].set_title('Feeder ' + str(feeder_id) + ', Voltage assistance ' + str(round(ratio*100)) + '%', fontsize=16)
        #axs[h,g].set_xticks(fontsize=12)
        axs[h,g].set_xlabel("Duration (days) that hourly data was collected")
        axs[h,g].set_ylabel("Percentage of customers with smart meter")
        #axs[h,g].set_yticks(fontsize=12)
        #plt.show()
        #axs[h,g].savefig("accuracy_low_sm_pen_integrated_"+feeder_id+"_"+str(int(ratio*100)))
        #plt.close()

plt.show()