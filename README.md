# A motion planner blueprint for for [Commonroad](https://commonroad.in.tum.de/) 

Important notes: 
- this code provides a motion planner as in  [commonroad search repository](https://gitlab.lrz.de/tum-cps/commonroad-search/) (which is licenced under GNU General Public License v3.0.)
- see the student_example.py in the [commonroad_search repo](https://gitlab.lrz.de/tum-cps/commonroad-search/-/blob/master/SMP/motion_planner/search_algorithms/student_example.py)

- if you use this in the TUM Challenge: Techniques in Artificial Intelligence (IN2062), it might be considered plagiatism. no liablity.
- also if you use this search heueristik in your own tesla, no liablity. (see GNU General Public License v3.0.)

## Performance:
- evaluation on the [2020a Version of Commonroad](https://gitlab.lrz.de/tum-cps/commonroad-scenarios) (2077 scenarios total)
- evaluation with BMW320i, KS2, SM1 and a [default motion primitves set] (https://gitlab.lrz.de/tum-cps/commonroad-search/-/tree/master/SMP/maneuver_automaton/primitives) ```V_0.0_20.0_Vstep_4.0_SA_-1.066_1.066_SAstep_0.18_T_0.5_Model_BMW_320i```
- Batch_processing: timelimit set to 30 seconds, 12 Threads (Ryzen 5600x, 32gb RAM)


|Property  |    number of scenarios|
| ------------- |:-------------:|
|Total number of scenarios:  	  |      2077|
|Solution found:               	|      1588|
|Solution found but invalid:   	|         6|
|Solution not found:           	|        70|
|Exception occurred:            |         2|
|Time out:                     	|       407|

## Answers to Infrequently asked questions (IAQ):

- For ideas, please feel free to contact me (contact details on Github or [Website](https://michaelfeil.github.io) )
- Obviously no weights are tuned in this blueprint 
- no szenarios types are distinguished. 
(e.g. in a scenario without goal, a reference path that shows a way to the goal is not as helpful as with goal)
- if makes sense to use a different (or even multiple) motion planner sets)
- I do not plan to provide my non vanilla/blueprint version in the future.

## Visualizaton

For the [USA_US101-21_1_T-1](https://commonroad.in.tum.de/submissions/ranking/KS2:SM1:USA_US101-21_1_T-1:2020a) the *relevant* part (from start of the ego vehicle to goal) of the reference path. Since the interval of time_steps of arrival is 70-80, the relevant reference path should be completed in 75 steps. Given the closest position towards the reference path and time_step at any giiven time of the ego vehicle, an estimate of the average speed needed and the desired subsection of the reference path that should be completed at this time_step, can be returned.

![route planner on USA_US101-21_1_T-1](/png/USA_US101-21_1_T-1_route.png " part of route planner from start to finish of USA_US101-21_1_T-1")


## Motion Primitives

If you plan to follow the reference path, you might require a denser set of motion primitives to solve some scenarios.
There are also effects on changing the duration of the motion primitive on the turning radius. 

motion primitive with a duration of 0.5 seconds / 5 steps in commonroad Axes in m/0.5s:
![motion_primitves_0_5_second](/png/motion_primitves_0_5_second.png "motion primitive with a duration of 0.5 seconds / 5 steps in commonroad Axes in m/0.5s")
motion primitive with a duration of 1 second / 10 steps in commonroad. Axes in m/1s:
![motion_primitves_1second.png](/png/motion_primitves_1second.png "motion primitive with a duration of 1 second / 10 steps in commonroad. Axes in m/1s")
