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
#################################################
"""

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
cases = ["Case A","Case B","Case C","Case D","Case E","Case F"]
include_three_phase = True
length = 24*20
salient_components = 0
reps = 100
accuracy = 0.1
sal_treshold = 10

for case, feeder_id in enumerate(included_feeders):
    acc_class_range = np.array([0.2,0.5,0.1,0.2,0.5,1.0])
    #voltage_pen_range = np.array([0.1])
    s_range = [True,True,False,False,False,False]
    sal_treshold_range = list(range(5,482,5))
    tot_scores = np.zeros([3, len(acc_class_range)])
    for rep in range(0,reps):
        scores = []
        col = []
        for i, accuracy in enumerate(acc_class_range):
            feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
            phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy, s=s_range[i]))
            phase_identification.random_sort()
            phase_identification.load_correlation_xu_no_sort(salient_components=salient_components, length=length)
            col += [phase_identification.accuracy()]
        scores.append(col)
        col = []
        for i, accuracy in enumerate(acc_class_range):
            feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
            phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy, s=s_range[i]))
            phase_identification.sort_devices_by_nb_salient_components()
            phase_identification.load_correlation_xu_no_sort(salient_components=salient_components, length=length)
            col += [phase_identification.accuracy()]
        scores.append(col)
        col = []
        for i, accuracy in enumerate(acc_class_range):
            feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
            phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy, s=s_range[i]))
            phase_identification.sort_devices_by_variation()
            phase_identification.load_correlation_xu_no_sort(salient_components=salient_components, length=length)
            col += [phase_identification.accuracy()]
        scores.append(col)
        tot_scores += np.array(scores)
        print(round(rep/reps*100), "% complete")
    tot_scores = tot_scores/reps
    # Plot
    plt.figure(figsize=(8, 6), dpi=80)
    y = sal_treshold_range
    x = ["Class 0.2s","Class 0.5s","Class 0.1","Class 0.2","Class 0.5","Class 1.0"]
    #x = ["Class 0.1"]
    for i,c in enumerate(["no sort","# salient components sort","Power variability sort"]):
        plt.plot(x, tot_scores[i]*100, label=c)

    # Decorations
    plt.rc('font', size=14)
    plt.title(cases[case], fontsize=20)
    plt.xticks(fontsize=12)
    #plt.ylim([25,105])
    plt.xlabel("Accuracy class",fontsize=20)
    plt.ylabel("Accuracy (%)",fontsize=20)
    plt.yticks(fontsize=12)
    plt.legend()
    #plt.show()
    plt.savefig("salient_components_sensetivity_sort" + cases[case])

