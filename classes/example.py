from rust_classes import RustEnvironment as REnvironment
from environment import Environment
import timeit
import numpy as np



env = REnvironment(  expo                = 2,
                    sim_pop_size        = 1000,
                    sim_mean_skill      = 50,
                    sim_n_days          = 1000,
                    sim_skill_sd        = 50/4,
                    sim_basic_spending  = (15/10) ** 2,
                    sim_education_cost  = (15/10) ** 2,
                    sim_education_mult  = 2,
                    sim_initial_coins   = 1000,
                    sim_tax_rate        = [0, 0, 0, 0]  )
print("score Rust ============================== ", env.runGov())
# print("Skills", env.genPopulation())
env.getScores()
print("-------------------------------------")

# args = {"expo"              : 2,
#         "sim_pop_size"      : 1000,
#         "sim_mean_skill"    : 50,
#         "sim_n_days"        : 100,
#         "sim_skill_sd"      : 50/4,
#         "sim_basic_spending": (15/10) ** 2,
#         "sim_education_cost": (15/10) ** 2,
#         "sim_education_mult": 2,
#         "sim_initial_coins" : 1000}
# env = Environment( None , args )
# print("score Python ============================== ", env.runGov(debug=True))
# env.getScores()

#----------------------------------------------------
# setup = """
# from rust_classes import RustEnvironment as REnvironment
# from environment import Environment
# env = REnvironment(  expo                = 2,
#                     sim_pop_size        = 1000,
#                     sim_mean_skill      = 50,
#                     sim_n_days          = 1000,
#                     sim_skill_sd        = 50/4,
#                     sim_basic_spending  = (15/10) ** 2,
#                     sim_education_cost  = (15/10) ** 2,
#                     sim_education_mult  = 2,
#                     sim_initial_coins   = 1000  )
# """
# code = """
# env.runGov()
# """
# print ("Rust time : ", timeit.timeit(setup = setup,
#                      stmt = code,
#                      number = 10))




# setup = """
# from rust_classes import RustEnvironment as REnvironment
# from environment import Environment
# args = {"expo"              : 2,
#         "sim_pop_size"      : 1000,
#         "sim_mean_skill"    : 50,
#         "sim_n_days"        : 1000,
#         "sim_skill_sd"      : 50/4,
#         "sim_basic_spending": (15/10) ** 2,
#         "sim_education_cost": (15/10) ** 2,
#         "sim_education_mult": 2,
#         "sim_initial_coins" : 1000}
# env = Environment( None , args )
# """
# code = """
# env.runGov(debug=True)
# """
# print ("Python time : ", timeit.timeit(setup = setup,
#                      stmt = code,
#                      number = 10))
