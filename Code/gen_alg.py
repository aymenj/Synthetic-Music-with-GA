import random

# Some defaults.
cantus_firmus = [5, 7, 6, 5, 8, 7, 9, 8, 7, 6, 5]

VALID_INTERVALS = [2, 4, 5, 7, 9, 11] # Intervals between notes that are allowed (fourth sepcies counterpoint)

CONSONANCES, DISSONANCES = [2, 4, 5, 7, 9, 11], [3, 6, 8, 10] # Intervals between notes that are allowed (third species counterpoint)

VALID_ODD_BEAT_INTERVALS, VALID_EVEN_BEAT_INTERVALS = CONSONANCES, CONSONANCES + DISSONANCES

VALID_FIRST_BEAT_INTERVALS, VALID_THIRD_BEAT_INTERVALS = CONSONANCES, CONSONANCES + DISSONANCES





def genetic_algorithm(population, fitness, generate, halt):
    current_population = sorted(population, key=fitness, reverse=True)
    generation_count = 1
    yield current_population
    while not halt(current_population, generation_count):
        generation_count += 1
        new_generation = generate(current_population)
        current_population = sorted(new_generation, key=fitness, reverse=True)
        yield current_population


# A random number between 0 and the total fitness score of all the melodies in a population is chosen (a point with a slice of a roulette 
# wheel). Iterates through the melodies adding up the fitness scores. When the subtotal is greater than the randomly chosen point 
# it returns the melody at that point "on the wheel".

# https://en.wikipedia.org/wiki/Fitness_proportionate_selection

def roulette_wheel(population):
    fitness = 0.0
    for melody in population:
        fitness += melody.fitness

    if fitness == 0.0:
        return random.choice(population) # Random selection if no solutions are fit

    random_pt = random.uniform(0.0, fitness)
    fitness_tally = 0.0
    
    for melody in population:
        fitness_tally += melody.fitness
        if fitness_tally > random_pt:
            return melody

# Randomly select a midpoint and then swap the ends of each melody's notes to create two new melodies
def crossover(mother, father):
    if mother.notes == father.notes:
        return (mother, father) # do nothing if the parents are the same
    else:
        crossover_pt = random.randint(0, len(mother.notes))
        return (Melody(mother.notes[:crossover_pt] + father.notes[crossover_pt:]), Melody(mother.notes[:crossover_pt] + father.notes[crossover_pt:]))


# Mutates the genotypes
def mutate(gen, mutation_range, mutation_rate):        
    # SECOND SPECIES
    first_beat_mutation_intervals = [interval for interval in VALID_FIRST_BEAT_INTERVALS if interval <= mutation_range]
    third_beat_mutation_intervals = [interval for interval in VALID_THIRD_BEAT_INTERVALS if interval <= mutation_range]

    # THIRD SPECIES
    odd_beat_mutation_intervals = [interval for interval in VALID_ODD_BEAT_INTERVALS if interval <= mutation_range]
    even_beat_mutation_intervals = [interval for interval in VALID_EVEN_BEAT_INTERVALS if interval <= mutation_range]
    notes_length = len(gen.notes)

    # FOURTH SPECIES
    FOURTH_mutation_intervals = [interval for interval in VALID_INTERVALS if interval <= mutation_range]

    for locus in range(len(gen.notes)):
        if mutation_rate >= random.random():

            # SPECIES TWO
            cantus_firmus_note = cantus_firmus[locus / 2]
            if locus % 2:
                # Current melody note is on the third beat of the bar
                SECOND_mutation_intervals = third_beat_mutation_intervals
            else:
                # Current melody note is on the first beat of the bar.
                SECOND_mutation_intervals = first_beat_mutation_intervals

            SECOND_mutation_range = [interval for interval in SECOND_mutation_intervals if (interval + cantus_firmus_note) < 17]


            # SPECIES THREE
            cantus_firmus_note = cantus_firmus[locus / 4]
            # The pitch of the notes immediately before and after the current note (used to avoid mutations that result in a
            # repeated pitch).
            pitches_to_avoid = []
            if locus > 0:
                pre_pitch = gen.notes[locus - 1]
                pitches_to_avoid.append(pre_pitch)
            if locus < notes_length - 2:
                post_pitch = gen.notes[locus + 1]
                pitches_to_avoid.append(post_pitch)
            if locus % 2:
                # Current melody note is on an even beat of the bar
                THIRD_mutation_intervals = [i for i in even_beat_mutation_intervals if cantus_firmus_note + i not in pitches_to_avoid]
                if not THIRD_mutation_intervals:
                    THIRD_mutation_intervals = even_beat_mutation_intervals
            else:
                # Current melody note is on an odd beat of the bar.
                THIRD_mutation_intervals = [i for i in odd_beat_mutation_intervals if cantus_firmus_note + i not in pitches_to_avoid]
                if not THIRD_mutation_intervals:
                    THIRD_mutation_intervals = odd_beat_mutation_intervals

            THIRD_mutation_range = [interval for interval in THIRD_mutation_intervals if (interval + cantus_firmus_note) < 17]


            # SPECIES ONE AND FOUR
            cantus_firmus_note = cantus_firmus[locus]
            FOURTH_mutation_range = [interval for interval in FOURTH_mutation_intervals if (interval + cantus_firmus_note) < 17]


            
            valid_mutation_range = list(set(SECOND_mutation_range) & set(THIRD_mutation_range) & set(FOURTH_mutation_range))
            
            mutation = random.choice(valid_mutation_range)
            new_allele = cantus_firmus_note + mutation
            gen.notes[locus] = new_allele

            return gen
            

class Melody(object):

    def __init__(self, notes):
        self.notes = notes
        self.fitness = None # set by the fitness function.