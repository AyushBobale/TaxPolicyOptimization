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
#VARS
CHECKPOINT              = 500
GENERATIONS             = 200
POPSIZE                 = 100
N_HIDDEN                = 2
N_INPUTS                = 2
N_OUTPUTS               = 2

SIM_POP_SIZE            = 10000
SIM_MEAN_SKILL          = 50
SIM_N_DAYS              = 1000
#=====================================================================================
@ray.remote
def distFunction(genome):
    network         = neat.nn.FeedForwardNetwork.create(genome, config)
    env = Environment(network, SIM_POP_SIZE, SIM_MEAN_SKILL, SIM_N_DAYS)
    return env.runGov()


def eval_genome(genomes, config):
    futures = []
    for genomeid, genome in genomes:
        futures.append(distFunction.remote(genome))
    
    for i, (genomeid, genome) in enumerate(genomes):
        genome.fitness =  ray.get(futures[i])


def eval_genome_nonDist(genomes, config):
    for genomeid, genome in genomes:
        network         = neat.nn.FeedForwardNetwork.create(genome, config)
        env = Environment(network, SIM_POP_SIZE, SIM_MEAN_SKILL, SIM_N_DAYS)
        genome.fitness = env.runGov()


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




