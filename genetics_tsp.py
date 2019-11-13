import random

import math
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from tkinter import scrolledtext
from tkinter import *
from tkinter import messagebox

class tsp_genetics():

    def __init__(self, population=500, routes=10, crossover=1, type_route=0, selection=2, probability=.8):

        self.population = [random.sample(range(routes),routes) for _ in range(population)]
        self.number_routes = routes
        self.population_size = population
        self.probability = probability
        self.best_generation = []
        self.radio_random = False
        if type_route == 0:
            self.generate_square_points(self.number_routes)
        elif type_route == 1:
            self.generate_circle_points(self.number_routes)
        else:
            self.generate_circle_points(self.number_routes)
            self.radio_random = True
        
        self.selection = [self.rank_selection,self.roulette_wheel_selection, self.tournament_selection][selection]
        self.crossover = [self.order_crossover_operator, self.partially_mapped_crossover][crossover]

        
        

    def  create_new_generations(self,number_generations):
        
        self.first_last = []
        self.best = (float('inf'), 0)
        for gen in range(number_generations):

            self.aptitudes_population()
            best_of_gen =  np.argmin(self.aptitudes)
            if gen == 0 or gen == number_generations - 1:
                self.first_last.append((self.aptitudes[best_of_gen] ,self.population[best_of_gen]))
            
            self.best_generation.append(self.aptitudes[best_of_gen])

            if self.aptitudes[best_of_gen] < self.best[0]:
                self.best = (self.aptitudes[best_of_gen], self.population[best_of_gen])

            print(f"Best of the generation {gen} with {self.aptitudes[best_of_gen]} of aptitude")
            
            
            new_population = []

            for _ in range(self.population_size // 2):

                specie_1 = self.selection()
                specie_2 = self.selection()

                specie_1, specie_2 = self.crossover(specie_1, specie_2)

                new_population.append(specie_1)
                new_population.append(specie_2)
            
            self.mutation(new_population)

            self.population = new_population


    def mutation(self, new_population):


        for i in range(self.population_size):

            prob = random.random()

            if prob > self.probability:
                a = random.randint(0,self.number_routes-1)
                b = random.randint(0,self.number_routes-1)

                new_population[i][b],new_population[i][a] = new_population[i][a],new_population[i][b]
            

    def plot_results(self):

        x, y = np.random.random(size=(2,10))
        fig, axes = plt.subplots(2,2)
        axes[1][1].title.set_text('Aptitudes rating')

        for i in range(len(self.best_generation)):
            axes[1][1].plot([i for i in range(1,len(self.best_generation)+1)], self.best_generation, 'go-')
        

        axes[0][1].title.set_text('Best route of all generations aptitude: '+str(self.best[0]))
        route = self.best[1]
        
        for i in range((self.number_routes)):
            
            x1,y1 = self.points[ route[i] ]
            x2,y2 = self.points[ route[(i+1) % self.number_routes] ]

            axes[0][1].plot((x1,x2), (y1,y2), 'bo-',linestyle='-')


        axes[1][0].title.set_text('The best of the first generation')
        route = self.first_last[0][1]
        for i in range((self.number_routes)):
            
            x1,y1 = self.points[ route[i] ]
            x2,y2 = self.points[ route[(i+1) % self.number_routes] ]

            axes[1][0].plot((x1,x2), (y1,y2), 'yo',linestyle='-')

        
        axes[0][0].title.set_text('The best of the last generation')
        route = self.first_last[1][1]
        for i in range((self.number_routes)):
            
            x1,y1 = self.points[ route[i] ]
            x2,y2 = self.points[ route[(i+1) % self.number_routes] ]

            axes[0][0].plot((x1,x2), (y1,y2), 'ro',linestyle='-')


        plt.show()

    def aptitudes_population(self):

        self.aptitudes = []

        for route in self.population:

            aptitude = 0 
            for i in range(self.number_routes):
                node_a = route[i]
                node_b = route[ (i + 1) % self.number_routes ]
                x_x = (self.points[ node_a ][0] - self.points[ node_b ][0])**2
                y_y = (self.points[ node_a ][1] - self.points[ node_b ][1])**2
                aptitude += math.sqrt(x_x + y_y)
            
            self.aptitudes.append(aptitude)


        
    def roulette_wheel_selection(self):
        
        fitness = sum(self.aptitudes)
        
        roulete = random.uniform(0,fitness)
        pointer = 0
        
        for index,aptitude in enumerate(self.aptitudes):
            
            pointer += aptitude
            
            if roulete <= pointer:
                return index
            
        
    def tournament_selection(self):

        cut_point_a = random.randint(0, self.population_size//3)
        cut_point_b = random.randint(cut_point_a + 5, self.population_size)

        return np.argmin(self.aptitudes[cut_point_a : cut_point_b])

           
        
    def rank_selection(self):

        fitness = sum(self.aptitudes)
        
        roulete = random.uniform(0,fitness)
        pointer = 0
        
        for index,_ in enumerate(self.aptitudes):
            
            pointer += random.uniform(0,fitness//2)
            
            if roulete <= pointer:
                return index
        
        

    def partially_mapped_crossover(self,species_1, species_2):

        slices_size = self.number_routes // 3
        cut_point_a = random.randint(slices_size, slices_size + 3)
        cut_point_b = cut_point_a * 2
        
        specie_1_ref = self.population[species_1].copy()
        specie_2_ref = self.population[species_2].copy()

        temp = specie_1_ref[cut_point_a: cut_point_b]
        specie_1_ref[cut_point_a: cut_point_b] = specie_2_ref[cut_point_a: cut_point_b] 
        specie_2_ref[cut_point_a: cut_point_b] = temp
    
        self.fix_repeated_number(specie_1_ref, cut_point_a, cut_point_b)
        self.fix_repeated_number(specie_2_ref, cut_point_a, cut_point_b)

        return specie_1_ref, specie_2_ref

    def order_crossover_operator(self,species_1, species_2):

        
        cut_point_a = self.number_routes // 3
        cut_point_b = cut_point_a * 2

        specie_1_ref = self.population[species_1]
        specie_2_ref = self.population[species_2]
        
        
        temp_specie_1 = self.concatenate_new_species(specie_1_ref, 
                            specie_2_ref,cut_point_a, cut_point_b)
        temp_specie_2 = self.concatenate_new_species(specie_2_ref, 
                            specie_1_ref,cut_point_a, cut_point_b)
        
        return temp_specie_1, temp_specie_2
        

                                                                                         
    def concatenate_new_species(self, specie_a, specie_b, cut_point_a, cut_point_b):

        check_set = set(specie_b[ cut_point_a : cut_point_b ])
        temp = []

        for node in specie_a[ :cut_point_a]:
            if node not in check_set:
                temp.append(node)        

        temp += specie_b[ cut_point_a : cut_point_b ]

        for node in specie_a[ cut_point_b: ]:
            if node not in check_set:
                temp.append(node)

        check_set = set(temp)

        for i in range(self.number_routes):
            if i not in check_set:
                temp.append(i)

        return temp 

        
    def fix_repeated_number(self, specie_1_ref, cut_point_a, cut_point_b):
        
        set_ = set()
        values = []

        for index, node in enumerate(specie_1_ref):
            if node in set_:
                values.append(index)
            else:
                set_.add(node)


        for index in values:

            for i in range(self.number_routes):

                if i not in set_:
                    set_.add(i)
                    specie_1_ref[index] = i
                    break
     
                
    
    def generate_circle_points(self, number_points, radio_size=50):
        
        # radius of the circle
        circle_r = radio_size
        # center of the circle (x, y)
        circle_x = radio_size + 10
        circle_y = radio_size + 10

        self.points = []
        r = circle_r * math.sqrt(random.random())
        # calculating coordinates
        for _ in range(number_points):
            alpha = 2 * math.pi * random.random()
            # random radius
            if self.radio_random:
                r = circle_r * math.sqrt(random.random())

            
            x = r * math.cos(alpha) + circle_x
            y = r * math.sin(alpha) + circle_y
            
                
            self.points.append((x,y))
        
        


    def generate_square_points(self, number_points, square_size=500):
        
        vertices = [(0,0),(0,square_size),(square_size,square_size),(square_size,0)]
        self.points = []
        for _ in range(number_points):
            
            vertex_a = random.randint(0,3)
            vertex_b = (vertex_a + 1) % 4
                
            
            if vertices[vertex_a][0] == vertices[vertex_b][0]:
                
                new_point = (vertices[vertex_a][0], random.random()*square_size)
            else:
                new_point = (random.random()*square_size, vertices[vertex_a][1])
            self.points.append(new_point)
        


def clicked():
        
    
    #print(selection.get(), crossover.get(), route_option.get(), population.get(), route.get(), probability.get())
    
    object = tsp_genetics(  population=population.get(),
                            routes=route.get(),
                            crossover=crossover.get(),
                            type_route=route_option.get(),
                            selection=selection.get(),
                            probability=probability.get())

    object.create_new_generations(generations.get())
    object.plot_results()



if __name__ == "__main__":

    

    window = Tk()
    
    window.title("Welcome to LikeGeeks app")
    
    window.geometry('800x200')
    
    
    selection = IntVar()
    Label(window, text="Selection").grid(column=0, row=0)
    Radiobutton(window,text='Rank selection', value=0, variable=selection).grid(column=8, row=0)
    Radiobutton(window,text='Roulette selection', value=1, variable=selection).grid(column=16, row=0)
    Radiobutton(window,text='Tournamente selection', value=2, variable=selection).grid(column=32, row=0)
    

    crossover = IntVar()
    Label(window, text="Crossover option: ").grid(column=0, row=8)
    Radiobutton(window,text='Order crossover operator', value=0, variable=crossover).grid(column=8, row=8)
    Radiobutton(window,text='Partially mapped crossover', value=1, variable=crossover).grid(column=16, row=8)
    

    route_option = IntVar()
    Label(window, text="Route option: ").grid(column=0, row=16)
    Radiobutton(window,text='Squared', value=0, variable=route_option).grid(column=8, row=16)
    Radiobutton(window,text='Circle', value=1, variable=route_option).grid(column=16, row=16)
    Radiobutton(window,text='Circle version 2', value=2, variable=route_option).grid(column=16, row=16)
    
    population = IntVar()
    population.set(500)
    Label(window, text="Population size: ").grid(column=0, row=24)
    Entry(window,width=10,textvariable=population).grid(column=1, row=24)
    
    route = IntVar()
    route.set(50)
    Label(window, text="Number of routes: ").grid(column=0, row=32)
    Entry(window,width=10,textvariable=route).grid(column=1, row=32)

    generations = IntVar()
    generations.set(10)
    Label(window, text="Number of generations: ").grid(column=0, row=40)
    Entry(window,width=10,textvariable=generations).grid(column=1, row=40)
    
    probability = DoubleVar()
    probability.set(.8)
    Label(window, text="Probability: ").grid(column=0, row=48)
    Spinbox(window, values=[ i/10 for i in range(1,10)], width=5,textvariable=probability).grid(column=1,row=48)
 
    btn = Button(window, text="Start", command=clicked)
   
    btn.grid(column=0, row=80)
    
    window.mainloop()

    

