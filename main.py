from classes.agent import Agent
from classes.people import People
from classes.environment import Environment

from utils.configWriter import ConfigWriter

import neat
import os
import pickle
import ray
import time

#=====================================================================================
# TODO 
# Softmax implementation
# network.activate implemntation

#=====================================================================================
#VARS
CHECKPOINT              = 500
GENERATIONS             = 100
POPSIZE                 = 50
N_HIDDEN                = 2
N_INPUTS                = 4
N_OUTPUTS               = 4

SIM_POP_SIZE            = 10
SIM_MEAN_SKILL          = 50
SIM_N_DAYS              = 1000
SIM_SKILL_SD            = 20 
SIM_BASIC_SPENDING      = 30 ** 2
SIM_EDUCATION_COST      = 10 ** 2
SIM_EDUCATION_MULT      = 1
SIM_INITIAL_COINS       = 100
#=====================================================================================
@ray.remote
def distFunction(genome):
    network         = neat.nn.FeedForwardNetwork.create(genome, config)
    env = Environment(  network         = network, 
                            people          = SIM_POP_SIZE, 
                            mean_skill      = SIM_MEAN_SKILL, 
                            no_days         = SIM_N_DAYS, 
                            basic_spending  = SIM_BASIC_SPENDING, 
                            skill_sd        = SIM_SKILL_SD,
                            education_cost  = SIM_EDUCATION_COST,
                            education_mult  = SIM_EDUCATION_MULT,
                            initial_coins   = SIM_INITIAL_COINS)
    return  1 - env.runGov()


def eval_genome(genomes, config):
    futures = []
    for genomeid, genome in genomes:
        futures.append(distFunction.remote(genome))
    
    for i, (genomeid, genome) in enumerate(genomes):
        genome.fitness =  ray.get(futures[i])


def eval_genome_nonDist(genomes, config):
    for genomeid, genome in genomes:
        network         = neat.nn.FeedForwardNetwork.create(genome, config)
        env = Environment(  network         = network, 
                            people          = SIM_POP_SIZE, 
                            mean_skill      = SIM_MEAN_SKILL, 
                            no_days         = SIM_N_DAYS, 
                            basic_spending  = SIM_BASIC_SPENDING, 
                            skill_sd        = SIM_SKILL_SD,
                            education_cost  = SIM_EDUCATION_COST,
                            education_mult  = SIM_EDUCATION_MULT,
                            initial_coins   = SIM_INITIAL_COINS)
        genome.fitness = 1 - env.runGov()


def runNeat(config):
    #pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint1')
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(CHECKPOINT))

    winner = pop.run(eval_genome, GENERATIONS)
    with open("best_pickle.pkl", "wb") as f:
        pickle.dump(winner, f)

#=====================================================================================
if __name__ == "__main__":
    ray.init()

    confWriter = ConfigWriter(  n_inputs    = N_INPUTS,
                                n_outputs   = N_INPUTS, 
                                n_hidden    = N_HIDDEN, 
                                pop_size    = POPSIZE)
    confWriter.writeFile('config.txt')

    LOCALDIR = os.path.dirname(__file__)
    config_path = os.path.join(LOCALDIR, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    starttime = time.time()
    runNeat(config)
    print(f"Execution time : {time.time() - starttime}")
    

    # env = Environment(None, 10000, 50, 100)
    # env.plotSkillLevel()
    # #env.genPopulation()




