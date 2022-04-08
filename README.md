#       Phase identification algorithms toolbox
I developed a toolbox in Python that makes it possible to simulate different
- Algorithms:
        Voltage correlation, clustering, load correlation, hybrid correlation​
- Accuracy class of SM:
        Class 1.0%, Class 0.1% (% of max error of the nominal voltage/power)​
- Length of data collection
- Level of SM penetration ( % of houses that have a SM)
##      Distribution network data
The toolbox requires 2 different sources of data, data on the topology of the distribution network and time-series data of (simulated) smart meter.
### Topology data
The topology data needs to be provided in .json format in a specific structure. An example topology of a publicly available distribution network in Spain called POLA is provided. The topology data of POLA is provided in \data\POLA.
### Smart meter data

### Feeder object class
The aforementioned data sources are needed to then create the Feeder object on which then phase identification algorithms can be applied
```Python
feeder_id = "86315_785383"
feeder = Feeder(feederID=feeder_id, include_three_phase=True,data="POLA_data/",topology_data="POLA/")
"""
        feederID = full identification number of the feeder
        include_three_phase = put on True if you want to include 3 phase customers in your analysis, 3 phase customers
                              will be regarded as 3 single phase customers
        Set Errorclass object containing SM class info with error_class: Errorclass
        Set path starting from data directory where smart meter data can be found using data: string
        Set path starting from data directory where network topology data can be found using topology_data: string
"""
```
This object will not be mutaded if a phase identification is performed. Therefore it only needs to be created once when doing Monte Carlo simulations.

## Voltage based phase ID 
To perform a phase identification algorithm on a feeder a PhaseIdentification object needs to be created. At this stage noise should be added. The creation of this object is computationally light unlike Feeder objects. 
```Python
feeder = Feeder(feederID=feeder_id, include_three_phase=include_three_phase)
phase_identification = PhaseIdentification(feeder, ErrorClass(accuracy_class, s=False))
        """
        Initialize the PhaseIdentification object by reading out the data from JSON files in the specified directory.
        feeder = attach feeder object or feederID
        include_three_phase = put on True if you want to include 3 phase customers in your analysis, 3 phase customers
                              will be regarded as 3 single phase customers
        measurement_error = std of the amount of noise added to the voltage (p.u.)
        length = number of data samples used, the first samples are used
        """
phase_identification.voltage_correlation_transfo_ref(length=base_length)
```
Various algorithms can then by applied on Phaseidentification objects. 
## Power based phase ID 
In power based phase identification algorithms the order in which customers are identified matters and it is needed to keep track of which customers are already allocated. Therefore the power based methods should be applied on another object type called PartialPhaseIdentification in a similar manner.
```Python
 feeder = Feeder(feederID=feeder_id, include_three_phase=True,data="POLA_data/",topology_data="POLA/")
 phase_identification = PartialPhaseIdentification(feeder, ErrorClass(accuracy_class,s=False))
 phase_identification.load_correlation_xu_fixed(nb_salient_components=nb_salient_components,salient_components=1,length=length)
```

## Notes & limitations
- Requires Numpy 1.19 to work
