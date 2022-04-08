from PhaseIdentification.common import *
import numpy as np
import matplotlib.pyplot as plt
import datetime


class PartialPhaseIdentification(Feeder):
    """
    Subclass of Feeder which contains functionality to do a partial phase identification (i.e. only identify a subset
    of customers) during one iteration. This is used by the load based methods which solve the phase Identification partly
    and then subtract the load profile from the correct phase.
    """

    def __init__(self, feeder, error_class=ErrorClass(0)):
        """
        Initialize the PartialPhaseIdentification object by reading out the data from JSON files in the specified directory.
        feederID = full identification number of the feeder
        include_three_phase = put on True if you want to include 3 phase customers in your analysis, 3 phase customers
                              will be regarded as 3 single phase customers
        measurement_error = std of the amount of noise added to the voltage (p.u.)
        length = number of data samples used, the first samples are used
        """
        self.__dict__ = feeder.__dict__.copy()
        size = (np.size(self.voltage_features, 0), np.size(self.voltage_features, 1))
        if error_class.s == False:
            self.voltage_features = self.voltage_features + np.random.normal(0,error_class.get_load_noise(), size)
            self.load_features = self.load_features + np.random.normal(0,error_class.get_load_noise(), size)
        else:
            self.voltage_features = self.voltage_features + np.random.normal(0,error_class.get_load_noise(), size)
            self.load_features = np.random.normal(self.load_features, self.load_features * error_class.accuracy_class/3)
        self.partial_phase_labels = np.zeros(len(self.phase_labels))



    def sub_load_profile(self,j,phase,loss_factor=1):
        """
        Subtracts the load profile from the total and assigns a phase label "phase" to device on index "j"
        """
        if phase == 1 or phase == 2 or phase == 3:
            self.load_features_transfo[phase - 1] -= loss_factor*self.load_features[j]
            self.partial_phase_labels[j] = phase
        elif phase == 5:
            # If i marked as customer without meter (phase==5)
            # do not allocate yet
            self.partial_phase_labels[j] = 0
        else:
            self.partial_phase_labels[j] = 0

    def get_salient_variations(self, treshold, var, var_transfo):
        """
        Sets the salient variations taking into account the remaining devices and threshold
        """
        sal = []
        sal_transfo = []
        total_var = sum(var_transfo)
        pl = self.partial_phase_labels
        for j in range(0,len(self.phase_labels)):
            new_row = []
            new_row_transfo_a = []
            new_row_transfo_b = []
            new_row_transfo_c = []
            for t in range(1, len(var[0])):
                if abs(var[j,t]) > treshold*(total_var[t] - var[j,t])/len(self.phase_labels):
                    new_row += [var[j, t]]
                    new_row_transfo_a += [var_transfo[0, t]]
                    new_row_transfo_b += [var_transfo[1, t]]
                    new_row_transfo_c += [var_transfo[2, t]]
            sal.append(new_row)
            sal_transfo.append([new_row_transfo_a,new_row_transfo_b,new_row_transfo_c])

        sal = np.array(sal)
        sal_transfo = np.array(sal_transfo)
        return sal, sal_transfo

    def get_salient_variation(self, treshold, var, var_transfo):
        """
        Sets the salient variations taking into account the remaining devices and threshold
        """
        sal = []
        sal_transfo = []
        sal_transfo_a = []
        sal_transfo_b = []
        sal_transfo_c = []
        total_var = sum(var_transfo)
        ind = []
        pl = self.partial_phase_labels
        for t in range(1, len(var)):
            if abs(var[t]) > treshold*(total_var[t] - var[t])/len(self.phase_labels):
                sal += [var[t]]
                sal_transfo_a += [var_transfo[0, t]]
                sal_transfo_b += [var_transfo[1, t]]
                sal_transfo_c += [var_transfo[2, t]]
                ind += [t]
        sal = np.array(sal)
        sal_transfo = np.array([sal_transfo_a, sal_transfo_b, sal_transfo_c])
        #plot_salient_comp(var, sal, np.array(ind))
        return sal, sal_transfo

    def get_salient_variations_fixed(self, number, var, var_transfo):
        """
        Sets the salient variations taking into account the remaining devices and threshold
        """
        sal = []
        sal_transfo = []
        for j in range(0,len(self.phase_labels)):
            cf = var/sum(var_transfo)
            ind = np.argpartition(cf[j], -number)[-number:]
            new_row = var[j][ind]
            new_row_transfo_a = var_transfo[0][ind]
            new_row_transfo_b = var_transfo[1][ind]
            new_row_transfo_c = var_transfo[2][ind]
            sal.append(new_row)
            sal_transfo.append([new_row_transfo_a,new_row_transfo_b,new_row_transfo_c])

        sal = np.array(sal)
        sal_transfo = np.array(sal_transfo)
        return sal, sal_transfo

    def get_salient_variation_fixed(self, number, var, var_transfo):
        """
        Sets the salient variations taking into account the remaining devices and threshold
        """
        total_var = sum(var_transfo)
        pl = self.partial_phase_labels
        cf = var/sum(var_transfo)
        ind = np.argpartition(cf, -number)[-number:]
        sal = var[ind]
        sal_transfo_a = var_transfo[0][ind]
        sal_transfo_b = var_transfo[1][ind]
        sal_transfo_c = var_transfo[2][ind]
        sal = np.array(sal)
        sal_transfo = np.array([sal_transfo_a, sal_transfo_b, sal_transfo_c])
        #plot_salient_comp(var,sal,ind)
        return sal, sal_transfo

    def find_phase(self, sal, sal_transfo):
        """
        Chooses phase with highest correlation to device j,
        based on it's salient factors sal (and the indexes therof sal_i
        """
        if len(sal) == 0:
            raise AssertionError("No salient components found")
        elif len(sal) < 3:
            best_corr = -np.inf
            for phase in range(0,3):
                corr = sal[0] / sal_transfo[phase][0]
                if corr > best_corr:
                    best_corr = corr
                    best_phase = phase + 1
        else:
            mean_sal = np.mean(sal)
            std_sal = np.std(sal)
            best_phase = 4
            best_corr = -np.inf
            lf = self.load_features_transfo
            for phase in range(0, 3):
                sal_phase = sal_transfo[phase]  # check if this is right
                mean_sal_phase = np.mean(sal_phase)
                std_sal_phase = np.std(sal_phase)
                corr = 1.0/(len(sal)-1) * sum(np.multiply((sal-mean_sal), (sal_phase-mean_sal_phase)) /
                                       np.multiply(std_sal, std_sal_phase))
                if corr >= best_corr:
                    best_corr = corr
                    best_phase = phase + 1
                #print(corr, " ", best_corr, " ", sal[j])
        return best_phase, best_corr

    def improved_find_phase(self, sal, sal_transfo):
        if len(sal) == 0:
            raise AssertionError("No salient components found")
        elif len(sal) < 3:
            best_corr = -np.inf
            second_best = 0
            for phase in range(0,3):
                corr = sal[0] / sal_transfo[phase][0]
                if corr > best_corr:
                    second_best = best_corr
                    best_corr = corr
                    best_phase = phase + 1
                elif corr > second_best:
                    second_best = corr
        else:
            mean_sal = np.mean(sal)
            std_sal = np.std(sal)
            best_phase = 4
            best_corr = -np.inf
            second_best = 0
            lf = self.load_features_transfo
            for phase in range(0, 3):
                sal_phase = sal_transfo[phase]  # check if this is right
                mean_sal_phase = np.mean(sal_phase)
                std_sal_phase = np.std(sal_phase)
                corr = 1.0/(len(sal)-1) * sum(np.multiply((sal-mean_sal), (sal_phase-mean_sal_phase)) /
                                       np.multiply(std_sal, std_sal_phase))
                if corr >= best_corr:
                    second_best = best_corr
                    best_corr = corr
                    best_phase = phase + 1
                elif corr > second_best:
                    second_best = corr
                #print(corr, " ", best_corr, " ", sal[j])
        corr_diff = best_corr - second_best
        return best_phase, corr_diff


    def assign_devices(self, sal_treshold=0.01, corr_treshold=0.0,salient_components=1,length=24*20):
        """
        """
        var = np.diff(self.load_features[:, 0:length], salient_components)
        var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
        sal, sal_transfo = self.get_salient_variations(sal_treshold, var, var_transfo)
        counter = 0
        for j in range(0,len(self.device_IDs)):
            if len(sal[j]) > 0 and self.partial_phase_labels[j] == 0:
                phase, corr = self.find_phase(sal[j], sal_transfo[j])
                if corr > corr_treshold:
                    self.sub_load_profile(j, phase)
                    counter += 1
                #else:
                    #print(corr, "is below correlation threshold")

        progress = sum(np.array(self.partial_phase_labels) != 0) / len(self.partial_phase_labels)
        acc = self.accuracy()
        print(counter, " devices allocated, ", progress*100, "% done, accuracy ", acc*100, "%")
        return progress

    def assign_devices_enhanced_tuning(self, nb_salient_components=10, nb_assignments=10, salient_components=1,length=24*20):
        """
        """
        var = np.diff(self.load_features[:, 0:length], salient_components)
        var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
        sal, sal_transfo = self.get_salient_variations_fixed(nb_salient_components, var, var_transfo)
        corr_list = []
        phase_list = []
        j_list = []
        counter = 0
        for j in range(0,len(self.device_IDs)):
            if self.partial_phase_labels[j] == 0.0:
                phase, corr = self.improved_find_phase(sal[j], sal_transfo[j])
                corr_list += [corr]
                phase_list += [phase]
                j_list += [j]
        if len(corr_list) >= nb_assignments:
            ind = np.argpartition(corr_list, -nb_assignments)[-nb_assignments:]
        else:
            ind = range(0, len(corr_list))
        for i in ind:
            self.sub_load_profile(j_list[i], phase_list[i])
            counter += 1

        progress = sum(np.array(self.partial_phase_labels) != 0) / len(self.partial_phase_labels)
        acc = self.accuracy()
        print(counter, " devices allocated, ", progress*100, "% done, accuracy ", acc*100, "%")
        return progress

    def finish_assign_devices(self, sal_treshold=0.01,salient_components=1,length=24*20):
        """
        """
        var = np.diff(self.load_features[:, 0:length], salient_components)
        var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
        sal, sal_transfo = self.get_salient_variations(sal_treshold, var, var_transfo)
        counter = 0
        for j in range(0,len(self.device_IDs)):
            if len(sal[j]) > 0 and self.partial_phase_labels[j] == 0:
                phase, corr = self.find_phase(sal[j], sal_transfo[j])
                self.sub_load_profile(j, phase)
                counter += 1
                #else:
                    #print(corr, "is below correlation threshold")

        progress = sum(np.array(self.partial_phase_labels) != 0) / len(self.partial_phase_labels)
        acc = self.accuracy()
        print(counter, " devices allocated, ", progress*100, "% done, accuracy ", acc*100, "%")
        return progress

    def load_correlation_xu_no_sort(self,nb_salient_components=400,salient_components=1,length=24*20):
        for j in range(0, len(self.device_IDs)):
            if self.partial_phase_labels[j] == 0:
                var = np.diff(self.load_features[j, 0:length], salient_components)
                var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
                sal, sal_transfo = self.get_salient_variation_fixed(nb_salient_components, var, var_transfo)
                if len(sal) > 0:
                    phase, corr = self.find_phase(sal, sal_transfo)
                    self.sub_load_profile(j, phase)
        acc = self.accuracy()
        print("All devices allocated, accuracy ", acc * 100, "%")

    def load_correlation_xu(self,salient_treshold=0.1,salient_components=1,length=24*20):
        """
        Implements load correlation algorithm as described by Xu et. al.
        Continues to assign devices as long as progress is being made
        """
        self.sort_devices_by_variation()
        #self.sort_devices_by_nb_salient_components(salient_treshold,salient_components)
        for j in range(0, len(self.device_IDs)):
            if self.partial_phase_labels[j] == 0:
                #plot_load_profile(self.load_features[j,:])
                var = np.diff(self.load_features[j, 0:length], salient_components)
                var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
                sal, sal_transfo = self.get_salient_variation(salient_treshold, var, var_transfo)
                if len(sal) > 0:
                    phase, corr = self.find_phase(sal, sal_transfo)
                    self.sub_load_profile(j, phase)
        acc = self.accuracy()
        print("All devices allocated, accuracy ", acc * 100, "%")

    def load_correlation_xu_fixed(self,nb_salient_components,salient_components=1,length=24*20):
        """
        Implements load correlation algorithm as described by Xu et. al.
        Continues to assign devices as long as progress is being made
        """
        self.sort_devices_by_variation()
        for j in range(0, len(self.device_IDs)):
            if self.partial_phase_labels[j] == 0:
                var = np.diff(self.load_features[j, 0:length], salient_components)
                var_transfo = np.diff(self.load_features_transfo[:, 0:length], salient_components)
                sal, sal_transfo = self.get_salient_variation_fixed(nb_salient_components, var, var_transfo)
                if len(sal) > 0:
                    phase, corr = self.find_phase(sal, sal_transfo)
                    self.sub_load_profile(j, phase)
        acc = self.accuracy()
        print("All devices allocated, accuracy ", acc * 100, "%")

    def load_correlation_enhanced_tuning(self,nb_salient_components=10, nb_assignments=10,salient_components=1,length=24*20):
        """
        Implements load correlation algorithm as described by Xu et. al.
        Continues to assign devices as long as progress is being made
        """
        progress = 0.0
        self.sort_devices_by_variation()

        while progress < 1.0:
            progress = self.assign_devices_enhanced_tuning(nb_salient_components=nb_salient_components,nb_assignments=nb_assignments,salient_components=salient_components,length=length)

    def accuracy(self):
        if len(self.partial_phase_labels) != len(self.phase_labels):
            raise IndexError("Phase labels not of same length")
        c = 0.0
        for i in range(0, len(self.partial_phase_labels)):
            if self.partial_phase_labels[i] == self.phase_labels[i]:
                c = c + 1.0
        try:
            acc = c / (len(self.phase_labels))
        except ZeroDivisionError:
            acc = np.nan
        return acc

    def sort_devices_by_nb_salient_components(self,treshold=10,salient_components=1):
        var = np.diff(self.load_features,salient_components)
        var_transfo = np.diff(self.load_features_transfo,salient_components)
        sal, sal_transfo = self.get_salient_variations(treshold, var, var_transfo)
        nb_sal = np.array([len(i) for i in sal])
        sort_order = nb_sal.argsort()
        #sort_order = np.mean(abs(lf_var),axis=1).argsort()
        i = np.array(self.device_IDs)
        self.device_IDs = i[sort_order[::-1]]
        self.load_features = self.load_features[sort_order[::-1]]
        self.voltage_features = self.voltage_features[sort_order[::-1]]
        self.phase_labels = np.array(self.phase_labels)[sort_order[::-1]]




    def add_noise(self, error=0, data="voltage"):
        if data == "voltage":
            noise = np.random.normal(0, error/3, [np.size(self.voltage_features, 0), np.size(self.voltage_features, 1)])
            self.voltage_features = self.voltage_features + noise
        if data == "load":
            error = error *0.007/3
            noise = np.random.normal(0, error, [np.size(self.load_features, 0), np.size(self.load_features, 1)])
            self.load_features = self.load_features + noise

    def reset_partial_phase_identification(self):
        self.partial_phase_labels = np.zeros(len(self.phase_labels))

    def reset_load_features_transfo(self,feeder):
        self.load_features_transfo = getattr(feeder,"load_features_transfo")


