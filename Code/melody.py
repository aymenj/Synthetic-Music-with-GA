import random
import gen_alg

# Some defaults.
DEFAULT_MAX_GENERATION = 100


VALID_INTERVALS = [2, 4, 5, 7, 9, 11] # Intervals between notes that are allowed (fourth sepcies counterpoint)

CONSONANCES, DISSONANCES = [2, 4, 5, 7, 9, 11], [3, 6, 8, 10] # Intervals between notes that are allowed (third species counterpoint)

VALID_ODD_BEAT_INTERVALS, VALID_EVEN_BEAT_INTERVALS = CONSONANCES, CONSONANCES + DISSONANCES

VALID_FIRST_BEAT_INTERVALS, VALID_THIRD_BEAT_INTERVALS = CONSONANCES, CONSONANCES + DISSONANCES


# Various rewards and punishments used with different aspects of the solution.
REWARD_FIRST, PUNISH_FIRST = 1, 0.1 # Reward / punishment to ensure the solution starts correctly (5th or 8ve).

REWARD_LAST, PUNISH_LAST = 1, 0.1 # Reward / punishment to ensure the solution finishes correctly (at an 8ve).

REWARD_LAST_STEP, PUNISH_LAST_STEP = 1, 0.7 # Reward / punishment to ensure the penultimate note is step wise onto the final note.

REWARD_LAST_MOTION, PUNISH_LAST_MOTION = 1, 0.1 # Reward / punish contrary motion onto the final note.

PUNISH_REPEATED_PENULTIMATE = 0.1 # Punishment if the penultimate note is a repeated note.

REWARD_PENULT_PREP, PUNISH_PENULT_PREP = 1, 0.7 # Ensure the movement to the penultimate note isn't from too far away (not greater than a third).

PUNISH_PRLL_FIFTHS_OCTS = 0.5 # Punish parallel fifths or octaves.

PUNISH_REPEATS = 0.1 # Punishment for too many repeated notes.

PUNISH_THIRDS = 0.1 # Punishment for too many parallel thirds

PUNISH_SIXTHS = 0.1 # Punishment for too many parallel sixths.

PUNISH_PARALLEL = 0.1 # Punishment for too many parallel/similar movements.

PUNISH_LEAPS = 0.1 # Punishment for too many large leaps in the melody.

REWARD_SUSPENSION = 1.0 # Reward for a valid suspension.

REWARD_STEPWISE_MOTION, PUNISH_STEPWISE_MOTION = 0.5, 0.1 # Reward / punish correct stepwise movement around dissonances.


# Create a new list of random candidate solutions of the specified number given the context of the cantus_firmus.
def create_population(number, cantus_firmus):
    
    result = []
    for i in range(number):
        new_chromosome = []
        for note in cantus_firmus:
            valid_range = [interval for interval in VALID_INTERVALS if (interval + note) < 17]
            interval = random.choice(valid_range)
            new_chromosome.append(note + interval)
        genome = Genome(new_chromosome)
        result.append(genome)
    return result


    '''result = []
    for i in range(number):
        new_chromosome = []
        for note in cantus_firmus:
            valid_odd_beat_range = [interval for interval in VALID_ODD_BEAT_INTERVALS if (interval + note) < 17]
            valid_even_beat_range = [interval for interval in VALID_EVEN_BEAT_INTERVALS if (interval + note) < 17]
            first_beat_interval = random.choice(valid_odd_beat_range)
            second_beat_interval = random.choice(valid_even_beat_range)
            third_beat_interval = random.choice(valid_odd_beat_range)
            fourth_beat_interval = random.choice(valid_even_beat_range)
            new_chromosome.append(note + first_beat_interval)
            new_chromosome.append(note + second_beat_interval)
            new_chromosome.append(note + third_beat_interval)
            new_chromosome.append(note + fourth_beat_interval)
        # Remove the last three beats since they're surplus to requirements.
        genome = Genome(new_chromosome[:-3])
        result.append(genome)
    return result'''

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

