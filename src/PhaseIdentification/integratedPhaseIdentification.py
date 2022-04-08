from PhaseIdentification.powerBasedPhaseIdentification import *
from PhaseIdentification.voltageBasedPhaseIdentification import *
from VisualizePhaseIdentification.visualization import *
import numpy as np
from numpy.random import default_rng
import copy


class IntegratedPhaseIdentification(PartialPhaseIdentification):

    def __init__(self, feeder, error_class=ErrorClass(0)):
        PartialPhaseIdentification.__init__(self, feeder, error_class)

    def voltage_assisted_load_correlation(self, sal_treshold_load=1, sal_treshold_volt=0.4, corr_treshold=0.2,
                                          volt_assist=0.0, length=24*20,salient_components=1, printout_level=1):
        """
        Also uses salient voltage measurements, therefore also feeder voltage needed
        """
        counter = 1
        completeness = 0

        # Sorting done according to highest variance in load
        self.sort_devices_by_variation()
        if printout_level >= 3:
            C = CorrelationCoeficients(self)
            C.visualize_correlation_all()

        while counter > 0 and completeness != 1:

            # Load salient components
            var_load = tuple(np.diff(self.load_features[:, 0:length], k) for k in range(0, salient_components))
            var_transfo_load = tuple(np.diff(self.load_features_transfo[:, 0:length], k) for k in range(0, salient_components))
            var_load = np.concatenate(var_load, axis=1)
            var_transfo_load = np.concatenate(var_transfo_load, axis=1)
            sal_load, sal_transfo_load = self.get_salient_variations(sal_treshold_load, var_load, var_transfo_load)
            # print("# Salient components load between ", min(nb_sal), " and ", max(nb_sal))

            # Voltage salient components
            var_volt = np.diff(self.voltage_features[:, 0:length], 1)
            var_transfo_volt = np.diff(self.voltage_features_transfo[:, 0:length], 1)
            # sal_volt, sal_transfo_volt = self.get_salient_variations(sal_treshold_volt, var_volt, var_transfo_volt)
            # ("# Salient components voltage between ", min(nb_sal), " and ", max(nb_sal))

            # Reactive power salient components?

            counter = 0
            for j in range(0, len(self.device_IDs)):
                if self.partial_phase_labels[j] == 0:
                    phase, corr = self.find_phase(var_volt[j], var_transfo_volt, sal_load[j], sal_transfo_load[j],
                                                  volt_assist)
                    if corr > corr_treshold:
                        # Subtract assigned load from transfo measurement & update variance "var_transfo_load"
                        self.sub_load_profile(j, phase)
                        counter += 1
                    # else:
                    #   print(corr, "is below correlation threshold")

            try:
                completeness = sum(np.array(self.partial_phase_labels) != 0) / len(self.partial_phase_labels)
            except ZeroDivisionError:
                completeness = 1
            acc = self.accuracy()
            if printout_level >= 1:
                print(counter, " devices allocated, ", completeness * 100, "% done, accuracy ", acc * 100, "%")
            if printout_level  >= 4:
                C = CorrelationCoeficients(self)
                C.visualize_correlation_all()
        if completeness != 1:
            # Complete remaining
            # Load salient components
            var_load = np.diff(self.load_features[:, 0:length], 1)
            var_transfo_load = np.diff(self.load_features_transfo[:, 0:length], 1)
            sal_load, sal_transfo_load = self.get_salient_variations(sal_treshold_load, var_load, var_transfo_load)
            # print("# Salient components load between ", min(nb_sal), " and ", max(nb_sal))

            # Voltage salient components
            var_volt = np.diff(self.voltage_features[:, 0:length], 1)
            var_transfo_volt = np.diff(self.voltage_features_transfo[:, 0:length], 1)
            # sal_volt, sal_transfo_volt = self.get_salient_variations(sal_treshold_volt, var_volt, var_transfo_volt)
            # ("# Salient components voltage between ", min(nb_sal), " and ", max(nb_sal))

            # Reactive power salient components?

            counter = 0
            for j in range(0, len(self.device_IDs)):
                if self.partial_phase_labels[j] == 0:
                    phase, corr = self.find_phase(var_volt[j], var_transfo_volt, sal_load[j], sal_transfo_load[j],
                                                  volt_assist)
                    # Subtract assigned load from transfo measurement & update variance "var_transfo_load"
                    self.sub_load_profile(j, phase)
                    counter += 1
                    # else:
                    #   print(corr, "is below correlation threshold")

            completeness = sum(np.array(self.partial_phase_labels) != 0) / len(self.partial_phase_labels)
            acc = self.accuracy()
            if printout_level >= 1:
                print(counter, " devices allocated, ", completeness * 100, "% done, accuracy ", acc * 100, "%")
            if printout_level >= 4:
                C = CorrelationCoeficients(self)
                C.visualize_correlation_all()


