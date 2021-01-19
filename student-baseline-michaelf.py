"""
Forked from the student.py in the commonroad-search repository. https://gitlab.lrz.de/tum-cps/commonroad-search
"""

__author__ = "Michael Feil"

#libaries
from scipy import spatial
import numpy as np
import time
import math

#commonroad
from commonroad.visualization.draw_dispatch_cr import draw_object
import copy

#local search libaries
from SMP.motion_planner.node import PriorityNode

from SMP.motion_planner.plot_config import DefaultPlotConfig
from SMP.motion_planner.search_algorithms.best_first_search import GreedyBestFirstSearch
from SMP.motion_planner.utility import MotionPrimitiveStatus, initial_visualization, update_visualization

from SMP.motion_planner.queue import PriorityQueue


#local libaries for search

from SMP.route_planner.route_planner.route_planner import RoutePlanner

#[Start StudentMotionPlanner]
class StudentMotionPlanner(GreedyBestFirstSearch):
    """
    Motion planner implementation by students.
    Note that you may inherit from any given motion planner as you wish, or come up with your own planner.
    Here as an example, the planner is inherited from the GreedyBestFirstSearch planner.
    """

    def __init__(self, scenario, planningProblem, automata, plot_config=DefaultPlotConfig):
        super().__init__(scenario=scenario, planningProblem=planningProblem, automaton=automata,
                         plot_config=plot_config)
        self.frontier = PriorityQueue()
        self.verbose = 2
        #everything that needs to be run once
        self.id = scenario.benchmark_id

        if self.verbose > 1:
            print("welcome to commonroad. today we want to delivery pizza in ", self.id)
        self._init_goal_lanelet()

        self.optimal_route = optimal_route_planned(scenario, planningProblem, 
                                                       self.time_desired, self.distance_initial, self.state_initial.position, self.position_desired, verbose = self.verbose)

    def evaluation_function(self, node_current: PriorityNode) -> float:
        # copied the implementation in GreedyBestFirstSearch
        node_current.priority = self.heuristic_function(node_current=node_current)
        return node_current.priority

    def heuristic_function(self, node_current: PriorityNode) -> float:
        ########################################################################
        # todo: Improve your own heuristic cost calculation here.            #
        # Hint:                                                                #
        #   Use the State of the current node and the information from the     #
        #   planning problem, as well as from the scenario.                    #
        #   Some helper functions for your convenience can be found in         #
        #   ./search_algorithms/base_class.py                             #
        ########################################################################
        
        path_last = node_current.list_paths[-1]
        curr_position = path_last[-1].position
        curr_time_step = path_last[-1].time_step
        curr_orientation = path_last[-1].orientation
        curr_lanelet_ids = self.scenario.lanelet_network.find_lanelet_by_position([curr_position])[0]
        curr_velocity = path_last[-1].velocity

        if curr_time_step > self.time_desired.end+5: #+5 so that if desired end = 101, an expansion of 100->105 step works. not sure if correct and what best avlue is
                return np.inf #goal can not be fullfilled anymore

        #scores
        goal_distance = self.distance_to_goal(curr_position, node_current)

        distance_optimal_route, orientation_difference = self.optimal_route.find_closest_distance(curr_position, curr_orientation)
        distance_score = self.optimal_route.distance_score(distance_optimal_route)
        orientation_score = self.optimal_route.orientation_score(orientation_difference)


        time_difference_optimum, v_optimum = self.optimal_route.check_with_progress_on_route(curr_position, curr_time_step, curr_velocity)

        #return, weights are just demo
        return_value = 0.2*goal_distance + \
                        1*distance_score +\
                        1*orientation_score +\
                        1*time_difference_optimum +\
                        1*(self.time_desired.start-curr_time_step)+\
                        1*abs(v_optimum-curr_velocity)

        return return_value



    def _init_goal_lanelet(self):
        """
        if not explicit goal (polygon, goal area)  given, use distance to closest goal lanelet, if possible


        """

        self.position_desired_is_lanelet = False
        self.position_desired_is_none = False
        
        if self.position_desired is None: #if no explicit desired position / goal rectangle etc. is given
            
            self.position_desired_is_none = True
            if self.list_ids_lanelets_goal: #if there are some lanlets set as goal
                self.goal_lanelet_objs = []
                for goal_lane_id in self.list_ids_lanelets_goal: #for all permissoble goal lanelets
                    #print("goal is lanelet with ID", goal_lane_id)
                    self.goal_lanelet_objs.append(self.scenario.lanelet_network.find_lanelet_by_id(goal_lane_id)) #get object and goal ventrices of goal lane by id
                    self.position_desired_is_lanelet = True #a goal lane is used
            
            if self.position_desired_is_lanelet == False:
                pass 
                #goal is neither lanelet nor polygon -> survival scenario

        else:
            pass #using distance to goal polygon

    def distance_to_goal(self, curr_position, node_current, default = 7.001):
        """
        current position: array [x, y]
        node_current: node_current object in search

        returns: float
            if goal position is lane:  euclidian distance to goal lane in meter
                
            elif goal position is explicitly given: euclidian distance to 

            else: float default distance e.g. 7.001 [meter]
        """

        if self.position_desired_is_lanelet:
            closest_distances = np.array(100000)
        
            for goal_lane_obj in self.goal_lanelet_objs:
                projection_on_lanelet, a, b = self.find_nearest_point_on_lanelet(goal_lane_obj,curr_position) #get position to closest goal ventrices
                closest_distances = np.vstack((closest_distances, self.euclidean_distance(projection_on_lanelet, curr_position)))
                
            goal_distance = np.amin(closest_distances)

        elif not self.position_desired is None: #if pos exists
            goal_distance = self.calc_euclidean_distance(current_node=node_current)
        else:
            goal_distance = default #no goal distance
            
        return goal_distance
