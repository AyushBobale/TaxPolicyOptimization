from classes.agent import Agent
from classes.people import People
from classes.environment import Environment
from classes.saveModel import SaveModel

from utils.configWriter import ConfigWriter
from utils.termColors import TermColors

import neat
import os
import pickle
import ray
import time
import sys
import colored
from colored import stylize, fg, bg, attr

sys.path.append(os.path.join(os.path.dirname(__file__)))
#=====================================================================================
# TODO 
# *** Colored refactor from colors to coloured
# ** code clean up [not optimization]
# sys arg execution flow control 
# More better metric of fitness
#   - gini index
#   - procutivity = wealth + tax - welfare
#
# change config writer to neat's own provided module
# IK the code is a bit redundant will optimise later hopefully

#=====================================================================================
#VARS
CHECKPOINT              = 500
GENERATIONS             = 2
POPSIZE                 = 64
N_HIDDEN                = 2
N_INPUTS                = 5
N_OUTPUTS               = 4

EXPO                    = 2         # indicates level how fast can skilled become richer
SIM_POP_SIZE            = 50
SIM_MEAN_SKILL          = 50
SIM_N_DAYS              = 1000
SIM_SKILL_SD            = 20 
SIM_BASIC_SPENDING      = (20/10) ** EXPO  
SIM_EDUCATION_COST      = (25/10) ** EXPO
SIM_EDUCATION_MULT      = 1
SIM_INITIAL_COINS       = 100

#this function (n/10) ** Expo gives us at what skill lvl is it possible to survive

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

    if sys.argv[1] == "1":
        winner = pop.run(eval_genome, GENERATIONS)
    if sys.argv[1] == "0":
        winner = pop.run(eval_genome_nonDist, GENERATIONS)
    model = SaveModel(winner, args)
    with open("best_pickle.pkl", "wb") as f:
        pickle.dump(model, f)


def testNeat(config):
    print("Testing model ==========================================: ")
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
    '''
    1 : Distributed mode [1 | 0]
    2 : Test | Train | Train & Test [0 | 1 | 2]
    3 : Colab Mode [0 | 1]
    '''
    if sys.argv[1] == "1":
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
    
    if sys.argv[2] == "1" or sys.argv[2] == "2":
        starttime = time.time()
        runNeat(config)
        print(f"Execution time : {time.time() - starttime}")
    
    if sys.argv[2] == "0" or sys.argv[2] == "2":
        testNeat(config)
        
    print(stylize("Test", TermColors.info))
    

