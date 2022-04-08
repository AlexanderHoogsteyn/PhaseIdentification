import json
import random
import numpy as np
import pandas as pd
import os
import copy
import glob
import matplotlib.pyplot as plt

class ErrorClass(object):

    def __init__(self,accuracy_class,s=False,n_power=3.5,n_voltage=230,power_base=500,voltage_base=230):
        """
        Adds noise to the data according to the given accuracy class:
        Common classes: 1.0, 0.5, 0.2, 0.1
        """
        self.accuracy_class = accuracy_class
        self.n_voltage = n_voltage
        self.n_power = n_power
        self.power_base = power_base
        self.voltage_base = voltage_base
        self.s = s
        self.set_voltage_noise()
        self.set_load_noise()

    def set_voltage_noise(self):
        self.voltage_noise_sigma = self.accuracy_class/3*self.n_voltage/self.voltage_base/100

    def set_load_noise(self):
        self.load_noise_sigma = self.accuracy_class/3*self.n_power/self.power_base

    def get_voltage_noise(self):
        return self.voltage_noise_sigma

    def get_load_noise(self):
        return self.load_noise_sigma

    def reroll_noise(self):
        self.set_voltage_noise()
        self.set_load_noise()

class Feeder(object):
    """
    A Feeder object contains all the data (voltage + load) that is needed to perform the phase identification. The object will store the features in  a numpy array as well as some metadata
    such as list of the features used and the ID's of the feeders.
    """

    def __init__(self, feederID='65019_74469', include_three_phase=False,error_class=ErrorClass(0),data="POLA_data/"):
        """
        Initialize the feeder object by reading out the data from JSON files in the specified directory.
        feederID = full identification number of the feeder
        include_three_phase = put on True if you want to include 3 phase customers in your analysis, 3 phase customers
                              will be regarded as 3 single phase customers
        measurement_error = std of the amount of noise added to the voltage (p.u.)
        length = number of data samples used, the first samples are used
        """
        features = []
        dir = os.path.dirname(os.path.realpath(__file__))
        self._path_data = os.path.join(dir, "../../data/"+data)
        self._path_topology = os.path.join(dir, "../../data/POLA/")
        self.feederID = feederID

        configuration_file = self._path_topology + feederID + '_configuration.json'
        with open(configuration_file) as current_file:
            config_data = json.load(current_file)
        self.id = config_data['gridConfig']['id']
        self.transfo_id = config_data['gridConfig']['trafoId']
        devices_path = config_data['gridConfig']['devices_file']
        # branches_path = config_data['gridConfig']['branches_file']
        self.nb_customers = config_data['gridConfig']['totalNrOfEANS']

        self.phase_labels = []
        self.device_IDs = []
        self.multiphase_IDs = []
        self.bus_IDs = []
        voltage_features = []
        load_features = []

        with open(os.path.join(os.path.dirname(self._path_topology), feederID + "_devices.json")) as devices_file:
            devices_data = json.load(devices_file)
        with open(os.path.join(os.path.dirname(self._path_data), feederID + "_voltage_data.json")) as voltage_file:
            voltage_data = json.load(voltage_file)
        with open(os.path.join(os.path.dirname(self._path_data), feederID + "_load_data.json")) as load_file:
            load_data = json.load(load_file)

        for device in devices_data['LVcustomers']:
            deviceID = device.get("deviceId")
            busID = device.get("busId")
            device_phases = device.get("phases")
            empty_power_profile = False
            if include_three_phase or len(device_phases) == 1:
                #print("device: ", deviceID, " bus: ", busID, " phase: ", device_phases)
                for phase in device_phases:
                    v = voltage_data[str(busID)]
                    p = load_data[str(deviceID)]
                    if phase == 1 and np.mean(p["phase_A"]) != 0:
                        voltage_features.append(v["phase_A"])
                        load_features.append(p["phase_A"])
                    elif phase == 2 and np.mean(p["phase_B"]) != 0:
                        voltage_features.append(v["phase_B"])
                        load_features.append(p["phase_B"])
                    elif phase == 3 and np.mean(p["phase_C"]) != 0:
                        voltage_features.append(v["phase_C"])
                        load_features.append(p["phase_C"])
                    else:
                        empty_power_profile = True
                if len(device_phases) == 3 and not empty_power_profile:
                    self.multiphase_IDs += [deviceID]
                    self.device_IDs += [deviceID, deviceID, deviceID]
                    self.bus_IDs += [busID, busID, busID]
                    self.phase_labels += device_phases
                elif not empty_power_profile:
                    self.device_IDs += [deviceID]
                    self.bus_IDs += [busID]
                    self.phase_labels += device_phases


        self.voltage_features_transfo = np.zeros([3, len(voltage_data["transfo"]["phase_A"])])
        self.voltage_features_transfo[0] = voltage_data["transfo"]["phase_A"]
        self.voltage_features_transfo[1] = voltage_data["transfo"]["phase_B"]
        self.voltage_features_transfo[2] = voltage_data["transfo"]["phase_C"]

        self.load_features_transfo = np.zeros([3, len(load_data["transfo"]["phase_A"])])
        self.load_features_transfo[0] = load_data["transfo"]["phase_A"]
        self.load_features_transfo[1] = load_data["transfo"]["phase_B"]
        self.load_features_transfo[2] = load_data["transfo"]["phase_C"]

        self.voltage_features = np.array(voltage_features)
        self.load_features = np.array(load_features)
        self.phase_labels = np.array(self.phase_labels)

        size = (np.size(self.voltage_features, 0), np.size(self.voltage_features, 1))
        if error_class.s == False:
            self.voltage_features = self.voltage_features + np.random.normal(0,error_class.get_load_noise(), size)
            self.load_features = self.load_features + np.random.normal(0,error_class.get_load_noise(), size)
        else:
            self.voltage_features = self.voltage_features + np.random.normal(0,error_class.get_load_noise(), size)
            self.load_features = np.random.normal(self.load_features, self.load_features * error_class.accuracy_class/3)
        self.partial_phase_labels = np.zeros(len(self.phase_labels))




    def plot_data(self, data, ylabel="(pu)", length=24):
        """
        Makes a 2D plot of a Feeder object.
        data specifies the data to be plotted, should be a 2D numpy array.
        length specifies the length of the data plotted, cannot be longer then the length of the feeder object
        """
        plt.figure(figsize=(8, 6))
        markers = ["s", "o", "D", ">", "<", "v", "+"]
        x = np.arange(0, length)
        i = 0
        for line in data:
            line = line[0:length]
            color = plt.cm.viridis(float(i) / (float(self.nb_customers) - 1.0))
            plt.plot(x, line, color=color, alpha=0.85)
            i = i + 1
        plt.xlabel("time step (30 min intervals")
        plt.ylabel(ylabel)
        plt.show()

    def plot_voltages(self, ylabel="Voltage (pu)", length=48):
        return self.plot_data(self.voltage_features, ylabel, length)

    def plot_load_profiles(self, ylabel="Power (kW)", length=48):
        return self.plot_data(self.load_features * 500, ylabel, length)

    def plot_load_profiles_transfo(self, ylabel="Power (kW)", length=48):
        return self.plot_data(self.load_features_transfo * 500, ylabel, length)

    def change_data_representation(self, representation="delta", data="voltage", inplace=True):
        """
        Changes the data representation from raw to delta or binary
        Not used in final implementation
        """
        if data == "voltage":
            original_data = self.voltage_features
            original_transfo_data = self.voltage_features_transfo
        elif data == "load":
            original_data = self.load_features
            original_transfo_data = self.voltage_features_transfo
        else:
            return print("enter voltage or load as data")

        new_data = []
        new_transfo_data = []
        if representation == "delta" or representation == "binary":
            for row in original_data:
                new_row = [0] * len(row)
                for i in range(1, len(row)):
                    new_row[i] = row[i] - row[i - 1]
                new_data.append(new_row)
            new_data = np.array(new_data)

            for row in original_transfo_data:
                new_row = [0] * len(row)
                for i in range(1, len(row)):
                    new_row[i] = row[i] - row[i - 1]
                new_transfo_data.append(new_row)
            new_transfo_data = np.array(new_transfo_data)

        if representation == "binary":
            new_data[new_data > 0] = 1
            new_data[new_data < 0] = -1
            new_transfo_data[new_transfo_data > 0] = 1
            new_transfo_data[new_transfo_data < 0] = -1
        if inplace:
            if data == "voltage":
                self.voltage_features = np.array(new_data)
                self.voltage_features_transfo = np.array(new_transfo_data)
            if data == "load":
                self.load_features = np.array(new_data)
                self._load_features_transfo = np.array(new_transfo_data)
        else:
            new_self = copy.deepcopy(self)
            if data == "voltage":
                new_self.voltage_features = np.array(new_data)
                new_self.voltage_features_transfo = np.array(new_transfo_data)

            if data == "load":
                new_self.load_features = np.array(new_data)
                new_self.voltage_features_transfo = np.array(new_transfo_data)
            return new_self

    def truncate_voltages(self):
        """
        Truncates voltages to the nearest volt
        """
        vf = self.voltage_features
        vf = vf*230     #change from pu to V
        vf = np.trunc(vf)
        self.voltage_features = vf

    def lower_data_resolution(self,n):
        self.voltage_features = np.array([x[::n] for x in self.voltage_features])
        self.voltage_features_transfo = np.array([x[::n] for x in self.voltage_features_transfo])
        self.load_features = np.array([x[::n] for x in self.load_features])
        self.load_features_transfo = np.array([x[::n] for x in self.load_features_transfo])


    def set_sm_pentration(self,ratio):
        nb = round(len(self.phase_labels) * ratio)
        nb_to_remove = len(self.phase_labels) - nb
        if nb_to_remove < 0:
            nb_to_remove = 0
        rng = np.random.default_rng()
        i_to_remove = rng.choice(len(self.phase_labels), nb_to_remove, replace=False)
        self.load_features = np.delete(self.load_features, i_to_remove, axis=0)
        self.voltage_features = np.delete(self.voltage_features, i_to_remove, axis=0)
        self.phase_labels = np.delete(self.phase_labels, i_to_remove, axis=0)

    def sort_devices_by_variation(self):
        """
        Devices are sorted such that the phases with highest variability are handled first
        using mean absolute variability (MAV)
        """
        lf = self.load_features
        vf = self.voltage_features
        lf_var = np.diff(self.load_features, 1)
        i = np.array(self.device_IDs)
        lf_mav = []
        for col in lf_var:
            lf_mav.append(sum(abs(col))/len(col))
        lf_mav = np.array(lf_mav)
        sort_order = lf_mav.argsort()
        #sort_order = np.mean(abs(lf_var),axis=1).argsort()
        self.device_IDs = i[sort_order[::-1]]
        self.load_features = lf[sort_order[::-1]]
        self.voltage_features = vf[sort_order[::-1]]
        self.phase_labels = np.array(self.phase_labels)[sort_order[::-1]]

    def random_sort(self):
        lf = self.load_features
        vf = self.voltage_features
        i = np.array(self.device_IDs)
        sort_order = np.random.permutation(len(self.device_IDs))
        self.device_IDs = i[sort_order[::-1]]
        self.load_features = lf[sort_order[::-1]]
        self.voltage_features = vf[sort_order[::-1]]
        self.phase_labels = np.array(self.phase_labels)[sort_order[::-1]]

    def build_power_features(self,diff=0):
        lf = np.diff(self.load_features, diff)
        lf_transfo = np.diff(self.load_features_transfo, diff)
        lf_a = np.array([lf[i]/lf_transfo[0] for i in range(0,len(lf))])
        lf_b = np.array([lf[i]/lf_transfo[1] for i in range(0,len(lf))])
        lf_c = np.array([lf[i]/lf_transfo[2] for i in range(0,len(lf))])
        return np.concatenate([lf_a, lf_b, lf_c], axis=1)

    def get_mav_imbalance(self):
        mean_ref = np.mean(self.voltage_features_transfo)
        mav_imbalance = []
        for voltage_profile in self.voltage_features:
            mav_imbalance.append(np.mean(abs(voltage_profile/mean_ref - 1)))
        return np.array(mav_imbalance)*100