class IntegratedMissingPhaseIdentification(IntegratedPhaseIdentification):
    def __init__(self, feeder, error_class=ErrorClass(0)):
        IntegratedPhaseIdentification.__init__(self, feeder, error_class=error_class)
        self.nb_missing = 0
        self.nb_original_devices = len(self.phase_labels)

    def add_missing(self, ratio):
        nb = round(self.nb_original_devices * ratio)
        nb_to_add = nb - self.nb_missing
        if nb_to_add < 0:
            nb_to_add = 0
        rng = np.random.default_rng()
        i_to_remove = rng.choice(len(self.phase_labels), nb_to_add, replace=False)
        self.load_features = np.delete(self.load_features, i_to_remove, axis=0)
        self.voltage_features = np.delete(self.voltage_features, i_to_remove, axis=0)
        self.phase_labels = np.delete(self.phase_labels, i_to_remove, axis=0)
        self.partial_phase_labels = np.delete(self.partial_phase_labels, i_to_remove, axis=0)

        self.nb_missing += len(i_to_remove)
        self.missing_ratio = ratio


def power_voltage_conform_method(feeder, length=24*20, salient_components=1,nb_salient_components=400,voltage_meter_penetration=1):
    nb_devices = len(feeder.device_IDs)
    phase_identification_volt = PhaseIdentification(feeder)
    phase_identification_load = PartialPhaseIdentification(feeder)
    phase_identification_load.sort_devices_by_variation()

    phase_identification_volt.sort_devices_by_variation()
    phase_identification_volt.voltage_correlation_transfo_ref(length=length)
    nb_devices = len(phase_identification_volt.partial_phase_labels)
    meters_without_voltage_data = np.sort(np.random.choice(nb_devices,int(nb_devices*(1-voltage_meter_penetration)),replace=False))
    phase_labels_volt = np.array(phase_identification_volt.partial_phase_labels)
    phase_labels_volt[meters_without_voltage_data] = 5

    combined_phase_labels = np.zeros(nb_devices)
    feeder_combined = copy.deepcopy(feeder)
    phase_identification_combined = PartialPhaseIdentification(feeder_combined)
    phase_identification_combined.sort_devices_by_variation()
    progress = 1
    prev_conform_i = np.array([False]*len(feeder_combined.device_IDs))
    while progress > 0:
        phase_identification_load.load_correlation_xu_no_sort(nb_salient_components=nb_salient_components,
                                                            salient_components=salient_components, length=length)
        conform_i = phase_identification_load.partial_phase_labels == phase_labels_volt
        combined_phase_labels[conform_i] = phase_identification_load.partial_phase_labels[conform_i]
        remaining = np.arange(0, nb_devices, 1)[np.logical_xor(conform_i, prev_conform_i)]
        for i in remaining:
            phase_identification_combined.sub_load_profile(i, int(combined_phase_labels[i]))
        phase_identification_load = copy.deepcopy(phase_identification_combined)
        prev_conform_i = conform_i
        progress = len(remaining)

    phase_identification_combined.load_correlation_xu_no_sort(nb_salient_components=nb_salient_components,
                                                            salient_components=salient_components, length=length)
    acc_combined = phase_identification_combined.accuracy()
    print("Combined method accuracy: ", acc_combined)
    return acc_combined

def boost_voltage_with_power(feeder,length=24*20,volt_length=24*20, salient_components=1,nb_salient_components=400,voltage_meter_penetration=1,select_biggest=False, min_corr=-np.inf,var_filter=False):
    nb_devices = len(feeder.device_IDs)
    feeder.sort_devices_by_variation()
    feeder_load = copy.deepcopy(feeder)
    phase_identification_volt = PhaseIdentification(feeder)
    phase_identification_volt.voltage_correlation_transfo_ref(length=volt_length, min_corr=min_corr)

    if select_biggest==False:
        meters_without_voltage_data = np.sort(
            np.random.choice(nb_devices, int(nb_devices * (1 - voltage_meter_penetration)), replace=False))
        phase_labels_volt = np.array(phase_identification_volt.partial_phase_labels)
        phase_labels_volt[meters_without_voltage_data] = 0
    else:
        number = int(nb_devices * (1 - voltage_meter_penetration))
        total_load = np.sum(feeder.load_features, axis=1)
        phase_labels_volt = np.array(phase_identification_volt.partial_phase_labels)
        if number == len(total_load):
            phase_labels_volt = np.array([0]*number)
        elif number != 0:
            meters_without_voltage_data = np.argpartition(total_load, number)[:number]
            phase_labels_volt[meters_without_voltage_data] = 0

    if var_filter == True:
        phase_labels_volt[phase_identification_volt.get_mav_imbalance()<0.02] = 0

    phase_identification_load = PartialPhaseIdentification(feeder_load)
    for i, phase in enumerate(phase_labels_volt):
        phase_identification_load.sub_load_profile(i,int(phase),loss_factor=0.9)

    phase_identification_load.load_correlation_xu_no_sort(nb_salient_components=nb_salient_components,
                                                              salient_components=salient_components, length=length)
    acc_combined = phase_identification_load.accuracy()
    print("Combined method accuracy: ", acc_combined)
    return acc_combined

