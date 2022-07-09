import numpy as np
import matplotlib.pyplot as plt

#=====================================================================================
class Environment:
    def __init__(self, network, people, mean_skill, no_days, skill_sd=None, debug=True):
        # These percentile values are used to mimic indian diversity
        # values obtained from percentile values of the distribution
        self.LOW_SKILL          = 40
        self.MED_SKILL          = 60
        self.HIGH_SKILL         = 85


        self.no_people          = people
        self.mean_skill         = mean_skill
        self.skill_sd           = skill_sd
        self.network            = network
        if not skill_sd:
            self.skill_sd       =  self.mean_skill/4
        
        self.people_skill       = np.random.normal(
                                        loc=self.mean_skill, 
                                        scale=self.skill_sd, 
                                        size=self.no_people)
                            

        self.no_days            = no_days
        self.pop                = []

        


    def plotSkillLevel(self):
        count, bins, ignored = plt.hist(self.people_skill, 30)
        plt.show()
    
    def genPopulation(self):
        #done at sim time to optimize distributed performance
        for i, slvl in enumerate(self.people_skill):
            self.pop.append(People(i))
        return self.pop
    
    def runGov(self):
        score  = 0
        for day in range(self.no_days):
            #work
            #calc productivity
            #calc equality
            days = day ** 2 ** 2 ** 2 
            
        return score