#[End StudentMotionPlanner]

#[Start optimal_route_planned]
class optimal_route_planned():
    """
        class used to work with the reference path

        classfuctions 
        - find closest distance to reference path, given the current position and derivation in orientation 
        - check what average speed is needed to complete trjaectory at steps_desired at current position and time_step

    """


    def __init__(self, scenario, planningProblem, steps_desired, distance_initial, position_initial, position_desired, verbose):
        """
        input:
            scenario: commonroad io object
            planningProblem: commonroad io object
            distance_initial: float
            position_initial.attributes (position_initial.start position_initial.end): int
            position_desired: None or [x,y]

        """

        try:
            route_planner = RoutePlanner(scenario, planningProblem, backend=RoutePlanner.Backend.NETWORKX)
            candidate_holder = route_planner.plan_routes()
            route = candidate_holder.retrieve_best_route_by_orientation()
            


            self.reference_path = np.asarray(route.reference_path)
            self.kd_tree_reference_path = spatial.KDTree(self.reference_path) #according to Stackoverflow, a KD tree is efficient in this scenario. not tested.
            
            
            self.distance_initial = distance_initial
            self.position_initial = position_initial
            self.position_desired = position_desired
            self.steps_desired_end = max((steps_desired.end + steps_desired.start)//2, steps_desired.end - 6)            
            self.verbose = verbose

            if self.verbose > 1:
                print("this is going to be tight, we got only", self.steps_desired_end , "seconds to deliver our warm pizza.")


            self._progress_route()


            self.initialized = True

            if self.verbose > 1:
                print("everything prepared. buckle up!")

        except Exception as e:
            print("route planning failed", e)
            self.initialized = False
        

    def find_closest_distance(self,pt_pos, pt_orient):
        """
        find closest distance to reference path and corresponing orientation compared to current point_orient
        gets called in heueristic

        input
            pt_pos: list of [float(x), float(y)]
            pt_orient: 

        returns 
            1. distance to reference path in m 
            2. orientation diff in rad
        """
        
        #if not self.initialized == True: #quickfix if something went wrong, e.g. route planer not able to find any solution
        #    return 0.001, 0.001
        
        distance, index = self.kd_tree_reference_path.query(pt_pos)
        orient_traject = self.orientation_traj(index) 
        orient_diff = np.abs(pt_orient - orient_traject) #compare orientation of reference_path to ego vehicle 
        
        return distance, orient_diff #distance in m, orientation diff in rad
    
    def orientation_traj(self, index):
        """
        find the orientation of the point reference_path["index"] towards its predecessor. (orientation of reference path trajectory at index)
        """
        if index == 0: 
            index = 1 # if closest point is first on trajecetory
        predecessor = self.reference_path[index-1]
        current = self.reference_path[index]
        return math.atan2(current[1] - predecessor[1], current[0] - predecessor[0])
    
    def orientation_score(self, orient_diff):
        """
        some scoring function to penaltize points far away from reference path

        returns np.float 
        """
        return 5*np.exp(0.5*orient_diff) 
    
    def distance_score(self, distance):
        """
        some scoring function to penaltize points far away from reference path

        returns np.float 
        """
        return 5*np.exp(0.5* distance) 
    
    def _progress_route(self, mode="default"):
        """
        init for finding a progress at each  needed to complete the route at desired_time
        gets called once

        mode:
            str "default": not considering slowdown through turns
        
        initializes:
            self.relevant_reference_path: approx. part of the reference_path needed from start to goal
            self.relevant_route_lenght: approx. lenght of the relevant_reference_path / route 
          
            
        """
        distance, index_initial = self.kd_tree_reference_path.query(self.position_initial)
        if self.position_desired is not None:
            x_center = (self.position_desired[0].start + self.position_desired[0].end)/2
            y_center = (self.position_desired[1].start + self.position_desired[1].end)/2
            distance, index_end = self.kd_tree_reference_path.query([x_center,y_center])
        else:
            index_end = len(self.reference_path)
        
        self.relevant_reference_path = self.reference_path[index_initial:index_end]
        
        self.relevant_route_lenght = 0
        for i in range(len(self.relevant_reference_path)-1):
            self.relevant_route_lenght += self.euclidean_distance_special(self.relevant_reference_path[i], self.relevant_reference_path[i+1])  
        
        self.kd_tree_relevant_reference_path = spatial.KDTree(self.relevant_reference_path )
        
        if self.verbose > 1:
            print("expected route is ", int(self.relevant_route_lenght), " meters long. ")
                
        if mode == "default":
            desired_progress = []
            self.quatisation_size = len(self.relevant_reference_path)/self.steps_desired_end

        else: #consider slowdown at turns 
            raise "other mode than default not implemented"
        
            self.orientation_change = []
            for i in self.reference_path:
                self.orientation_change.append(orientation_traj(i))
            self.orientation_change = np.asarray(self.orientation_change)

            curviness = self.distance_initial / self.relevant_route_lenght

            #TODO: slowdown the expected speed / progress in curves, raise speed expecation when driving straight
        
                          
    def check_with_progress_on_route(self, curr_position, curr_time_step, curr_velocity):
        """
        gets called in heueristic function. Has not been extensivly tested. does not make sense to apply in every scenario. 

        input
            curr_position: list of [float(x), float(y)]
            curr_time_step: int
            curr_velocity: float

        returns 
            1. difference in time_steps between 1.position_current and 2. desired quantisized progress  
            2. avg speed needed at this point to arrive at time
        """

        
        
        distance, index_current = self.kd_tree_relevant_reference_path.query(curr_position)
        
        progress = index_current/self.quatisation_size
                
        time_remaining = (self.steps_desired_end - progress)
       
        time_difference = (abs(progress-curr_time_step))
        
        
        meters_remaining = (1-(progress / self.steps_desired_end)) * self.relevant_route_lenght #portion of route remaining, in meters
        
        velocity_needed = meters_remaining*(1/time_remaining*10)
        
        #print(int(progress), distance, curr_time_step, curr_position, meters_remaining, time_remaining, velocity_needed)
        return time_difference, velocity_needed

    def euclidean_distance_special(self, pos1: np.ndarray, pos2: np.ndarray) -> float:
        """
        copied from https://gitlab.lrz.de/tum-cps/commonroad-search/-/tree/master/SMP/motion_planner/search_algorithms

        Returns the euclidean distance between 2 points.

        :param pos1: the first point
        :param pos2: the second point
        """
        return np.sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + (pos1[1] - pos2[1]) * (pos1[1] - pos2[1]))
#[End optimal_route_planned]