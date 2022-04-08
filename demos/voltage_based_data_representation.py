import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.voltageBasedPhaseIdentification import *
from src.PhaseIdentification.integratedPhaseIdentification import *
from src.PhaseIdentification.common import *
from src.PhaseIdentification.voltageBasedPhaseIdentification import *

"""
##################################################
DEMO 1
Influence of missing data on accuracy of load based methods

I can improve this by making sure an additional 10 of missing is added in stead of all new devices
##################################################
"""

include_three_phase = True
length = 24*20
volt_assist = 0
reps = 100
salient_components = 1
nb_salient_components = 400
nb_assignments = 10
corr_treshold = 0.4
salient_treshold = 200
accuracy = 1.0
#"1132967_1400879" only has 3 customers
#included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1132967_1400879", "65025_80035","1076069_1274125"]
included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]

results = []
class_results = []
for feeder_id in included_feeders:
    acc = 0
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,error_class=ErrorClass(accuracy, s=True))
        phase_identification = PhaseIdentification(feeder)
        #phase_identification.load_correlation_xu(salient_components=salient_components,length=length,salient_treshold=salient_treshold)
        phase_identification.k_means_clustering(length=length)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc*100/reps)
    print("Feeder: ", feeder_id)
results.append(class_results)
class_results = []
for feeder_id in included_feeders:
    acc = 0
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,
                        error_class=ErrorClass(accuracy, s=True))
        feeder.change_data_representation("delta")
        phase_identification = PhaseIdentification(feeder)
        # phase_identification.load_correlation_xu(salient_components=salient_components,length=length,salient_treshold=salient_treshold)
        phase_identification.k_means_clustering(length=length)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc * 100 / reps)
    print("Feeder: ", feeder_id)
class_results = []
results.append(class_results)
for feeder_id in included_feeders:
    acc = 0
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,
                        error_class=ErrorClass(accuracy, s=True))
        feeder.change_data_representation("binary")
        phase_identification = PhaseIdentification(feeder)
        # phase_identification.load_correlation_xu(salient_components=salient_components,length=length,salient_treshold=salient_treshold)
        phase_identification.k_means_clustering(length=length)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc * 100 / reps)
    print("Feeder: ", feeder_id)
results.append(class_results)



labels = ['Case A', 'Case B', 'Case C','Case D', 'Case E', 'Case F']

x = np.arange(len(labels))  # the label locations
width = 0.20  # the width of the bars

fig, ax = plt.subplots(figsize=(9,3))
rects3 = ax.bar(x - width, results[0], width, label='Raw')
rects4 = ax.bar(x, results[1], width, label='Delta')
rects5 = ax.bar(x + width, results[2], width, label='Binary')
# Add some text for labels, titl and custom x-axis tick labels, etc.
ax.set_ylabel('Accuracy (%)')
ax.set_ylim([0, 101])
#ax.set_title('Accuracy by case and accuracy class using voltage Pearson correlation')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(bbox_to_anchor=(1,0.0),loc='lower right',ncol=2)


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 4, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


#autolabel(rects1)
#autolabel(rects2)
#autolabel(rects3)
#autolabel(rects4)

fig.tight_layout()

plt.show()