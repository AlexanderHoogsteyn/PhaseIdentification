import sys
from os.path import dirname

sys.path.append(dirname("../src/"))

from PhaseIdentification.PhaseIdentification import IntegratedPhaseIdentification
from PhaseIdentification.common import *

"""
##################################################
DEMO 2
Comparison across accuracy classes and 6 feeders

I can improve this by making shure an additional 10 of missing is added in stead of all new devices
##################################################
"""

accuracy_class = 0.01  # pu
include_three_phase = False
length = 24 * 20
volt_assist = 0.9

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1132967_1400879", "65025_80035",
                    "1076069_1274125"]

for feeder_id in included_feeders:
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase, length=length)
    phase_identification = IntegratedPhaseIdentification(feeder, ErrorClass(accuracy_class))
    phase_identification.voltage_assisted_load_correlation(sal_treshold_load=1, sal_treshold_volt=0.0, corr_treshold=2,
                                                           volt_assist=volt_assist, length=length, salient_components=4,
                                                           printout_level=0)
