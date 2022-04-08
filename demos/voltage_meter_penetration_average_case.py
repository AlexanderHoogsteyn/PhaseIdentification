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

#################################################
"""

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
#included_feeders = ["86315_785383", "1076069_1274129", "1351982_1596442", "65025_80035"]
#included_feeders = ["1076069_1274129"]

cases = ["Case A","Case B","Case C","Case D","Case E","Case F"]
include_three_phase = True
length = 24*20
volt_length = 24*1
salient_components = 1
reps = 30
accuracy = 0.5
s = True
sal_treshold = 10
data="POLA_data/"
nb_salient_components = int(length*0.98)
methods = ["voltage Pearson correlation","power Pearson correlation ","Bagging ensemble","Boosting ensemble"]
voltage_pen_range = np.arange(0, 1.1, 0.1)
tot_scores = np.zeros([len(methods), len(voltage_pen_range)])

for case, feeder_id in enumerate(included_feeders):
    for rep in range(0, reps):
        scores = []
        feeder_volt = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s),data=data)
        phase_identification_volt = PhaseIdentification(feeder_volt)
        phase_identification_volt.sort_devices_by_variation()
        phase_identification_volt.voltage_correlation_transfo_ref(length=volt_length)
        col = list(phase_identification_volt.accuracy() * voltage_pen_range)
        scores.append(col)

        feeder_load = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s),data=data)
        phase_identification_load = PartialPhaseIdentification(feeder_load)
        phase_identification_load.load_correlation_xu_fixed(salient_components=salient_components,nb_salient_components=nb_salient_components, length=length)
        col = [phase_identification_load.accuracy()]*len(voltage_pen_range)
        scores.append(col)

        # col = []
        # for i, voltage_pen in enumerate(voltage_pen_range):
        #     feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s))
        #     result = power_voltage_conform_method(feeder,salient_components=salient_components, nb_salient_components=nb_salient_components,length=length,voltage_meter_penetration=voltage_pen)
        #     col += [result]
        # scores.append(col)

        col = []
        for i, voltage_pen in enumerate(voltage_pen_range):
            feeder_A = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s),data=data)
            result = power_and_voltage_bagging(feeder_A, nb_salient_components=nb_salient_components,salient_components=salient_components,length=length,voltage_meter_penetration=voltage_pen,volt_length=volt_length)
            col += [result]
        scores.append(col)

        # col = []
        # for i, voltage_pen in enumerate(voltage_pen_range):
        #     feeder_B = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s),data=data)
        #     result = boost_power_with_voltage(feeder_B, nb_salient_components=nb_salient_components, salient_components=salient_components, length=length,power_treshold = 30 )
        #     col += [result]
        # scores.append(col)

        col = []
        for i, voltage_pen in enumerate(voltage_pen_range):
            feeder_B = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=s),data=data)
            result = boost_voltage_with_power(feeder_B, nb_salient_components=nb_salient_components, salient_components=salient_components, length=length,voltage_meter_penetration=voltage_pen,min_corr=0.2*volt_length,select_biggest=False, var_filter=True,volt_length=volt_length)
            col += [result]
        scores.append(col)

        tot_scores += np.array(scores)
        print(round(rep/reps*100), "% complete")

tot_scores = tot_scores/(reps*len(included_feeders))
# Plot
plt.figure(figsize=(8, 6), dpi=80)
x = voltage_pen_range
markers = ["o","D","s","<",">"]
for i, c in enumerate(methods):
    plt.plot(x*100, tot_scores[i]*100,marker=markers[i], label=c)

# Decorations
plt.rc('font', size=14)
#plt.title(cases[case], fontsize=20)
plt.xticks(fontsize=12)
plt.ylim([0,105])
plt.xlim([0,105])
plt.xlabel("Voltage data collected (%)",fontsize=20)
plt.ylabel("Accuracy (%)",fontsize=20)
plt.yticks(fontsize=12)
plt.legend()
plt.show()
#plt.savefig("voltage_penetration_comparison_10")

