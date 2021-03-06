# A motion planner blueprint for  [Commonroad](https://commonroad.in.tum.de/) 

Important notes: 
- this code provides a motion planner as in  [commonroad search repository](https://gitlab.lrz.de/tum-cps/commonroad-search/) (which is licenced under GNU General Public License v3.0.)
- to *run the code*, pull the [commonroad_search repo](https://gitlab.lrz.de/tum-cps/commonroad-search/-/blob/master/SMP/motion_planner/search_algorithms/student.py) and replace the student.py. Also follow the instructions of the search repo on how to set up the docker.
- in case you are a student at TU Munich and participate in TUM Challenge of Techniques in Artificial Intelligence (IN2062), it might be considered plagiatism if you submit parts of this code. no liablity.

## Performance:
- evaluation on the [2020a Version of Commonroad](https://gitlab.lrz.de/tum-cps/commonroad-scenarios) (2077 scenarios total)
- evaluation with BMW320i, KS2, SM1 and a [default motion primitves set] (https://gitlab.lrz.de/tum-cps/commonroad-search/-/tree/master/SMP/maneuver_automaton/primitives) ```V_0.0_20.0_Vstep_4.0_SA_-1.066_1.066_SAstep_0.18_T_0.5_Model_BMW_320i```
- Batch_processing: timelimit set to 30 seconds, 12 Threads (Ryzen 5600x, 32gb RAM)
- only uses the [Baseline Solution](./student-baseline-michaelf.py). No weights are tuned (set to 1), this is the minimal approach and can easily be improved.

|Property  |    number of scenarios|
| ------------- |:-------------:|
|Total number of scenarios:  	  |      2077|
|Solution found:               	|      1588|
|Solution found but invalid:   	|         6|
|Solution not found:           	|        70|
|Exception occurred:            |         2|
|Time out:                     	|       407|


## Visualizaton

For the [USA_US101-21_1_T-1](https://commonroad.in.tum.de/submissions/ranking/KS2:SM1:USA_US101-21_1_T-1:2020a) scanario, we extract the *relevant* part (from start of the ego vehicle to goal) of the reference path. Since the interval of time_steps of arrival is 70-80, it is a good assumption the relevant reference path can  be completed in ~75 steps. Given the closest position towards the reference path and time_step at any giiven time of the ego vehicle, an estimate of the average speed needed and the progess of the reference path that should be achieved at this time_step, can be returned. Also distance and orientation towards the reference path help to guide the low level search. 

Extracted part of reference_route from start to finish of the USA_US101-21_1_T-1 Scenario:

![Image of the USA_US101 Planned Route.](/png/USA_US101-21_1_T-1_route.png "USA_US101-21_1_T-1route")
Now we "only" need to guide the search along the reference path in time and in space. This how the solution looks in Action. 

![USA_US101 GIF](/png/USA_US101-21_1_T-1demo.gif "USA_US101-21_1_T-1demo.gif")


(until 18.Jan 2020, 3 out of ~300 users found a solution for this [scenario](https://commonroad.in.tum.de/submissions/ranking/KS2:SM1:USA_US101-21_1_T-1:2020a) )

## Motion Primitives

If you plan to follow the reference path, you might require a denser set of motion primitives to solve some scenarios.
There are also effects on changing the duration of the motion primitive on the turning radius, as shown below. 

motion primitive with a duration of 0.5 seconds / 5 steps in commonroad Axes in m/0.5s: (avg. branching factor 9.35)
![motion_primitves_0_5_second.jpg](/png/motion_primitves_0_5_second.jpg "motion primitive with a duration of 0.5 seconds / 5 steps in commonroad Axes in m/0.5s")
motion primitive with a duration of 1 second / 10 steps in commonroad. Axes in m/1s: (avg. branching factor 23.20)
![motion_primitves_1_second.jpg](/png/motion_primitves_1_second.jpg "motion primitive with a duration of 1 second / 10 steps in commonroad. Axes in m/1s")

## A couple of generated solutions:

USA_US101-2_1_T-1:

![](/png/USA_US101-2_1_T-1.gif  " USA_US101-2_1_T-1.gif")

USA_Lanker-2_10_T-1:

![](/png/USA_Lanker-2_10_T-1.gif  " USA_Lanker-2_10_T-1.gif")

KS2-SM1-ZAM_Zip-1_16_T-1-2020a

![](/png/KS2-SM1-ZAM_Zip-1_16_T-1-2020a.gif  " KS2-SM1-ZAM_Zip-1_16_T-1-2020a.gif")

## Answers to Infrequently asked questions (IAQ):

- For ideas, please feel free to contact me or create an issue. (contact details on my [website](https://michaelfeil.github.io) )
- Obviously no weights are tuned in this blueprint 
- no szenarios types are distinguished. 
(e.g. in a scenario without goal, a reference path that shows a way to the goal is not as helpful as with goal)
- if makes sense to use a different (or even multiple sequentially) motion primitive sets. I have uploaded some under [./motion_primitives](https://github.com/michaelfeil/commonroad_motionplaner_michaelf/tree/main/motion_primitives)
