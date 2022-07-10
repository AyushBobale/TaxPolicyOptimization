import numpy as np
import matplotlib.pyplot as plt
import time

from people import People
#=====================================================================================
class Environment:
    def __init__(self, network, people, mean_skill, no_days, skill_sd=None, debug=True):
        # These percentile values are used to mimic indian diversity
        # values obtained from percentile values of the distribution
        # now job level control  how much everyone gets paid
        self.LOW_SKILL          = 30
        self.MED_SKILL          = 50
        self.HIGH_SKILL         = 75

        self.tax_rate           = (0.1, 0.2, 0.3, 0.4)
        self.tax_bracket        = (self.LOW_SKILL, self.MED_SKILL, self.HIGH_SKILL)


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
        self.jobs               = list(np.random.normal(
                                        loc=self.mean_skill, 
                                        scale=self.skill_sd, 
                                        size=self.no_people))
        self.taxes_collected    = { '<LOW'    : [0,0],
                                    'LOW>MED' : [0,0],
                                    'MED>HIGH': [0,0],
                                    '>HIGH'   : [0,0] }
        self.tot_tax            = 0
        


    def plotSkillLevelvsJobs(self):
        count, bins, ignored = plt.hist(self.people_skill, 30)
        count, bins, ignored = plt.hist(self.jobs, 30)
        plt.show()
    

    def getAvgTax(self):
        avg_tax = []
        for value in self.taxes_collected.values():
            avg_tax.append(value[1]/value[0])
        return avg_tax


    def genPopulation(self):
        #done at sim time to optimize distributed performance
        for i, slvl in enumerate(self.people_skill):
            self.pop.append(People(slvl))
        return self.pop

    
    def genJobs(self, mean_skill, no_jobs, skill_sd=None):
        # genrates available jobs in the market
        # can be customized as per needs and the env it is modeled against
        # consideration generates the same n of jobs as people
        # a concept from the econmy simulation video can be impleneted for less or more jobs
        # will be considered for later
        # Point to consider 
        # as the econmy progesses the job levels should also progress
        # to be implemented
        if not skill_sd:
            skill_sd            = mean_skill/4
        self.jobs               = list(np.random.normal(
                                        loc=mean_skill, 
                                        scale=skill_sd, 
                                        size=no_jobs))
        
    def collectTax(self, tax):
        self.tot_tax += tax[0]

        if tax[1] <= self.LOW_SKILL:
            self.taxes_collected['<LOW'][1] += tax[0]
            self.taxes_collected['<LOW'][0] += 1

        if tax[1] > self.LOW_SKILL and tax[1] <=  self.MED_SKILL:
            self.taxes_collected['LOW>MED'][1] += tax[0]
            self.taxes_collected['LOW>MED'][0] += 1

        if tax[1] > self.MED_SKILL and tax[1] <= self.HIGH_SKILL:
            self.taxes_collected['MED>HIGH'][1] += tax[0]
            self.taxes_collected['MED>HIGH'][0] += 1

        if tax[1] > self.HIGH_SKILL:
            self.taxes_collected['>HIGH'][1] += tax[0]        
            self.taxes_collected['>HIGH'][0] += 1        

        

    def runGov(self):
        score  = 0
        self.genPopulation()

        # optimize this loop
        for day in range(self.no_days):

            self.jobs.sort()
            self.pop.sort(key = lambda x : x.skill_lvl)

            for person in self.pop:

                if  person.work(self.jobs[0]):
                    del self.jobs[0]

                self.collectTax(person.payTax(self.tax_rate, self.tax_bracket))
                person.spend()
                person.accquireSkill()
                person.availSocialWelfare()
                person.dayEnd()
            
            self.genJobs(self.mean_skill, self.no_people)

        return score
    

    def getScores(self):
        coins = []
        skill_lvl = []
        
        
        for person in self.pop:
            skill_lvl.append(person.skill_lvl)
            coins.append(person.coins)
        
        print(self.taxes_collected)
        print(self.tot_tax)

        print("avgtax", self.getAvgTax())

        return None


if __name__ == "__main__":
    SIM_POP_SIZE            = 10000
    SIM_MEAN_SKILL          = 50
    SIM_N_DAYS              = 100
    SIM_SKILL_SD            = None

    env = Environment(None, SIM_POP_SIZE, SIM_MEAN_SKILL, SIM_N_DAYS, SIM_SKILL_SD)
    starttime = time.time()
    env.runGov()
    print(f"Exec time : {time.time()-starttime}")
    print(env.getScores())
    env.plotSkillLevelvsJobs()