class ConfigWriter:
    def __init__(self,  n_inputs = None, n_outputs = None, n_hidden = None, pop_size = None):
        num_hidden  = n_hidden  if n_hidden     else 2
        num_inputs  = n_inputs  if n_inputs     else 2
        num_outputs = n_outputs if n_outputs    else 1
        pop_size    = pop_size  if pop_size     else 48

        self.text   = f"""
[NEAT]
fitness_criterion     = max
fitness_threshold     = 0.8
pop_size              = {pop_size}
reset_on_extinction   = False

[DefaultStagnation]
species_fitness_func = max
max_stagnation       = 30
species_elitism      = 2

[DefaultReproduction]
elitism            = 2
survival_threshold = 0.2

[DefaultGenome]
# node activation options
activation_default      = relu
activation_mutate_rate  = 1.0
activation_options      = relu

# node aggregation options
aggregation_default     = sum
aggregation_mutate_rate = 0.0
aggregation_options     = sum

# node bias options
bias_init_mean          = 3.0
bias_init_stdev         = 1.0
bias_max_value          = 30.0
bias_min_value          = -30.0
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7
bias_replace_rate       = 0.1

# genome compatibility options
compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient   = 0.5

# connection add/remove rates
conn_add_prob           = 0.5
conn_delete_prob        = 0.5

# connection enable options
enabled_default         = True
enabled_mutate_rate     = 0.01

feed_forward            = True
initial_connection      = full_direct

# node add/remove rates
node_add_prob           = 0.2
node_delete_prob        = 0.2

# network parameters
num_hidden              = {num_hidden}
num_inputs              = {num_inputs}
num_outputs             = {num_outputs}

# node response options
response_init_mean      = 1.0
response_init_stdev     = 0.0
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

# connection weight options
weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

[DefaultSpeciesSet]
compatibility_threshold = 3.0
                """
    
    def writeFile(self, path):
        with open(path, 'w') as f:
            f.write(self.text)