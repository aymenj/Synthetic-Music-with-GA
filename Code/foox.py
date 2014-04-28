#!/usr/bin/env python
"""
A simple command line wrapper around the genetic algorithm used for finding
valid solutions to species counterpoint problems.
"""

import argparse
import logging

import ga

import lilypond
import melody

import matplotlib.pyplot as plt


# MAJOR, MINOR, RELEASE, STATUS [alpha, beta, final], VERSION
VERSION = (0, 0, 0, 'alpha', 0)


def get_version():
    """
    Returns a string version of VERSION
    """
    return '.'.join([str(i) for i in VERSION])


parser = argparse.ArgumentParser(description='Evolves valid solutions to species counterpoint problems.')

parser.add_argument('--version', action='version', version=get_version())

parser.add_argument('-v', '--verbose', help='increased amount of verbosity', action='store_true')

parser.add_argument('-cf', '--cantus-firmus', help='specify the cantus firmus', nargs='*', required=True)

parser.add_argument('-o', '--out', help='name the output file')


if __name__ == '__main__':
    args = parser.parse_args()
    cf = [int(x) for x in args.cantus_firmus]
    #species = args.species
    output = 'out'
    if args.out:
        output = args.out

    population_size = 1000
    mutation_range = 7
    mutation_rate = 0.4

    population_size = melody.DEFAULT_POPULATION_SIZE
    mutation_range = melody.DEFAULT_MUTATION_RANGE
    mutation_rate = melody.DEFAULT_MUTATION_RATE
    start_population = melody.create_population(population_size, cf)
    fitness_function = melody.make_fitness_function(cf)
    generate_function = melody.make_generate_function(mutation_range, mutation_rate, cf)
    halt_function = melody.make_halt_function(cf)

    ga = ga.genetic_algorithm(start_population, fitness_function, generate_function, halt_function)
    
    fitness = 0.0
    fitnesses = []

    counter = 0
    for generation in ga:
        counter += 1
        fitness = generation[0].fitness
        fitnesses.append(fitness)
        print "--- Generation %d ---" % counter
        print generation[0]
        print fitness

    plt.plot(fitnesses)
    plt.show()
    
    with open('%s.ly' % output, 'w') as output:
        output.write(lilypond.render(4, cf, generation[0].chromosome))