# Return a function that takes a seed generation and returns a new population.
def make_generator(mutation_range, mutation_rate, cantus_firmus):

    # Return a new generation of candidate solutions assuming the cantus_firmus and other settings in the closure.
    def generator(seed_gen):
        
        new_gen = seed_gen[:len(seed_gen)/2] # Keep the fittest 50%

        # Breed the remaining 50% using roulette wheel selection
        offspring = []
        while len(offspring) < len(seed_gen)/2:
            mother, father = gen_alg.roulette_wheel(seed_gen), gen_alg.roulette_wheel(seed_gen)
            children = mother.breed(father)
            offspring.extend(children)

        # Mutate
        for genome in offspring:
            genome.mutate(mutation_range, mutation_rate, cantus_firmus)

        new_gen.extend(offspring)
        new_gen = new_gen[:len(seed_gen)] # Ensure the new generation is the right length

        return new_gen

    return generator


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
        return REWARD_FIRST
    else:
        return -PUNISH_FIRST

# Ensure the melody ends appropriately, i.e. at an octave
def reward_end(interval):
    if interval == 7:
        return REWARD_LAST
    else:
        return -PUNISH_LAST

# Ensure the penultimate note is step wise onto the final note
def reward_penultimate(interval):
    if interval == 1:
        return REWARD_LAST_STEP
    else:
        return -PUNISH_LAST_STEP

# Reward contrary motion onto the final note
def reward_last_motion(interval1, interval2):
    if ((interval1 < 0 and interval2 > 0) or (interval1 > 0 and interval2 < 0)):
        return REWARD_LAST_MOTION
    else:
        return -PUNISH_LAST_MOTION    

# Ensure the penultimate note isn't a repeated note
def reward_penultimate_preparation(interval):
    if interval == 0:
        return -PUNISH_REPEATED_PENULTIMATE
    else:
        # Movement to the penultimate note shouldn't be from too far away (not greater than a third).
        if interval < 2:
            return REWARD_PENULT_PREP
        else:
            return -PUNISH_PENULT_PREP

# Ensure dissonances are part of a step-wise movement
def reward_stepwise_dissonances(i, interval, contrapunctus):
    if i % 2 and interval in [3, 6, 8, 10]:
        # The current_note is a dissonance on the third beat of a bar. Check that both the adjacent notes are only a step away.
        if is_stepwise(contrapunctus, i):
            return REWARD_STEPWISE_MOTION
        else:
            return -PUNISH_STEPWISE_MOTION
    else:
        if is_stepwise(contrapunctus, i):
            return REWARD_STEPWISE_MOTION
        else:
            return 0.0

def punish_excess(quantity, limit, punishment):
    if quantity > limit:
        return -punishment
    else:
        return 0.0

# Returns a function that takes a single Genome instance and returns a fitness score.
def make_evaluator(cantus_firmus):

    # Melody-wide measures.
    repeat_threshold, jump_threshold = len(cantus_firmus) * 0.5, len(cantus_firmus) * 0.3
    
    # Return the fitness score assuming the cantus_firmus in this closure. Caches the fitness score in the genome.
    def evaluator(genome):
        
        # Save some time!
        if genome.fitness is not None:
            return genome.fitness

    
        fitness_score = 0.0 # The fitness score to be returned.
        repeats = 0 # Counts the number of repeated notes in the contrapunctus.
        thirds = 0 # Counts consecutive parallel thirds.
        sixths = 0 # Counts consecutive parallel sixths.
        parallel_motion = 0 # Counts the amount of parallel motion.
        jump_contour = 0 # Counts the number of jumps in the melodic contour.


        contrapunctus = genome.chromosome

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
                fitness_score -= PUNISH_PRLL_FIFTHS_OCTS

            if contrapunctus_note == last_notes[0]: # Check if the melody is a repeating note.
                repeats += 1



            # SPECIES TWO / THREE

            fitness_score += reward_stepwise_dissonances(i, current_interval, contrapunctus)

            # SPECIES FOUR

            # Check for a suspension.
            if is_suspension(contrapunctus, i, cantus_firmus):
                fitness_score += REWARD_SUSPENSION


            last_notes = current_notes
            last_interval = current_interval

        # SPECIES ONE PUNISHMENTS

        fitness_score += punish_excess(thirds, repeat_threshold, PUNISH_THIRDS) # Punish too many (> 1/3) parallel thirds

        fitness_score += punish_excess(sixths, repeat_threshold, PUNISH_SIXTHS) # Punish too many (> 1/3) parallel sixths.

        fitness_score += punish_excess(parallel_motion, repeat_threshold, PUNISH_PARALLEL) # Punish too many (> 1/3) parallel movements.

        fitness_score += punish_excess(jump_contour, jump_threshold, PUNISH_LEAPS) # Punish too many large leaps in the melody.

        # SPECIES FOUR PUNISHMENTS

        # Punish too many (> 1/3) repeated notes.
        fitness_score += punish_excess(repeats, repeat_threshold, PUNISH_REPEATS)

        genome.fitness = fitness_score

        return fitness_score

    return evaluator

