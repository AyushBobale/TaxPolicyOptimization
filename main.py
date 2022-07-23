from classes.agent import Agent
from classes.people import People
from classes.environment import Environment
from classes.saveModel import SaveModel

from utils.configWriter import ConfigWriter

import neat
import os
import pickle
import ray
import time
import sys
# from colors import color
sys.path.append(os.path.join(os.path.dirname(__file__)))
#=====================================================================================
# TODO 
# More better metric of fitness
#   - gini index
#   - procutivity = wealth + tax - welfare
#
# change config writer to neat's own provided module
# IK the code is a bit redundant will optimise later hopefully

#=====================================================================================
#VARS
CHECKPOINT              = 500
GENERATIONS             = 20
POPSIZE                 = 64
N_HIDDEN                = 2
N_INPUTS                = 5
N_OUTPUTS               = 4

EXPO                    = 2         # indicates level how fast can skilled become richer
SIM_POP_SIZE            = 200
SIM_MEAN_SKILL          = 200
SIM_N_DAYS              = 30
SIM_SKILL_SD            = 20 
SIM_BASIC_SPENDING      = (12/10) ** EXPO
SIM_EDUCATION_COST      = (12/10) ** EXPO
SIM_EDUCATION_MULT      = 1
SIM_INITIAL_COINS       = 100

args = {"gens"              : GENERATIONS,
        "popsize"           : POPSIZE,
        "n_hidden"          : N_HIDDEN,
        "n_inputs"          : N_INPUTS,
        "n_outputs"         : N_OUTPUTS,
        "expo"              : EXPO,
        "sim_pop_size"      : SIM_POP_SIZE,
        "sim_mean_skill"    : SIM_MEAN_SKILL,
        "sim_n_days"        : SIM_N_DAYS,
        "sim_skill_sd"      : SIM_SKILL_SD,
        "sim_basic_spending": SIM_BASIC_SPENDING,
        "sim_education_cost": SIM_EDUCATION_COST,
        "sim_education_mult": SIM_EDUCATION_MULT,
        "sim_initial_coins" : SIM_INITIAL_COINS}

#=====================================================================================
# Stupid work around del it later from final code 
# work around for colab

def color(text, style, fg):
    return text

@ray.remote
def distFunction(genome):
    network         = neat.nn.FeedForwardNetwork.create(genome, config)
    env = Environment(  network         = network, 
                        args            = args)
    return 2 - env.runGov()


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
                            args            = args)
        genome.fitness = 2 - env.runGov()


def runNeat(config):
    #pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint1')
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(CHECKPOINT))

    winner = pop.run(eval_genome, GENERATIONS)
    model = SaveModel(winner, args)
    with open("best_pickle.pkl", "wb") as f:
        pickle.dump(model, f)


def testNeat(config):
    print(color("Testing model ==========================================: ", fg="green",style="bold+underline"))
    #/content/drive/Othercomputers/My computer (1)/TaxPolicyOptimization/
    with open("best_pickle.pkl","rb") as f:
        model = pickle.load(f)
    winner = model.winner
    print(f"Args : {model.args}")
    
    network         = neat.nn.FeedForwardNetwork.create(winner, config)

    env = Environment(  network         = network,  
                        args            = args)
    env.runGov(test=True)
    env.getScores()
                            
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
    
    
    testNeat(config)
    

