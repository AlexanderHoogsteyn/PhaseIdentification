import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from PhaseIdentification.powerBasedPhaseIdentification import *
from PhaseIdentification.common import *
import matplotlib.pyplot as plt

"""
##################################################
DEMO 3
Influence of voltage assist ratio on accuracy of load based methods
For multiple feeders

I can improve this by making shure an additional 10 of missing is added in stead of all new devices
##################################################
"""

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
cases = ["Case A","Case B","Case C","Case D","Case E","Case F"]
include_three_phase = True
length = 24*20
salient_components = 1
reps = 20
accuracy = 0.1
sal_treshold = 2

for case, feeder_id in enumerate(included_feeders):
    acc_class_range = np.array([0.2,0.5,0.1,0.2,0.5,1.0])
    #voltage_pen_range = np.array([0.1])
    s_range = [True,True,False,False,False,False]
    sal_treshold_range = np.arange(0, 5.2, 0.5)
    tot_scores = np.zeros([len(acc_class_range), len(sal_treshold_range)])

    for rep in range(0,reps):
        scores = []
        for i, accuracy in enumerate(acc_class_range):
            col = []
            for j, sal_treshold in enumerate(sal_treshold_range):
                feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
                phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy, s=s_range[i]))
                phase_identification.load_correlation_xu(salient_treshold=sal_treshold,
                                                      salient_components=salient_components, length=length)

                col += [phase_identification.accuracy()]
            scores.append(col)
        tot_scores += np.array(scores)
        print(round(rep/reps*100), "% complete")
    tot_scores = tot_scores/reps
    # Plot
    plt.figure(figsize=(9, 6), dpi=80)
    y = ["%.2f" % i for i in list(sal_treshold_range)]
    x = ["Class 0.2s","Class 0.5s","Class 0.1","Class 0.2","Class 0.5","Class 1.0"]
    #x = ["Class 0.1"]
    for i,c in enumerate(x):
        plt.plot(y, tot_scores[i], label=c)

    # Decorations
    plt.title(cases[case], fontsize=16)
    plt.xticks(fontsize=12)
    plt.xlabel("Correlation treshold",fontsize=16)
    plt.ylabel("Saliency treshold",fontsize=16)
    plt.yticks(fontsize=12)
    plt.legend()
    #plt.show()
    plt.savefig("treshold_sensitivity" + cases[case])

