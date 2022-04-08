import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.integratedPhaseIdentification import *
from src.PhaseIdentification.common import *
import seaborn as sns

"""
##################################################
DEMO 3
Influence of missing data on accuracy of load based methods

I can improve this by making shure an additional 10 of missing is added in stead of all new devices
##################################################
"""

included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
cases = ["Case A","Case B","Case C","Case D","Case E","Case F"]
include_three_phase = True
length = 24*20
salient_components = 0
reps = 40
accuracy = 0.2
s = True
sal_treshold = 2

length_range = np.arange(1, 21)
missing_range = np.arange(0, 1.00, 0.10)
tot_scores = np.zeros([len(missing_range), len(length_range)])
for feeder_id in included_feeders:
    for rep in range(0,reps):
        scores = []
        for i, value in enumerate(missing_range):
            col = []
            for j, length in enumerate(length_range):
                feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase,
                                error_class=ErrorClass(accuracy, s=s))
                load_feeder = IntegratedMissingPhaseIdentification(feeder)
                load_feeder.add_missing(ratio=value)
                load_feeder.load_correlation_xu_fixed(nb_salient_components=int(length*24-3),salient_components=salient_components,length=length*24)
                col += [load_feeder.accuracy()]
            scores.append(col)
        tot_scores += np.array(scores)
        print(round(rep/reps*100), "% complete")
tot_scores = tot_scores/reps/len(included_feeders)
    # Plot
plt.figure(figsize=(15, 7), dpi=80)
y = [str(i) + "%" for i in list(np.arange(100, 0, -10))]
x = length_range
ax = sns.heatmap(tot_scores, xticklabels=x, yticklabels=y, cmap='RdYlGn', center=0.7,
            annot=True,fmt = '.0%',cbar_kws={'label': 'Accuracy',})
ax.figure.axes[-1].yaxis.label.set_size(18)
# Decorations
#plt.title('Percentage of customers that are allocated correctly for ' + str(feeder_id), fontsize=16)
plt.xticks(fontsize=12)
plt.xlabel("Duration (days) of data collected", fontsize=18)
plt.ylabel("Percentage of customers with SM", fontsize=18)
plt.yticks(fontsize=12)
cbar = ax.collections[0].colorbar
cbar.set_ticks([0, .1,.2,.3,.4,.5,.6,.7,.8,.9, 1])
cbar.set_ticklabels(['0%','10%', '20%','30%', '40%','50%', '60%', '70%', '80%', '90%', '100%'])
plt.show()