def power_and_voltage_bagging(feeder,length=24*20, volt_length=24*20, salient_components=1,nb_salient_components=400,voltage_meter_penetration=1,select_biggest=False, min_corr=-np.inf,var_filter=False):
    nb_devices = len(feeder.device_IDs)
    feeder_load = copy.deepcopy(feeder)
    phase_identification_volt = PhaseIdentification(feeder)
    phase_identification_volt.sort_devices_by_variation()
    phase_identification_volt.voltage_correlation_transfo_ref(length=volt_length, min_corr=min_corr)


    nb_devices = len(phase_identification_volt.partial_phase_labels)
    if select_biggest==False:
        meters_without_voltage_data = np.sort(
            np.random.choice(nb_devices, int(nb_devices * (1 - voltage_meter_penetration)), replace=False))
        phase_labels_volt = np.array(phase_identification_volt.partial_phase_labels)
        phase_labels_volt[meters_without_voltage_data] = 5
    else:
        number = int(nb_devices * (1 - voltage_meter_penetration))
        total_load = np.sum(feeder.load_features, axis=1)
        phase_labels_volt = np.array(phase_identification_volt.partial_phase_labels)
        if number == len(total_load):
            phase_labels_volt = np.array([5]*number)
        elif number != 0:
            meters_without_voltage_data = np.argpartition(total_load, number)[:number]
            phase_labels_volt[meters_without_voltage_data] = 5

    if var_filter == True:
        phase_labels_volt[phase_identification_volt.get_mav_imbalance()<0.2] = 0
    phase_identification_volt.partial_phase_labels = phase_labels_volt

    phase_identification_load = PartialPhaseIdentification(feeder_load)
    phase_identification_load.sort_devices_by_variation()
    phase_identification_load.load_correlation_xu_no_sort(nb_salient_components=nb_salient_components,
                                                              salient_components=salient_components, length=length)
    phase_identification_volt.partial_phase_labels[phase_labels_volt == 5] = phase_identification_load.partial_phase_labels[phase_labels_volt == 5]

    acc_combined = phase_identification_volt.accuracy()
    print("Combined method accuracy: ", acc_combined)
    return acc_combined

def boost_power_with_voltage(feeder_1, length=24*20,salient_components=1,nb_salient_components=400,power_treshold=10,voltage_meter_penetration=1):
    feeder = PartialPhaseIdentification(feeder_1)
    feeder.sort_devices_by_variation()
    for j in range(0, len(feeder.device_IDs)):
        if feeder.partial_phase_labels[j] == 0:
            var = np.diff(feeder.load_features[j, 0:length], salient_components)
            var_transfo = np.diff(feeder.load_features_transfo[:, 0:length], salient_components)
            sal, sal_transfo = feeder.get_salient_variation_fixed(nb_salient_components, var, var_transfo)
            if len(sal) > 0:
                phase, corr_diff = feeder.improved_find_phase(sal, sal_transfo)
                if corr_diff > power_treshold:
                    feeder.sub_load_profile(j, phase)

    feeder_2 = PhaseIdentification(feeder_1)

    feeder_2.voltage_correlation_transfo_ref(length=length)

    nb_devices = len(feeder_2.partial_phase_labels)
    meters_without_voltage_data = np.sort(
        np.random.choice(nb_devices, int(nb_devices * (1 - voltage_meter_penetration)), replace=False))
    phase_labels_volt = np.array(feeder_2.partial_phase_labels)
    phase_labels_volt[meters_without_voltage_data] = 0


    acc = feeder.accuracy()
    print("All devices allocated, accuracy ", acc * 100, "%")
    return acc
