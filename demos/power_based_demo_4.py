import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.voltageBasedPhaseIdentification import *
from src.PhaseIdentification.common import *

"""
##################################################
DEMO 4
Accuracy accros differnt classes of SM

##################################################
"""

include_three_phase = True
length = 48*30
volt_assist = 0.9
reps = 1

#"1132967_1400879" only has 3 customers
# 'Case D'
included_feeders = ["86315_785383", "65028_84566", "1076069_1274129","1351982_1596442", "65025_80035", "1076069_1274125"]

results = []
for accuracy in [0.1, 0.2, 0.5, 1.0]:
    class_results = []
    for feeder_id in included_feeders:
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        acc = 0
        for rep in np.arange(1):
            phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy))
            #phase_identification.change_data_representation(representation="delta")
            phase_identification.k_means_clustering(n_repeats=reps)
            acc = acc + phase_identification.accuracy()
        class_results.append(acc*100/reps)
        print("Feeder: ", feeder_id)
    results.append(class_results)

labels = ['Case A', 'Case B', 'Case C','Case D', 'Case E', 'Case F']

x = np.arange(len(labels))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots(figsize=(9,3))
rects1 = ax.bar(x - width*3/2, results[0], width, label='Class 0.1',edgecolor = 'tab:blue',alpha=0.7)
rects2 = ax.bar(x - width/2, results[1], width, label='Class 0.2',edgecolor = 'tab:orange',alpha=0.7)
rects3 = ax.bar(x + width/2, results[2], width, label='Class 0.5',edgecolor = 'tab:green',alpha=0.7)
rects4 = ax.bar(x + width*3/2, results[3], width, label='Class 1.0',edgecolor = 'tab:red',alpha=0.7)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Accuracy (%)')
#ax.set_title('Accuracy by case and accuracy class using voltage Pearson correlation')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(bbox_to_anchor=(1,0.2),loc='lower right')


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
reps = 100
accuracy = 1.0
results = []
class_results = []
for feeder_id in included_feeders:
    acc = 0
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
    for rep in np.arange(reps):
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy))
        phase_identification.k_means_clustering(n_repeats=3)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc*100/reps)
    print("Feeder: ", feeder_id)
results.append(class_results)

class_results = []
for feeder_id in included_feeders:
    acc = 0
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
    for rep in np.arange(reps):
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy))
        phase_identification.change_data_representation(representation="delta")
        phase_identification.k_means_clustering(n_repeats=3)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc*100/reps)
    print("Feeder: ", feeder_id)
results.append(class_results)


class_results = []
for feeder_id in included_feeders:
    acc = 0
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
    for rep in np.arange(reps):
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy))
        phase_identification.change_data_representation(representation="binary")
        phase_identification.k_means_clustering(n_repeats=3)
        acc = acc + phase_identification.accuracy()
    class_results.append(acc*100/reps)
    print("Feeder: ", feeder_id)
results.append(class_results)

labels = ['Case A', 'Case B', 'Case C','Case D', 'Case E', 'Case F']

x = np.arange(len(labels))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots(figsize=(9,3))
rects1 = ax.bar(x - width*3/2, results[0], width, label='Raw',edgecolor = 'tab:blue',alpha=0.7)
rects2 = ax.bar(x - width/2, results[1], width, label='Delta',edgecolor = 'tab:orange',alpha=0.7)
rects3 = ax.bar(x + width/2, results[2], width, label='Binary',edgecolor = 'tab:green',alpha=0.7)


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Accuracy (%)')
plt.ylim([0, 100])
#ax.set_title('Accuracy by case and accuracy class using voltage Pearson correlation')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(bbox_to_anchor=(1,1),loc='upper right')

fig.tight_layout()
plt.show()
