from src.PhaseIdentification.voltageBasedPhaseIdentification import *

"""
##################################################
Fluvinus experiment can be done using "truncated"
#   CASE A: Rural area  
#           feeder ID = 86315_785383
#           number of devices = 22
#   CASE B: Urban area
#           number of devices = 125
#           feeder ID = 65028_84566
#   CASE C: Average feeder
#           number of devices = 76
#           feeder ID = 1830188_2181475
##################################################
"""
include_A = True
include_B = True
include_C = True
accuracy_class = 0.1
include_three_phase = True
length = 24*7
n_repeats = 1

included_feeders = []
if include_A:
    included_feeders.append("86315_785383")
if include_B:
    included_feeders.append("65028_84566")
if include_C:
    included_feeders.append("1830188_2181475")
for feeder_id in included_feeders:
    feeder = Feeder(feederID=feeder_id,include_three_phase=include_three_phase,length=length)
    feeder.truncate_voltages()
    error = ErrorClass(accuracy_class)
    phase_identification = PhaseIdentification(feeder, error)
    phase_identification.voltage_correlation()
    print("Accuracy using voltage correlation method", " data: ", phase_identification.accuracy())
    feeder.plot_voltages(length=length)
    feeder.plot_load_profiles(length=length)