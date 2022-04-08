import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.common import *
from src.VisualizePhaseIdentification.visualization import *
from src.PhaseIdentification.voltageBasedPhaseIdentification import *
from src.PhaseIdentification.powerBasedPhaseIdentification import *
import matplotlib.lines as lines

#
feeder = Feeder("1351982_1596442",include_three_phase=True)
phaseID = PhaseIdentification(feeder, ErrorClass(0.1))
phaseID.voltage_correlation()
# viz = WrongLabels(phaseID)
# viz.visualize_length_correlation()
# viz.visualize_imbalance_correlation()


voltage_data = phaseID.voltage_features
print(phaseID.phase_labels)
fig = plt.figure(figsize=(8, 6))
SIZE = 18
SMALL_SIZE = 14
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('font', size=SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SIZE)
plt.scatter(voltage_data[6],voltage_data[8])
x = np.linspace(0.998,1,100)
plt.plot(x, x, '-r', label='y=2x+1')
plt.xticks(np.arange(0.998, 1.000, step=0.001))
plt.yticks(np.arange(0.998, 1.000, step=0.001))
plt.xlabel("Voltage at customer A (p.u.)")
plt.ylabel("Voltage at customer B (p.u.)")
plt.show()


# plt.figure(figsize=(8, 6))
# plt.scatter(voltage_data[6],voltage_data[7])
# plt.plot(x, x, '-r', label='y=2x+1')
# plt.xticks(np.arange(0.998, 1.000, step=0.001))
# plt.yticks(np.arange(0.998, 1.000, step=0.001))
# plt.xlabel("Voltage at customer A (p.u.)")
# plt.ylabel("Voltage at customer C (p.u.)")
# plt.show()
#
# plt.figure(figsize=(8, 6))
# plt.scatter(np.append(1,voltage_data[6]), np.append(voltage_data[7],1))
# plt.plot(x, x, '-r', label='y=2x+1')
# plt.xticks(np.arange(0.998, 1.000, step=0.001))
# plt.yticks(np.arange(0.998, 1.000, step=0.001))
# plt.xlabel("Voltage at customer A shifted 1h (p.u.)")
# plt.ylabel("Voltage at customer C (p.u.)")
# plt.show()
#
included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
#included_feeders = ["1351982_1596442"]

markers = ["s", "o", "D", ">", "<", "v", "+"]

plt.figure(figsize=(14, 8))
plt.rc('font', size=18)
for id in included_feeders:
    feeder = Feeder(id, include_three_phase=True)
    phaseID = PhaseIdentification(feeder, ErrorClass(1.0))
    phaseID.voltage_correlation_transfo_ref()
    viz = WrongLabels(phaseID)

    mav_imbalance = viz.get_mav_imbalance()
    customer_path_length = viz.get_customer_path_length()
    correct = viz.phase_labels == viz.partial_phase_labels
    wrong = viz.phase_labels != viz.partial_phase_labels
    plt.scatter(mav_imbalance[correct], customer_path_length[correct], color='tab:green',marker="+")
    plt.scatter(mav_imbalance[wrong], customer_path_length[wrong], color='tab:red',marker="x")
    # plt.xticks(np.arange(0.998, 1.000, step=0.001))
    # plt.yticks(np.arange(0.998, 1.000, step=0.001))
plt.xlabel("Relative voltage variation (%)")
plt.ylabel("Distance from transformer (m)")
plt.legend(["Wrong allocated","Correctly allocated"])
plt.show()

mav_imbalance_correct = np.array([])
mav_imbalance_wrong = np.array([])

for rep in range(0,10):
    for id in included_feeders:
        feeder = Feeder(id, include_three_phase=True)
        phaseID = PhaseIdentification(feeder, ErrorClass(1.0))
        phaseID.voltage_correlation_transfo_ref()
        viz = WrongLabels(phaseID)
        mav_imbalance_id = viz.get_mav_imbalance()
        #customer_path_length_id = viz.get_customer_path_length()
        correct = viz.phase_labels == viz.partial_phase_labels
        wrong = viz.phase_labels != viz.partial_phase_labels
        mav_imbalance_correct = np.append(mav_imbalance_correct, mav_imbalance_id[correct])
        mav_imbalance_wrong = np.append(mav_imbalance_wrong, mav_imbalance_id[wrong])
        #np.append(customer_path_length, customer_path_length_id[correct])

# Assign colors for each airline and the names
colors = [ '#009E73', '#D55E00']
names = [ "Correct allocated", "Wrong allocated" ]
# Make the histogram using a list of lists
# Normalize the flights and assign colors and names
plt.figure(figsize=(8, 6))
plt.hist([mav_imbalance_correct, mav_imbalance_wrong], density=False,
         color=colors, bins=np.arange(0, 1, 0.02), label=names)
plt.xticks(np.arange(0.1, 1.000, step=0.1))
plt.yticks(np.arange(0, 600, step=100))
plt.ylim([0, 505])
plt.xlim([0, 0.91])
# Plot formatting
plt.legend()
plt.xlabel('Relative voltage variation (%)')
plt.ylabel('Frequency')
#plt.title('Side-by-Side Histogram with Multiple Airlines')
plt.show()