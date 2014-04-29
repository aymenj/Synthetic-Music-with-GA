import random

#A generator that yields a list of genomes ordered by fitness (descending). Each yielded list represents a generation in the execution of the genetic
#algorithm.

#@param population: the starting population of genomes.
#@param fitness: a function which given a genome will return a fitness score.
#@param generate: an function that produces offspring genomes for the next generation.
#@param halt: a function to test if the genetic algorithm should stop.

#Applies the fitness function to each genome in a generation, uses the generate function create the next generation from the existing one.

#If the halt function returns True for a generation then the algorithm stops.

def genetic_algorithm(population, fitness, generate, halt):
    current_population = sorted(population, key=fitness, reverse=True)
    generation_count = 1
    yield current_population
    while not halt(current_population, generation_count):
        generation_count += 1
        new_generation = generate(current_population)
        current_population = sorted(new_generation, key=fitness, reverse=True)
        yield current_population


# A random number between 0 and the total fitness score of all the genomes in a population is chosen (a point with a slice of a roulette 
# wheel). The code iterates through the genomes adding up the fitness scores. When the subtotal is greater than the randomly chosen point 
# it returns the genome at that point "on the wheel".

# https://en.wikipedia.org/wiki/Fitness_proportionate_selection

def roulette_wheel(population):
    fitness = 0.0
    for genome in population:
        fitness += genome.fitness

    if fitness == 0.0:
        return random.choice(population) # Random selection if no solutions are fit

    random_pt = random.uniform(0.0, fitness)
    fitness_tally = 0.0
    
    for genome in population:
        fitness_tally += genome.fitness
        if fitness_tally > random_pt:
            return genome

# Randomly select a midpoint and then swap the ends of each genome's chromosome to create two new genomes
def crossover(mother, father, klass):
    if mother == father:
        return (mother, father) # do nothing if the parents are the same
    else:
        crossover_pt = random.randint(0, len(mother))
        return (klass(mother[:crossover_pt] + father[crossover_pt:]), klass(mother[:crossover_pt] + father[crossover_pt:]))

# A base class that all Genome's must use. Genomes represent candidate solutions in the genetic algorithm.
class Genome(object):
    # The chromosome is a list of genes that encode specific characteristics of the candidate solution (genome). The different settings that a gene
    # may possess are called alleles, and their location in the chromosome is called the locus. The state of the alleles in a particular chromosome
    # is called the genotype. It is the genotype that provides information about the state of the actual candidate solution. The candidate
    # solution itself is called a genome (hence the name of this class).
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = None # set by the fitness function.

    # New offspring bred from this and another instance
    def breed(self, other):
        return crossover(self, other, self.__class__)

    
    # Mutates the genotypes no more than the mutation_range depending on the mutation_rate given a certain context (to ensure 
    # the mutation is valid). To be overridden as per requirements in the child classes.
    def mutate(self, mutation_range, mutation_rate, context):
        return NotImplemented

    # Genomes with the same genotype are equal
    def __eq__(self, other):
        return self.chromosome == other.chromosome

    # Chromosome length
    def __len__(self):
        return len(self.chromosome)

    # Slicing
    def __getitem__(self, key):
        return self.chromosome.__getitem__(key)

    # Chromosome's repr
    def __repr__(self):
        return self.chromosome.__repr__()
