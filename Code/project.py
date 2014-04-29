#!/usr/bin/env python
"""
A simple command line wrapper around the genetic algorithm used for finding
valid solutions to species counterpoint problems.
"""

import argparse
import logging

import gen_alg

import lilypond
import melody

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Evolves valid solutions to species counterpoint problems.')

parser.add_argument('-cf', '--cantus-firmus', help='specify the cantus firmus', nargs='*', required=True)


if __name__ == '__main__':
    args = parser.parse_args()
    cf = [int(x) for x in args.cantus_firmus]

    population_size = 1000
    mutation_range = 9 # or 7!
    mutation_rate = 0.4
    
    start_population = melody.create_population(population_size, cf)

    evaluator = melody.make_evaluator(cf)
    generator = melody.make_generator(mutation_range, mutation_rate, cf)
    halter = melody.make_halter(cf)

    ga = gen_alg.genetic_algorithm(start_population, evaluator, generator, halter)
    
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
    plt.ylabel('Generation')
    plt.xlabel('Fitness Score')
    plt.savefig('output/fitness_test.png')
    
    with open('output/test.ly', 'w') as output:
        output.write(lilypond.render(cf, generation[0].chromosome))
