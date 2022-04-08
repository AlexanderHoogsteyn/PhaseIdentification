import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
import os

class AccuracySensitivity():
    def __init__(self,results):
        self.ratio_range = results["corr_treshold_range"]
        self.length_range = results["corr_treshold_range"]
        self.missing_range = results["salient_comp_range"]
        self.included_feeders = results["included_feeders"]
        self.data = results["data"]
        print("Ratio range: %s to %s" % (self.ratio_range[0], self.ratio_range[-1]))
        print("Length range: %s to %s" % (self.length_range[0], self.length_range[-1]))
        print("Missing range: %s to %s" % (self.missing_range[0], self.missing_range[-1]))
        print("---------------------------------------")
        print("Ratio     %s     %s" % (self.ratio_range[0], self.ratio_range[-1]))
        for i, feeder in enumerate(self.included_feeders):
            print("{}:  {:.2%}  {:.2%}".format(feeder,np.mean(self.data[(0,i)]),np.mean(self.data[(len(self.ratio_range)-1,i)])))

    def merge(self, other):
        """
        Method to merge the data from 2 AccuracySensititvity objects together with different ratio ranges
        """
        self.ratio_range = np.sort(np.concatenate(self.ratio_range, other.corr_treshold_range))
        self.data.update(other.data)
        return self

    def get_index_ratio(self,ratio):
        for i, ratios in enumerate(self.ratio_range):
            if ratio == ratios:
                return i
        raise KeyError("Ratio not in ratio range")

    def visualize_one(self,ratio,feeder):
        plt.figure(figsize=(12, 10), dpi=80)
        y = [str(i) + "%" for i in list(np.arange(100, 0, -10))]
        x = self.length_range
        tup = (ratio,feeder)
        sns.heatmap(self.data[tup], xticklabels=x, yticklabels=y, cmap='RdYlGn', center=0.7,
                    annot=True)

        # Decorations
        plt.title('Percentage of customers that are allocated correctly for ' + str(feeder), fontsize=16)
        plt.xticks(fontsize=12)
        plt.xlabel("Duration (days) that hourly data was collected")
        plt.ylabel("Percentage of customers with smart meter")
        plt.yticks(fontsize=12)
        plt.show()

    def visualize_load_based(self, ratio=0):
        y = [str(i) + "%" for i in list(np.arange(100, 0, -10))]
        x = self.length_range

        i  = self.get_index_ratio(ratio)

        fig, axs = plt.subplots(1, 4, figsize=(20, 6), dpi=90,
                               gridspec_kw={'width_ratios':[1,1,1,0.08]})

        axs[0].get_shared_y_axes().join(axs[1], axs[2])
        sns.heatmap(100 * self.data[(i, 0)], ax=axs[0], xticklabels=x, yticklabels=y, cmap='RdYlGn',
                    cbar=False, center=70, annot=True)
        sns.heatmap(100 * self.data[(i, 1)], ax=axs[1], xticklabels=x, yticklabels=y, cmap='RdYlGn',
                    cbar=False, center=70, annot=True)
        sns.heatmap(100 * self.data[(i, 2)], ax=axs[2], xticklabels=x, yticklabels=y, cmap='RdYlGn',
                    cbar_ax=axs[3], center=70, annot=True)

        axs[1].set_xlabel("Duration (days) that hourly data was collected", fontsize=12)
        axs[2].set_xlabel("Duration (days) that hourly data was collected", fontsize=12)
        axs[0].set_xlabel("Duration (days) that hourly data was collected", fontsize=12)
        axs[0].set_ylabel("Percentage of customers with smart meter", fontsize=12)
        axs[0].set_title("Case A", fontsize=12)
        axs[1].set_title("Case B", fontsize=12)
        axs[2].set_title("Case C", fontsize=12)


        plt.show(fig)

    def visualize_voltage_based(self):
        self.visualize_load_based(ratio=1.0)


    def visualize_voltage_assisted(self,range):
        fig, axs = plt.subplots(len(range), len(self.included_feeders), figsize=(20, 16), dpi=90, sharex='all',
                                sharey='all')
        # fig.suptitle('Fraction of customers that are allocated correctly')
        for g, feeder in enumerate(self.included_feeders):
            for h, value in enumerate(range):

                y = [str(i) + "%" for i in list(np.arange(100, 0, -10))]
                x = self.length_range
                sns.heatmap(100 * self.data[(h, g)], ax=axs[h, g], xticklabels=x, yticklabels=y, cmap='RdYlGn',
                            cbar=False, center=70,
                            annot=False)

                # Decorations
                axs[h, g].set_title(feeder + ', Voltage assistance ' + str(round(value * 100)) + '%', fontsize=12)
                if h == 2:
                    axs[h, g].set_xlabel("Duration (days) that hourly data was collected", fontsize=12)
                if g == 0:
                    axs[h, g].set_ylabel("Percentage of customers with smart meter", fontsize=12)

        plt.show(fig)

