import sys
from os.path import dirname
sys.path.append(dirname("../src/"))

from src.PhaseIdentification.voltageBasedPhaseIdentification import *

include_three_phase = True
length = 24*20
accuracy_class = 0.5
reps = 100
nb_salient_components = int(length)

included_feeders = ["86315_785383", "1076069_1274129", "1351982_1596442", "65025_80035"]
included_feeders = ["86315_785383", "65028_84566", "1076069_1274129", "1351982_1596442", "65025_80035", "1076069_1274125"]
cases = ["Case A","Case B","Case C","Case D","Case E","Case F"]


for i, feeder_id in enumerate(included_feeders):
    acc = 0
    feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
    phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy_class, s=False))
    # phase_identification.load_correlation_xu_fixed(nb_salient_components=440, length=length, salient_components=1)
    scores = phase_identification.plot_voltage_correlation_transfo_ref(length=length)
    acc = acc + phase_identification.accuracy()
    for rep in range(reps):
        feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
        phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy_class,s=False))
        #phase_identification.load_correlation_xu_fixed(nb_salient_components=440, length=length, salient_components=1)
        scores = np.vstack((scores, phase_identification.plot_voltage_correlation_transfo_ref(length=length)))
        acc = acc + phase_identification.accuracy()
    scores = scores/length
    print(cases[i], " accuracy = ", 100*acc/(reps+1))

    fig = plt.figure(figsize=(8, 2))
    # plt.hist([scores[:,0], scores[:,1],scores[:,2]], density=False,
    #         color=colors, label=names)
    sns.distplot([scores[:, 0]], hist=True, kde=True,
                 kde_kws={'shade': False, 'linewidth': 3},)
    sns.distplot([scores[:, 1]], hist=True, kde=True,
                 kde_kws={'shade': False, 'linewidth': 3},)
    sns.distplot([scores[:, 2]], hist=True, kde=True,
                 kde_kws={'shade': False, 'linewidth': 3},)
    plt.xlim([-0.2, 0.9])
    plt.legend(["Third highest correlating phase", "Second highest correlating phase", "Correct phase"])
    plt.title(cases[i])
    plt.xlabel("Pearson correlation per sample")
    plt.tight_layout()
    fig.savefig("correlation_"+cases[i])
    #plt.show()