class PartialMissingPhaseIdentification(PartialPhaseIdentification):
    def __init__(self, feeder, include_three_phase = False, measurement_error = 0.0, length = 24, missing_ratio = 0.0):
        self.__dict__ = feeder.__dict__.copy()
        self.nb_missing = 0
        for col in self.load_features:
            if sum(col) == 0:
                self.nb_missing += 1
        nb_to_add = round(len(self.phase_labels)*missing_ratio) - self.nb_missing

        while nb_to_add > 0:
            self.load_features[random.randint(0, len(self.phase_labels) - 1)] = np.zeros(len(self.phase_labels))
            nb_to_add -= 1

    def add_missing(self,ratio):
        nb = round(len(self.phase_labels)*ratio)
        raise NotImplementedError

    # def accuracy(self):
    #     if len(self.partial_phase_labels) != len(self.phase_labels):
    #         raise IndexError("Phase labels not of same length")
    #     c = 0.0
    #     for i in range(0, len(self.partial_phase_labels)):
    #         if self.partial_phase_labels[i] == self.phase_labels[i]:
    #             c = c + 1.0
    #     try:
    #         acc = c / (len(self.phase_labels)-len(self.nb_missing))
    #     except ZeroDivisionError:
    #         acc = np.nan
    #     return acc

def plot_salient_comp(var,sal,ind):
    plt.figure(figsize=(8,3))
    x = np.arange(0, len(var))
    plt.plot(x,var*500,label="customer power consumption")
    plt.scatter(x[ind],sal*500,color='red',label='Salient component')
    plt.xlabel("Time step (h)",fontsize=14)
    plt.ylabel("Power (Kwh)",fontsize=14)
    plt.xlim([0,7*24])
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_load_profile(power):
    plt.figure(figsize=(8,3))
    x = np.arange(0, len(power))
    plt.plot(x,power*500,label="customer power consumption")
    plt.xlabel("Time step (h)",fontsize=14)
    plt.ylabel("Power (Kwh)",fontsize=14)
    plt.xlim([0,7*24])
    plt.tight_layout()
    plt.legend()
    plt.show()

def plot_transfo_profile(power):
    plt.figure(figsize=(8,3))
    x = np.arange(0, len(power))
    plt.plot(x,power*500,label="Transfo power consumption")
    plt.xlabel("Time step (h)",fontsize=14)
    plt.ylabel("Power (Kwh)",fontsize=14)
    plt.xlim([0,7*24])
    plt.tight_layout()
    plt.show()
