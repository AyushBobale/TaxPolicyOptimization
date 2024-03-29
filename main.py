from classes.people import People
# from classes.environment import Environment
from rust_classes import RustEnvironment as Environment
from classes.saveModel import SaveModel

from utils.configWriter import ConfigWriter
from utils.termColors import TermColors

import neat
import os
import pickle
import ray
import time
import sys
from sklearn import preprocessing as pp
import numpy as np
import colored
from colored import stylize, fg, bg, attr
from math import exp

sys.path.append(os.path.join(os.path.dirname(__file__)))
#=====================================================================================
# TODO 
# network.activate()
# *** better softmax 
# *** nan error
# ** code clean up [not optimization]
# More better metric of fitness
#   - gini index
#   - procutivity = wealth + tax - welfare
#
# change config writer to neat's own provided module
# IK the code is a bit redundant will optimise later hopefully
# probability of working is a function of tax rate
# following update would be scoring based on total productivity
# average productiviy could be calculated as 
# (total wealth + total tax)/(no_days * no_people) would be a expo function as it depends on it

# There is no concept of money vaue depreciation / appreciation for assets
# basic spending should scale according to inflation
# - Only Employer is government
# - There are as such no assets to be bought currenty

# think about increasing job level as a result of increasing economy
# as we have a way to increase skill lvl

#=====================================================================================
#VARS
CHECKPOINT              = 500
GENERATIONS             = 10
POPSIZE                 = 128
N_HIDDEN                = 2
N_INPUTS                = 4
N_OUTPUTS               = 4

EXPO                    = 2         # indicates level how fast can skilled become richer
SIM_POP_SIZE            = 100
SIM_MEAN_SKILL          = 50
SIM_N_DAYS              = 1000
SIM_SKILL_SD            = 20 
SIM_BASIC_SPENDING      = (20/10) ** EXPO  
SIM_EDUCATION_COST      = (25/10) ** EXPO
SIM_EDUCATION_MULT      = 1
SIM_INITIAL_COINS       = 100

# this function (n/10) ** Expo gives us at what skill lvl is it possible to survive
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

@ray.remote
def distFunction(genome, config):
    network         = neat.nn.FeedForwardNetwork.create(genome, config)
    # this is a mess
    output          = network.activate(
                        pp.normalize(
                        np.array([[SIM_MEAN_SKILL, SIM_SKILL_SD, SIM_BASIC_SPENDING, SIM_EDUCATION_COST]]))[0])
    exp_sum         = sum([exp(op) for op in output])
    SIM_TAX_RATE    = [exp(op)/exp_sum for op in output]
    env = Environment(  expo                = EXPO,
                        sim_pop_size        = SIM_POP_SIZE,
                        sim_mean_skill      = SIM_MEAN_SKILL,
                        sim_n_days          = SIM_N_DAYS,
                        sim_skill_sd        = SIM_SKILL_SD,
                        sim_basic_spending  = SIM_BASIC_SPENDING,
                        sim_education_cost  = SIM_EDUCATION_COST,
                        sim_education_mult  = SIM_EDUCATION_MULT,
                        sim_initial_coins   = SIM_INITIAL_COINS,
                        sim_tax_rate        = SIM_TAX_RATE)
    # deprecated =========================================================
    # env = Environment(  network         = network, 
    #                     args            = args)
    return 2 - env.runGov()

def eval_genome(genomes, config):
    futures = []
    for genomeid, genome in genomes:
        futures.append(distFunction.remote(genome, config))
    
    for i, (genomeid, genome) in enumerate(genomes):
        genome.fitness =  ray.get(futures[i])


def eval_genome_nonDist(genomes, config):
    for genomeid, genome in genomes:
        network         = neat.nn.FeedForwardNetwork.create(genome, config)
        output          = network.activate(
                        pp.normalize(
                        np.array([[SIM_MEAN_SKILL, SIM_SKILL_SD, SIM_BASIC_SPENDING, SIM_EDUCATION_COST]]))[0])
        exp_sum         = sum([exp(op) for op in output])
        SIM_TAX_RATE    = [exp(op)/exp_sum for op in output]
        env = Environment(  expo                = EXPO,
                            sim_pop_size        = SIM_POP_SIZE,
                            sim_mean_skill      = SIM_MEAN_SKILL,
                            sim_n_days          = SIM_N_DAYS,
                            sim_skill_sd        = SIM_SKILL_SD,
                            sim_basic_spending  = SIM_BASIC_SPENDING,
                            sim_education_cost  = SIM_EDUCATION_COST,
                            sim_education_mult  = SIM_EDUCATION_MULT,
                            sim_initial_coins   = SIM_INITIAL_COINS,
                            sim_tax_rate        = SIM_TAX_RATE)
        # deprecated =========================================================
        # env = Environment(  network         = network, 
        #                     args            = args)
        
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
    # Colored.stylize
    print(stylize("Testing model ==========================================: ", TermColors.infoHead))
    #/content/drive/Othercomputers/My computer (1)/TaxPolicyOptimization/
    with open("best_pickle.pkl","rb") as f:
        model = pickle.load(f)
    winner = model.winner
    # print(f"Args : {model.args}")
    args = model.args
    
    network         = neat.nn.FeedForwardNetwork.create(winner, config)
    output          = network.activate(
                        pp.normalize(
                        np.array([[args["sim_mean_skill"], args["sim_skill_sd"], args["sim_basic_spending"], args["sim_education_cost"]]]))[0])
    exp_sum         = sum([exp(op) for op in output])
    SIM_TAX_RATE    = [exp(op)/exp_sum for op in output]
    env = Environment(  expo                = args["expo"],
                        sim_pop_size        = args["sim_pop_size"],
                        sim_mean_skill      = args["sim_mean_skill"],
                        sim_n_days          = args["sim_n_days"],
                        sim_skill_sd        = args["sim_skill_sd"],
                        sim_basic_spending  = args["sim_basic_spending"],
                        sim_education_cost  = args["sim_education_cost"],
                        sim_education_mult  = args["sim_education_mult"],
                        sim_initial_coins   = args["sim_initial_coins"],
                        sim_tax_rate        = SIM_TAX_RATE)
    # deprecated
    # env = Environment(  network         = network,  
    #                     args            = args)
    env.runGov()
    env.getScores()
                            
#=====================================================================================
if __name__ == "__main__":
    '''
    1 : Distributed mode [1 | 0]
    2 : Test | Train | Train & Test [0 | 1 | 2]
    '''
    print(sys.argv)
    if sys.argv[1] == "1":
        ray.init(job_config=ray.job_config.JobConfig(code_search_path=sys.path))

    confWriter = ConfigWriter(  n_inputs    = N_INPUTS,
                                n_outputs   = N_OUTPUTS, 
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