import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys
from os.path import dirname

sys.path.append(dirname("../src/"))

from PhaseIdentification.common import *
from PhaseIdentification.powerBasedPhaseIdentification import *
from PhaseIdentification.integratedPhaseIdentification import *

feeder = Feeder("86315_785383",include_three_phase=True)

pf = feeder.build_power_features(0)

#feeder.voltage_features = pf

phase_ID = PhaseIdentification(feeder)
phase_ID.k_means_clustering()
print(phase_ID.accuracy())