# Return a halt function 
def make_halter(cantus_firmus):

    # Given a population of candidate solutions and generation count, indicates if an acceptable solution has been found
    def halter(population, generation_count):    
        fittest = population[0].chromosome
        suspensions = 0

        for i in range(1, len(fittest) - 2):
            if is_suspension(fittest, i, cantus_firmus):
                suspensions += 1

        max_reward = REWARD_FIRST + REWARD_LAST + REWARD_LAST_STEP + REWARD_LAST_MOTION + REWARD_PENULT_PREP
        return (population[0].fitness >= max_reward + suspensions or
            generation_count > DEFAULT_MAX_GENERATION)

    return halter


# Represent a candidate solution for counterpoint
class Genome(gen_alg.Genome):

    # Mutates the genotypes no more than the mutation_range depending on the mutation_rate given and the cantus_firmus passed in
    # as the context (to ensure the mutation is valid).
    def mutate(self, mutation_range, mutation_rate, context):
        
        # SECOND SPECIES
        first_beat_mutation_intervals = [interval for interval in VALID_FIRST_BEAT_INTERVALS if interval <= mutation_range]
        third_beat_mutation_intervals = [interval for interval in VALID_THIRD_BEAT_INTERVALS if interval <= mutation_range]

        # THIRD SPECIES
        odd_beat_mutation_intervals = [interval for interval in VALID_ODD_BEAT_INTERVALS if interval <= mutation_range]
        even_beat_mutation_intervals = [interval for interval in VALID_EVEN_BEAT_INTERVALS if interval <= mutation_range]
        chromosome_length = len(self.chromosome)

        # FOURTH SPECIES
        FOURTH_mutation_intervals = [interval for interval in VALID_INTERVALS if interval <= mutation_range]

        for locus in range(len(self.chromosome)):
            if mutation_rate >= random.random():

                # SPECIES TWO
                cantus_firmus_note = context[locus / 2]
                if locus % 2:
                    # Current melody note is on the third beat of the bar
                    SECOND_mutation_intervals = third_beat_mutation_intervals
                else:
                    # Current melody note is on the first beat of the bar.
                    SECOND_mutation_intervals = first_beat_mutation_intervals

                SECOND_mutation_range = [interval for interval in SECOND_mutation_intervals if (interval + cantus_firmus_note) < 17]


                # SPECIES THREE
                cantus_firmus_note = context[locus / 4]
                # The pitch of the notes immediately before and after the current note (used to avoid mutations that result in a
                # repeated pitch).
                pitches_to_avoid = []
                if locus > 0:
                    pre_pitch = self.chromosome[locus - 1]
                    pitches_to_avoid.append(pre_pitch)
                if locus < chromosome_length - 2:
                    post_pitch = self.chromosome[locus + 1]
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
                cantus_firmus_note = context[locus]
                FOURTH_mutation_range = [interval for interval in FOURTH_mutation_intervals if (interval + cantus_firmus_note) < 17]


                
                valid_mutation_range = list(set(SECOND_mutation_range) & set(THIRD_mutation_range) & set(FOURTH_mutation_range))
                
                mutation = random.choice(valid_mutation_range)
                new_allele = cantus_firmus_note + mutation
                self.chromosome[locus] = new_allele
                # Resets fitness score
                self.fitness = None
