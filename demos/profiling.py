import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

import cProfile as cp
from PhaseIdentification.integratedPhaseIdentification import *

profiler = cp.Profile()
cp.run('voltage_assisted_load_correlation()', 'stats')