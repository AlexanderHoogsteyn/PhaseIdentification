import sys
from os.path import dirname

sys.path.append(dirname("../src/"))

from src.PhaseIdentification.voltageBasedPhaseIdentification import *
from src.PhaseIdentification.integratedPhaseIdentification import *

feeder = Feeder(feederID="1351982_1596442", include_three_phase=False)

voltage_data = feeder.voltage_features
plt.figure(figsize=(6, 3))
markers = ["s", "o", "D", ">", "<", "v", "+"]
x = np.arange(0, 24*7)
color = plt.cm.viridis(float(1) / (float(feeder.nb_customers) - 1.0))
plt.plot(x, voltage_data[1], color=color, alpha=0.85)
plt.yticks(fontsize=10)
plt.ylabel("Voltage", fontsize=14)
plt.xlabel("Time", fontsize=14)
plt.show()

plt.figure(figsize=(6, 3))
markers = ["s", "o", "D", ">", "<", "v", "+"]
x = np.arange(0, 24*7)
color = plt.cm.viridis(float(8) / (float(feeder.nb_customers) - 1.0))
plt.plot(x, voltage_data[8], color=color, alpha=0.85)
plt.yticks(fontsize=10)
plt.ylabel("Voltage", fontsize=14)
plt.xlabel("Time", fontsize=14)
plt.show()

plt.figure(figsize=(6, 3))
markers = ["s", "o", "D", ">", "<", "v", "+"]
x = np.arange(0, 24*7)
color = plt.cm.viridis(float(13) / (float(feeder.nb_customers) - 1.0))
plt.plot(x, voltage_data[13], color=color, alpha=0.85)
plt.yticks(fontsize=10)
plt.ylabel("Voltage", fontsize=14)
plt.xlabel("Time", fontsize=14)
plt.show()

transfo_volt_data = feeder.voltage_features_transfo
plt.figure(figsize=(6, 3))
x = np.arange(0, 24*7)
color = plt.cm.viridis(float(13) / (float(feeder.nb_customers) - 1.0))
plt.plot(x, transfo_volt_data[0], color=color, alpha=0.85)
plt.plot(x, transfo_volt_data[1], color=color, alpha=0.85)
plt.plot(x, transfo_volt_data[2], color=color, alpha=0.85)
plt.yticks(fontsize=10)
plt.ylabel("Voltage", fontsize=14)
plt.xlabel("Time", fontsize=14)
plt.show()