import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys
from os.path import dirname

sys.path.append(dirname("../src/"))

from PhaseIdentification.common import *
from PhaseIdentification.voltageBasedPhaseIdentification import *

#df = pd.read_csv("https://raw.githubusercontent.com/selva86/datasets/master/email_campaign_funnel.csv")


df = pd.DataFrame(columns=("Sensitivity","Direction","Percentage"))

# Base case 14 days, One sample every hour, 80% SM penetration
included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
reps = 100
include_three_phase = True
base_length = 14*24
accuracy = 0.1
class_results = []
acc = 0.0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=base_length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
base_acc = 100*acc/(reps*len(included_feeders))
print("Base case accuracy: ", base_acc)


#Different length of  data
length = 24*7
acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
print("Shorter data collected ", acc)
df.loc[0] = ["Length of data collected (+/- 7 days)","decrease",acc-base_acc]

length = 24*20
acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
print("Longer data collected ", acc)
df.loc[1] = ["Length of data collected (+/- 7 days)","increase",acc-base_acc]

length = 24*10
acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
print("Shorter data collected ", acc)
df.loc[2] = ["Length of data collected (+/- 4 days)","decrease",acc-base_acc]

length = 24*18
acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
print("Longer data collected ", acc)
df.loc[8] = ["Length of data collected (+/- 4 days)","increase",acc-base_acc]

#Decrease sample time interval
acc = 0
length = int(14*24/2)

for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        feeder.lower_data_resolution(2)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[9] = ["Decrease sample time interval to 2h","decrease",acc-base_acc]

acc = 0
length = int(14*24/3)
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.8)
        feeder.lower_data_resolution(3)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[3] = ["Decrease sample time interval to 3h","decrease",acc-base_acc]

acc = 0
length = int(14*24)
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.9)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[4] = ["SM penetration (+/- 10%)","increase",acc-base_acc]

acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.7)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[5] = ["SM penetration (+/- 10%)","decrease",acc-base_acc]

acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[6] = ["SM penetration (+/- 20%)","increase",acc-base_acc]

acc = 0
for feeder_id in included_feeders:
    for rep in np.arange(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        feeder.set_sm_pentration(0.6)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy, s=False))
        phase_identification.voltage_correlation_transfo_ref(length=length)
        #phase_identification.load_correlation_enhanced_tuning(nb_salient_components=nb_salient_components, nb_assignments=nb_assignments, salient_components=salient_components, length=24*20)
        acc = acc + phase_identification.accuracy()
acc = 100*acc/(reps*len(included_feeders))
df.loc[7] = ["SM penetration (+/- 20%)","decrease",acc-base_acc]



# Draw Plot
plt.figure(figsize=(8, 4), dpi= 80)
group_col = 'Direction'
order_of_bars = df.Sensitivity.unique()[::-1]
#colors = [plt.cm.Spectral(i/4) for i in range(len(df[group_col].unique()))]
colors = ["firebrick", "mediumseagreen"]
for c, group in zip(colors, df[group_col].unique()):
    sns.barplot(x='Percentage', y='Sensitivity', data=df.loc[df[group_col]==group, :], order=order_of_bars, color=c, label=group)

# Decorations    
plt.xlabel("Accuracy difference to base case (%)",fontsize=12)
plt.xlim([-10.3, 10.3])
#plt.ylabel("Stage of Purchase",fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
#plt.title("Population Pyramid of the Marketing Funnel", fontsize=22)
plt.legend()
plt.show()
