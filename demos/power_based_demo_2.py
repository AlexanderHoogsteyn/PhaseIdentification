import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.powerBasedPhaseIdentification import *

"""
##################################################
Iterates over all feeders, try to find hard ones
-> Do powerflows first
Acctually I do not need voltages so..?
##################################################
"""
include_A = True
include_B = True
include_C = True
include_three_phase = False
length = 24*7


included_feeders = []
if include_A:
    included_feeders.append("86315_785383")
if include_B:
    included_feeders.append("65028_84566")
if include_C:
    included_feeders.append("1830188_2181475")

for feeder_id in included_feeders:
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
    load_feeder = PartialPhaseIdentification(feeder=feeder, error_class=ErrorClass(1))
    print("Start load correlation algorithm for ", feeder_id)
    load_feeder.load_correlation(sal_treshold=0.1,corr_treshold=0.2,sal_components=3)