import random
import gen_alg

from gen_alg import *

VALID_INTERVALS = [2, 4, 5, 7, 9, 11] # Intervals between notes that are allowed (fourth sepcies counterpoint)

cantus_firmus = [5, 7, 6, 5, 8, 7, 9, 8, 7, 6, 5]

mutation_range = 9 # or 7!
mutation_rate = 0.4

# Create a new list of random candidate solutions of the specified number given the context of the cantus_firmus.
def create_population(number):
    
    result = []
    for i in range(number):
        new_notes = []
        for note in cantus_firmus:
            valid_range = [interval for interval in VALID_INTERVALS if (interval + note) < 17]
            interval = random.choice(valid_range)
            new_notes.append(note + interval)
        melody = Melody(new_notes)
        result.append(melody)
    return result


# Is the motion between last and current notes parallel
def is_parallel(last, current):
    if ((last[0] - current[0] < 0) and (last[1] - current[1] < 0)) or ((last[0] - current[0] > 0) and (last[1] - current[1] > 0)):
        return True
    else:
        return False


# Is the note at pos in the middle of a step-wise movement in a single direction?
def is_stepwise(melody, pos):
    if abs(melody[pos-1] - melody[pos]) == 1 and abs(melody[pos] - melody[pos+1]) == 1:
        return melody[pos-1] != melody[pos+1]
    else:
        return False


# Return a new generation of candidate solutions
def spawn_function(seed_gen):
    new_gen = seed_gen[:len(seed_gen)/2] # Keep the fittest 50%

    # Breed the remaining 50% using roulette wheel selection
    offspring = []
    while len(offspring) < len(seed_gen)/2:
        mother, father = gen_alg.roulette_wheel(seed_gen), gen_alg.roulette_wheel(seed_gen)
        
        children = crossover(mother, father)

        #children = mother.breed(father)
        
        offspring.extend(children)

    # Mutate
    for melody in offspring:
        mutate(melody, mutation_range, mutation_rate)

    new_gen.extend(offspring)
    new_gen = new_gen[:len(seed_gen)] # Ensure the new generation is the right length

    return new_gen


# Is the note at the specified position part of a suspension? (dissonance resolving by step onto a consonance)
def is_suspension(melody, pos, cantus_firmus):    
    if (melody[pos] - cantus_firmus[pos + 1] == 3) and (melody[pos + 1] - cantus_firmus[pos + 1] == 2):
        return True
    elif (melody[pos] - cantus_firmus[pos + 1] == 6) and (melody[pos + 1] - cantus_firmus[pos + 1] == 5):
        return True
    else:
        return False

# rules below from http://www.donaldsonworkshop.com/coriakin/melody.html

# Ensure the melody starts appropriately, i.e. at a 5th/octave
def reward_start(interval):
    if interval == 7 or interval == 4:
        return 1.0
    else:
        return -0.1

# Ensure the melody ends appropriately, i.e. at an octave
def reward_end(interval):
    if interval == 7:
        return 1.0
    else:
        return -0.1

# Ensure the penultimate note is step wise onto the final note
def reward_penultimate(interval):
    if interval == 1:
        return 1.0
    else:
        return -0.7

# Reward contrary motion onto the final note
def reward_last_motion(interval1, interval2):
    if ((interval1 < 0 and interval2 > 0) or (interval1 > 0 and interval2 < 0)):
        return 1.0
    else:
        return -0.1   

# Ensure the penultimate note isn't a repeated note
def reward_penultimate_preparation(interval):
    if interval == 0:
        return -0.1
    else:
        # Movement to the penultimate note shouldn't be from too far away (not greater than a third).
        if interval < 2:
            return 1.0
        else:
            return -0.7

# Ensure dissonances are part of a step-wise movement
def reward_stepwise_dissonances(i, interval, contrapunctus):
    if i % 2 and interval in [3, 6, 8, 10]:
        # The current_note is a dissonance on the third beat of a bar. Check that both the adjacent notes are only a step away.
        if is_stepwise(contrapunctus, i):
            return 0.5
        else:
            return -0.1
    else:
        if is_stepwise(contrapunctus, i):
            return 0.5
        else:
            return 0.0