class CorrelationCoeficients():

    def __init__(self,PartialPhaseIdentification):
        self.phase_labels = PartialPhaseIdentification.phase_labels
        self.load_features = PartialPhaseIdentification.load_features
        self._load_features_transfo = PartialPhaseIdentification.load_features_transfo
        self.voltage_features = PartialPhaseIdentification.voltage_features
        self.voltage_features_transfo = PartialPhaseIdentification.voltage_features_transfo

    def pearson_corr_load(self,j,phase):
        phase = phase - 1
        corr = 1.0 / (len(self.phase_labels) - 1) * sum((self.load_features[j] - np.mean(self.load_features[j])) * \
                (self._load_features_transfo[phase] - np.mean(self._load_features_transfo[phase]))) \
                / (np.std(self.load_features[j])*np.std(self._load_features_transfo[phase]))
        return corr

    def pearson_corr_voltage(self,j,phase):
        phase = phase - 1
        corr = 1.0 / (len(self.phase_labels) - 1) * sum((self.voltage_features[j] - np.mean(self.voltage_features[j])) * \
                (self.voltage_features_transfo[phase] - np.mean(self.voltage_features_transfo[phase]))) \
                / (np.std(self.voltage_features[j])*np.std(self.voltage_features_transfo[phase]))
        return corr

    def corr_vector_load(self,phase, reference_phase):
        corr_vector = []
        for j,label in enumerate(self.phase_labels):
            if label == phase:
                corr_vector += [self.pearson_corr_load(j,reference_phase)]
        return np.array(corr_vector)

    def corr_vector_voltage(self,phase, reference_phase):
        corr_vector = []
        for j,label in enumerate(self.phase_labels):
            if label == phase:
                corr_vector += [self.pearson_corr_voltage(j,reference_phase)]
        return np.array(corr_vector)

    def visualize_correlation(self,reference):
        markers = ["s", "o", "D", ">", "<", "v", "+"]
        plt.figure(figsize=(8, 6), dpi=80)
        plt.scatter(self.corr_vector_voltage(1,reference),self.corr_vector_load(1,reference),color='tab:green',marker=markers[0])
        plt.scatter(self.corr_vector_voltage(2,reference),self.corr_vector_load(2,reference),color='tab:red',marker=markers[1])
        plt.scatter(self.corr_vector_voltage(3,reference),self.corr_vector_load(3,reference),color='tab:red',marker=markers[2])
        plt.xlabel("Voltage correlation")
        plt.ylabel("Load correlation")
        plt.show()

    def visualize_correlation_all(self):
        markers = ["s", "o", "D", ">", "<", "v", "+"]
        plt.figure(figsize=(8, 6), dpi=80)
        plt.scatter(self.corr_vector_voltage(1,1),self.corr_vector_load(1,1),color='tab:green',marker=markers[0])
        plt.scatter(self.corr_vector_voltage(2,1),self.corr_vector_load(2,1),color='tab:red',marker=markers[1])
        plt.scatter(self.corr_vector_voltage(3,1),self.corr_vector_load(3,1),color='tab:red',marker=markers[2])
        plt.scatter(self.corr_vector_voltage(1,2),self.corr_vector_load(1,2),color='tab:red',marker=markers[0])
        plt.scatter(self.corr_vector_voltage(2,2),self.corr_vector_load(2,2),color='tab:green',marker=markers[1])
        plt.scatter(self.corr_vector_voltage(3,2),self.corr_vector_load(3,2),color='tab:red',marker=markers[2])
        plt.scatter(self.corr_vector_voltage(1,3),self.corr_vector_load(1,3),color='tab:red',marker=markers[0])
        plt.scatter(self.corr_vector_voltage(2,3),self.corr_vector_load(2,3),color='tab:red',marker=markers[1])
        plt.scatter(self.corr_vector_voltage(3,3),self.corr_vector_load(3,3),color='tab:green',marker=markers[2])
        plt.xlabel("Voltage correlation", fontsize=12)
        plt.ylabel("Load correlation", fontsize=12)
        plt.show()

class WrongLabels():
    def __init__(self, phaseidentification):
        self.__dict__ = phaseidentification.__dict__.copy()

    def get_mav_imbalance(self):
        mean_ref = np.mean(self.voltage_features_transfo)
        mav_imbalance = []
        for voltage_profile in self.voltage_features:
            mav_imbalance.append(np.mean(abs(voltage_profile/mean_ref - 1)))
        return np.array(mav_imbalance)*100

    def visualize_imbalance_correlation(self):
        plt.figure(figsize=(6, 3))
        mav_imbalance = self.get_mav_imbalance()
        correct = mav_imbalance[self.phase_labels == self.partial_phase_labels]
        wrong = mav_imbalance[self.phase_labels != self.partial_phase_labels]
        plt.boxplot([correct, wrong],labels=['Correctly allocated customers', 'Wrongly allocated customers'])
        plt.ylabel("MAV imbalance (%)")
        plt.show()

    def path_length(self, busId, branches_data):
        """
        Backtracking algorithm to find the legth path in a feeder
        """
        longest_found = 0
        for branch in branches_data:
            if branch.get("downBusId") == busId:
                return branch.get("cableLength") + self.path_length(branch.get("upBusId"), branches_data)

        if busId == 0:
            return 0

    def get_customer_path_length(self):
        with open(os.path.join(os.path.dirname(self._path_topology), self.feederID + "_branches.json")) as branches_file:
            branches_data = json.load(branches_file)

        customer_path_length = []
        for customer in self.bus_IDs:
            customer_path_length += [self.path_length(customer, branches_data)]
        return np.array(customer_path_length)

    def visualize_length_correlation(self):
        plt.figure(figsize=(8, 6))
        mav_imbalance = self.get_mav_imbalance()
        customer_path_length = self.get_customer_path_length()
        correct = self.phase_labels == self.partial_phase_labels
        wrong = self.phase_labels != self.partial_phase_labels
        plt.scatter(mav_imbalance[correct], customer_path_length[correct], color='tab:green')
        plt.scatter(mav_imbalance[wrong], customer_path_length[wrong], color='tab:red')
        #plt.xticks(np.arange(0.998, 1.000, step=0.001))
        #plt.yticks(np.arange(0.998, 1.000, step=0.001))
        plt.xlabel("(MAV) Imbalance (%)")
        plt.ylabel("Distance between consumer and transformer")
        plt.show()