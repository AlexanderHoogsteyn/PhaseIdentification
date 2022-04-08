import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from PhaseIdentification.powerBasedPhaseIdentification import *
from PhaseIdentification.voltageBasedPhaseIdentification import *
from PhaseIdentification.integratedPhaseIdentification import *
from PhaseIdentification.common import *
import matplotlib.pyplot as plt
import numpy as np

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
reps = 1
accuracy = 0.5
s = True
sal_treshold = 10
nb_salient_components = int(length*0.98)

for case, feeder_id in enumerate(included_feeders):
    voltage_pen_range = np.arange(0, 1.1, 0.1)
    #voltage_pen_range = np.array([0.1])
    tot_scores = np.zeros([3, len(voltage_pen_range)])

    for rep in range(0, reps):
        scores = []
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=s))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        col = list(phase_identification.accuracy() * voltage_pen_range)
        scores.append(col)

        col = []
        for i, voltage_pen in enumerate(voltage_pen_range):
            feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s))
            result = power_voltage_conform_method(feeder, nb_salient_components=nb_salient_components,length=length,voltage_meter_penetration=voltage_pen)
            col += [result]
        scores.append(col)

        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy, s=s))
        phase_identification.load_correlation_xu_fixed(salient_components=salient_components,nb_salient_components=nb_salient_components, length=length)
        col = [phase_identification.accuracy()]*len(voltage_pen_range)
        scores.append(col)
        tot_scores += np.array(scores)
        print(round(rep/reps*100), "% complete")
    tot_scores = tot_scores/reps
    # Plot
    plt.figure(figsize=(8, 6), dpi=80)
    x = voltage_pen_range
    for i, c in enumerate(["voltage Pearson correlation","power voltage conform method","power Pearson correlation "]):
        plt.plot(x, tot_scores[i]*100, label=c)

    # Decorations
    plt.rc('font', size=14)
    plt.title(cases[case], fontsize=20)
    plt.xticks(fontsize=12)
    #plt.ylim([25,105])
    plt.xlabel("Voltage penetration",fontsize=20)
    plt.ylabel("Accuracy (%)",fontsize=20)
    plt.yticks(fontsize=12)
    plt.legend()
    #plt.show()
    plt.savefig("voltage_penetration_comparison_" + cases[case])

