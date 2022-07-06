import numpy as np
import matplotlib.pyplot as plt

#=====================================================================================
class People:
    def __init__(self, skill_lvl):
        self.skill_lvl          = skill_lvl
        self.coins              = 0

#=====================================================================================
class Environment:
    def __init__(self, people, mean_skill, skill_sd=None, debug=True):
        # These percentile values are used to mimic indian diversity
        # values obtained from percentile values of the distribution
        self.LOW_SKILL          = 40
        self.MED_SKILL          = 60
        self.HIGH_SKILL         = 85


        self.no_people          = people
        self.mean_skill         = mean_skill
        self.skill_sd           = skill_sd
        if not skill_sd:
            self.skill_sd       =  self.mean_skill/4
        
        self.people_skill       = np.random.normal(
                                        loc=self.mean_skill, 
                                        scale=self.skill_sd, 
                                        size=self.no_people)
                            

        self.days               = []
        self.pop                = []

        if debug:
            print("Debug is enabled")
        


    def plotSkillLevel(self):
        count, bins, ignored = plt.hist(self.people_skill, 30)
        plt.show()
    
    def genPopulation(self):
        for i, slvl in enumerate(self.people_skill):
            self.pop.append(People(i))
        return self.pop

#=====================================================================================
class Agent:
    def __init__(self):
        pass


if __name__ == "__main__":
    env = Environment(10000, 50)
    env.plotSkillLevel()
    env.genPopulation()