def punish_excess(quantity, limit):
    if quantity > limit:
        return -0.1
    else:
        return 0.0

    
# Return the fitness score assuming the cantus_firmus. Caches the fitness score in the melody.
def fitness_function(melody):

    # Melody-wide measures.
    repeat_threshold, jump_threshold = len(cantus_firmus) * 0.5, len(cantus_firmus) * 0.3


    fitness_score = 0.0 # The fitness score to be returned.
    repeats = 0 # Counts the number of repeated notes in the contrapunctus.
    thirds = 0 # Counts consecutive parallel thirds.
    sixths = 0 # Counts consecutive parallel sixths.
    parallel_motion = 0 # Counts the amount of parallel motion.
    jump_contour = 0 # Counts the number of jumps in the melodic contour.


    contrapunctus = melody.notes

    fitness_score += reward_start(contrapunctus[0] - cantus_firmus[0])

    fitness_score += reward_end(contrapunctus[-1] - cantus_firmus[-1])

    fitness_score += reward_penultimate(abs(contrapunctus[-1] - contrapunctus[-2]))

    fitness_score += reward_last_motion(cantus_firmus[-1] - cantus_firmus[-2], contrapunctus[-1] - contrapunctus[-2])

    fitness_score += reward_penultimate_preparation(abs(contrapunctus[-2] - contrapunctus[-3]))


    # Check the fitness of the body of the solution.
    solution = zip(contrapunctus, cantus_firmus)
    last_notes = solution.pop()
    last_interval = last_notes[0] - last_notes[1]
    for i in range(1, len(solution) - 2):
        current_notes = solution[i]
        contrapunctus_note, cantus_firmus_note = current_notes
        current_interval = contrapunctus_note - cantus_firmus_note

        # SPECIES ONE

        if current_interval == 2 and last_interval == 2: # Check for parallel thirds.
            thirds += 1

        if current_interval == 4 and last_interval == 4: # Check for parallel sixths.
            sixths += 1

        if is_parallel(last_notes, current_notes): # Check for parallel motion.
            parallel_motion += 1

        contour_leap = abs(current_notes[0] - last_notes[0]) # Check the melodic contour.
        if contour_leap > 2:
            jump_contour += contour_leap - 2

        if ((current_interval == 4 or current_interval == 7) and (last_interval == 4 or last_interval == 7)): # Punish parallel fifths or octaves.
            fitness_score -= 0.5

        if contrapunctus_note == last_notes[0]: # Check if the melody is a repeating note.
            repeats += 1



        # SPECIES TWO / THREE

        fitness_score += reward_stepwise_dissonances(i, current_interval, contrapunctus)

        # SPECIES FOUR

        # Check for a suspension.
        if is_suspension(contrapunctus, i, cantus_firmus):
            fitness_score += 1.0


        last_notes = current_notes
        last_interval = current_interval

    # SPECIES ONE PUNISHMENTS

    fitness_score += punish_excess(thirds, repeat_threshold) # Punish too many (> 1/3) parallel thirds

    fitness_score += punish_excess(sixths, repeat_threshold) # Punish too many (> 1/3) parallel sixths.

    fitness_score += punish_excess(parallel_motion, repeat_threshold) # Punish too many (> 1/3) parallel movements.

    fitness_score += punish_excess(jump_contour, jump_threshold) # Punish too many large leaps in the melody.

    # SPECIES FOUR PUNISHMENTS

    # Punish too many (> 1/3) repeated notes.
    fitness_score += punish_excess(repeats, repeat_threshold)

    melody.fitness = fitness_score

    return fitness_score


# Given a population of candidate solutions and generation count, indicates if an acceptable solution has been found
def halt_function(population, generation_count):    
    fittest = population[0].notes
    suspensions = 0

    for i in range(1, len(fittest) - 2):
        if is_suspension(fittest, i, cantus_firmus):
            suspensions += 1

    max_reward = 5.0
    return (population[0].fitness >= max_reward + suspensions or generation_count > 100)