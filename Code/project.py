import logging
import lilypond
from melody import *

import matplotlib.pyplot as plt

if __name__ == '__main__':
    # cantus_firmus
    cf = [5, 7, 6, 5, 8, 7, 9, 8, 7, 6, 5]

    population_size = 1000
    
    start_population = create_population(population_size)

    ga = genetic_algorithm(start_population, fitness_function, spawn_function, halt_function)
    
    fitness = 0.0
    fitnesses = []

    counter = 0
    for generation in ga:
        counter += 1
        fitness = generation[0].fitness
        fitnesses.append(fitness)
        print "--- Generation %d ---" % counter
        print generation[0].notes
        print fitness

    plt.plot(fitnesses)
    plt.ylabel('Generation')
    plt.xlabel('Fitness Score')
    plt.savefig('output/fitness_test.png')
    
    with open('output/test.ly', 'w') as output:
        output.write(lilypond.render(cf, generation[0].notes))
