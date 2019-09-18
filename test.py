# -*- coding: utf-8 -*-
import numpy as np
import random
from random import randrange
from numpy.random import choice


# =============================================================================
# Коммивояжёру необходимо посетить каждый город в пределах некоторой территории 
# и возвратиться в пункт отправления. 
# Требуется, чтобы путь был как можно короче. Таким образом, исходная задача преобразуется 
# в задачу поиска минимальной протяженности
# 
# Гамильтоновым циклом является такой цикл (замкнутый путь), 
# который проходит через каждую вершину данного графа ровно по одному разу
# Будем считать что начальная точка для всех муравьёв одинаковая
# start - 0
# =============================================================================

V=15             #количество вершин в графе
#a=0.5 #нужно?
b=70 #  % шанс на отклонение от дороги с самым большим числом феромонов
number_of_ants=100
pheromone_const=0.1 #константное значение выделяемого феромона для каждого муравья
vanishing_const=0.7
symmetrically=True
pheromone_min=2.5

#инициализация матрицы растояний рандомными числами от 1 до 50
mylist = []
for i in range(0,int((V*(V-1))/2)):
    q = random.randint(1,50)
    mylist.append(q)      
distance_matrix = np.zeros([V, V])
distance_matrix[np.triu_indices(V, 1)] = mylist
distance_matrix += distance_matrix.T
#print(distance_matrix)

#инициализация матрицы ферамонов рандомными положительными числами
mylist = np.random.uniform(low=2.8, high=3.1, size=(int((V*(V-1))/2),))
pheromone_matrix = np.zeros([V, V])
pheromone_matrix[np.triu_indices(V, 1)] = mylist
pheromone_matrix += pheromone_matrix.T
#print(pheromone_matrix)

shortest_distance=9999999999#не так, переделать
shortest_path=[]




class Place():
    class Ant:
        def __init__(self):
            self.start_location=0
            self.current_location=0
            self.location_history=[self.start_location,]
            self.distance=0
            self.posssible_paths=[]
            self.end=False
            self.attraction=[]
            for s in range (0,V):
                self.attraction.append(0.0)
            
            
        def update_pheromone(self, next_path):
            #матрица феромона=конст_феромон*длину_пути
            pheromone_matrix[self.current_location][next_path]+=distance_matrix[self.current_location][next_path]*pheromone_const
            if(symmetrically==True):
                pheromone_matrix[next_path][self.current_location]+=distance_matrix[self.current_location][next_path]*pheromone_const
    
    
        def find_possible_paths(self):
            #выбираются места где муровей ещё не был
            self.posssible_paths=[]
            for x in range(0, V):
                if(x not in self.location_history and x!=self.current_location):
                    self.posssible_paths.append(x)

            if(len(self.posssible_paths)!=0):
                return True
            
            
        def make_decision(self):
            self.find_possible_paths()
            total=0.0
            highest_phero_path=0
            highest_value=0
            pheromone=0.0
#            print('self.posssible_paths',self.posssible_paths)
            for path in self.posssible_paths:
#                print(self.current_location,'self.current_location')
#                print(path,'path')
                pheromone=pheromone_matrix[self.current_location][path]
                self.attraction[path]=pheromone#pow(pheromone, a)#*(1/b)
                if(pheromone>=highest_value):
                    highest_phero_path=path
                    highest_value=pheromone
                total+=self.attraction[path]
#                print('attraction',self.attraction[path])
              
            total-=highest_value
            self.attraction[highest_phero_path]=0.0
            for path in self.posssible_paths:
                self.attraction[path] /= total 
#                print(self.attraction[path])
            
            rand=randrange(100)

            if(rand>b or len(self.posssible_paths)==1):
                chosen_path=highest_phero_path
            else:
                self.attraction[highest_phero_path]=0.0
                chosen_path = choice(range(0,V), 1,p=self.attraction,replace=False)
#                print(chosen_path)
                chosen_path=chosen_path[0] 
                       
#            print(chosen_path)
            
            self.update_pheromone(chosen_path)
            self.location_history.append(chosen_path)
            self.distance+=distance_matrix[self.current_location][chosen_path]
            self.current_location=chosen_path
#            print('self.distance',self.distance)

            for q in range (0,V):#!!!
                self.attraction[q]=0.0
            
        
        def end_expl(self):
            self.end=True
            global shortest_distance
            global shortest_path
            if(self.distance < shortest_distance):
                shortest_distance=self.distance
                shortest_path=self.location_history
#            print('end self.distance',self.distance)
        
        
        def lets_go(self):
            if(self.find_possible_paths()==True and self.distance<shortest_distance):
                self.make_decision()          
            else:
                self.end_expl()
                
                
                
            
    
    
    
    def __init__(self):
        self.ants_colony=[]
        
        for count in range(number_of_ants):
            x = self.Ant()
            self.ants_colony.append(x)
           
            
    def in_process(self): #Есть ли хотя бы один работающий муравей, можно убрать в теории так как каждый муровей не может проти больше чем V узлов
        for ant in self.ants_colony:
            if ant.end==False:
                return True
        return False
        
    
    def pheromone_vanishing(self):
        for x in range(0,V):
            for y in range(0,V):
                if(pheromone_matrix[x][y]>pheromone_min):
                    pheromone_matrix[x][y]=pheromone_matrix[x][y]/(vanishing_const*distance_matrix[x][y])
    
    
    def start_exploration(self, epoch=1):
        for x in range(0, epoch):
            while( self.in_process()==True ):
                for ant in self.ants_colony:
                    if ant.end==False:
                        ant.lets_go()   
                self.pheromone_vanishing()
                        
            for ant in self.ants_colony:#обнуление параметров муравья
                ant.__init__()
            print( x+1 ,'epoch ended, best result:', shortest_distance, 'shortest path',shortest_path)
            
                        
            
            
            
            
            
    
        

def main():
    print('Start')
    x=Place()    
    x.start_exploration(50)
    print('Exploration completed, best result:', shortest_distance)
    
    
    
if __name__ == '__main__':
    main()
    
    
    