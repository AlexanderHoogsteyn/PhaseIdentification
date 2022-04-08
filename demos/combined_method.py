import sys
from os.path import dirname
sys.path.append(dirname("../src/"))
import copy

from src.PhaseIdentification.voltageBasedPhaseIdentification import *
from src.PhaseIdentification.common import *
from src.PhaseIdentification.powerBasedPhaseIdentification import *

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
include_three_phase = True
accuracy = 0.0
length = 24*20
nb_salient_components = 400
nb_assignments = 10
salient_components = 1

for feeder_id in included_feeders:
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=True))
    nb_devices = len(feeder.device_IDs)
    phase_identification_volt = PhaseIdentification(feeder)
    phase_identification_load = PartialPhaseIdentification(feeder)
    # phase_identification.load_correlation(salient_treshold=salient_treshold, corr_treshold=corr_treshold, salient_components=salient_components, length=24*20)
    phase_identification_load.load_correlation_xu(salient_components=salient_components)
    phase_identification_volt.sort_devices_by_variation()
    phase_identification_volt.voltage_correlation_transfo_ref(length=length)
    volt_acc = phase_identification_volt.accuracy()
    conformity = np.mean(phase_identification_load.partial_phase_labels == phase_identification_volt.partial_phase_labels)
    print("Voltage based accuracy: ", volt_acc)
    print("Correspondance: ", conformity)

    combined_phase_labels = np.zeros(nb_devices)

    conform_i = phase_identification_load.partial_phase_labels == phase_identification_volt.partial_phase_labels
    combined_phase_labels[conform_i] = phase_identification_load.partial_phase_labels[conform_i]
    #acc = acc + phase_identification.accuracy()
    phase_identification_combined = PartialPhaseIdentification(feeder)
    phase_identification_combined.sort_devices_by_variation()
    for i in np.arange(0,nb_devices,1)[conform_i]:
        phase_identification_combined.sub_load_profile(i,int(combined_phase_labels[i]))
    phase_identification_combined.load_correlation_xu(salient_components=salient_components)
    acc_combined = phase_identification_combined.accuracy()
    print("Combined method accuracy: ",acc_combined)