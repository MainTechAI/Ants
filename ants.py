# =============================================================================
# A traveling salesman needs to visit each city within a certain territory and 
# return to the point of departure. It is required that the path be as short 
# as possible. 
#
# Thus, the original problem is transformed into a minimum-length search problem.
# 
# A Hamiltonian cycle is a cycle (a closed path) that passes through each vertex
# of a given graph exactly once.
# =============================================================================
import numpy as np
import random
from random import randrange
from numpy.random import choice

random.seed(7)

# ------------/Parameters/-------------

random_distance_matrix = True
V = 20  # number of edges in complete graph
b = 0  # chance of leaving the main path with the highest number of pheromones

number_of_ants = 100

# if the value is false, then ants will appear in a random place
one_start_location = False

pheromone_min = 12.5
pheromone_max = 100.0
pheromone_const = 0.8  # the constant value of the pheromone secreted by each ant
vanishing_const = 1.1  # (1,10]~

# This value determines whether the pheromone is released in one 
# direction of movement or in both directions
symmetrically = False

# This value determines whether an increase in the amount of pheromone 
# on the best path is allowed
elitist = True

# the constant value of the pheromone secreted by the elite ant
elitist_const = 0.9

# -----/Distance matrix Initialization/------

if random_distance_matrix:  # Initialize the distance matrix with random numbers from 1 to 50
    mylist = []
    for i in range(0, int((V * (V - 1)) / 2)):
        q = random.randint(1, 50)
        mylist.append(q)
    distance_matrix = np.zeros([V, V])
    distance_matrix[np.triu_indices(V, 1)] = mylist
    distance_matrix += distance_matrix.T
else:
    string = input()
    distance_matrix = np.fromstring(string, dtype=int, sep=' ')
    import math

    V = int(math.sqrt(len(distance_matrix)))
    distance_matrix = distance_matrix.reshape((V, V))

# An example
# 0 2 30 9 1 4 0 47 7 7 31 33 0 33 36 20 13 16 0 28 9 36 22 22 0

# initialization of the pheromone matrix with random positive numbers
mylist = np.random.uniform(low=2.8, high=3.1, size=(int((V * (V - 1)) / 2),))
pheromone_matrix = np.zeros([V, V])
pheromone_matrix[np.triu_indices(V, 1)] = mylist
pheromone_matrix += pheromone_matrix.T

shortest_distance = float("inf")
shortest_path = []


class Ant:
    def __init__(self):

        if one_start_location is False:
            self.start_location = randrange(V)
        else:
            self.start_location = 0

        self.current_location = 0
        self.location_history = [self.start_location, ]
        self.distance = 0
        self.posssible_paths = []
        self.end = False
        self.attraction = []
        for s in range(0, V):
            self.attraction.append(0.0)

    def update_pheromone(self, next_path):
        pheromone_matrix[self.current_location][next_path] += distance_matrix[self.current_location][
                                                                  next_path] * pheromone_const
        if pheromone_matrix[self.current_location][next_path] > pheromone_max:
            pheromone_matrix[self.current_location][next_path] = pheromone_max
        if symmetrically is True:
            pheromone_matrix[next_path][self.current_location] += distance_matrix[self.current_location][
                                                                      next_path] * pheromone_const
            if pheromone_matrix[next_path][self.current_location] > pheromone_max:
                pheromone_matrix[next_path][self.current_location] = pheromone_max

    def find_possible_paths(self):
        # Here we choose places where an ant hasn't been yet
        self.posssible_paths = []
        for x in range(0, V):
            if x not in self.location_history and x != self.current_location:
                self.posssible_paths.append(x)

        if len(self.posssible_paths) != 0:
            return True

    def make_decision(self):
        self.find_possible_paths()
        highest_phero_path = 0
        highest_value = 0
        for path in self.posssible_paths:
            pheromone = pheromone_matrix[self.current_location][path]
            self.attraction[path] = pheromone
            if pheromone >= highest_value:
                highest_phero_path = path
                highest_value = pheromone

        self.attraction[highest_phero_path] = 0.0
        p = np.array(self.attraction)
        p /= p.sum()

        rand = randrange(100)

        if rand > b or len(self.posssible_paths) == 1:
            chosen_path = highest_phero_path
        else:
            self.attraction[highest_phero_path] = 0.0
            chosen_path = choice(range(0, V), 1, p=p)  # ,replace=False
            chosen_path = chosen_path[0]

        self.update_pheromone(chosen_path)
        self.location_history.append(chosen_path)
        self.distance += distance_matrix[self.current_location][chosen_path]
        self.current_location = chosen_path

        for idx in range(0, V):
            self.attraction[idx] = 0.0

    def end_expl(self):
        self.end = True
        global shortest_distance
        global shortest_path
        if self.distance < shortest_distance:
            shortest_distance = self.distance
            shortest_path = self.location_history

    def lets_go(self):
        if (self.find_possible_paths() is True) and (self.distance < shortest_distance):
            self.make_decision()
        else:
            self.end_expl()


class Place:
    def __init__(self):
        self.ants_colony = []
        for count in range(number_of_ants):
            x = Ant()
            self.ants_colony.append(x)

    @staticmethod
    def elitist_ant():
        for x in range(0, len(shortest_path) - 1):  # asymmetrical
            path = shortest_path[x]
            next_path = shortest_path[x + 1]
            if pheromone_matrix[path][next_path] < pheromone_max:
                pheromone_matrix[path][next_path] += distance_matrix[path][next_path] * elitist_const

    def in_process(self):
        # If there is at least one working ant, then in theory this can be removed, 
        # since each ant cannot pass more than V nodes
        for ant in self.ants_colony:
            if ant.end is False:
                return True
        return False

    @staticmethod
    def pheromone_vanishing():
        for x in range(0, V):
            for y in range(0, V):
                if pheromone_matrix[x][y] > pheromone_min:
                    pheromone_matrix[x][y] = (pheromone_matrix[x][y] / distance_matrix[x][y]) / vanishing_const

    def start_exploration(self, epoch=1):
        for x in range(0, epoch):
            while self.in_process() is True:
                for ant in self.ants_colony:
                    if ant.end is False:
                        ant.lets_go()
                self.pheromone_vanishing()

            for ant in self.ants_colony:  # resetting ant's parameters
                ant.__init__()

            if elitist is True:
                self.elitist_ant()

            print(x + 1, 'epoch ended, best result:', shortest_distance, 'shortest path', shortest_path)


def main():
    print('Start')
    x = Place()
    n_epoch = 600
    x.start_exploration(n_epoch)
    print('Exploration completed, best result:', shortest_distance)


if __name__ == '__main__':
    main()
