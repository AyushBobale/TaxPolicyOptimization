import numpy as np
import matplotlib.pyplot as plt
import time

from people import People
#=====================================================================================
# Better skill level generation function
# same to be implented in job generation
# basically a way to clamp vlaues within range
# think about increasing job level
class Environment:
    def __init__(   self, 
                    network, 
                    people, 
                    mean_skill, 
                    no_days, 
                    basic_spending=20, 
                    skill_sd=None, 
                    education_cost = 20,
                    initial_coins = 100,
                    debug=True):
        # values obtained from percentile values of the distribution
        # now job level control  how much everyone gets paid
        # try incorporating inflation not hardcoded like % increase per year 
        # more dynamic like when money is printed
        self.LOW_SKILL          = 30
        self.MED_SKILL          = 50
        self.HIGH_SKILL         = 75

        self.tax_rate           = (0.1, 0.2, 0.3, 0.4)
        self.tax_bracket        = (self.LOW_SKILL, self.MED_SKILL, self.HIGH_SKILL)


        self.network            = network
        self.no_people          = people
        self.mean_skill         = mean_skill
        self.no_days            = no_days
        self.basic_spending     = basic_spending
        self.skill_sd           = skill_sd
        if not skill_sd:
            self.skill_sd       =  self.mean_skill/4
        self.education_cost     = education_cost
        
        self.people_skill       = np.random.normal(
                                        loc=self.mean_skill, 
                                        scale=self.skill_sd, 
                                        size=self.no_people)
                            

        
        self.pop                = []
        self.initial_coins      = initial_coins
        self.jobs               = list(np.random.normal(
                                        loc=self.mean_skill, 
                                        scale=self.skill_sd, 
                                        size=self.no_people))
        self.taxes_collected    = { '<LOW'    : [0,0],
                                    'LOW>MED' : [0,0],
                                    'MED>HIGH': [0,0],
                                    '>HIGH'   : [0,0] }
        self.total_tax           = 0

        self.welfare_provided   = { '<LOW'    : [0,0],
                                    'LOW>MED' : [0,0],
                                    'MED>HIGH': [0,0],
                                    '>HIGH'   : [0,0] }
        self.total_welfare      = 0

        self.total_wealth       = 0
        self.wealth_info        = { '<LOW'    : [0,0],
                                    'LOW>MED' : [0,0],
                                    'MED>HIGH': [0,0],
                                    '>HIGH'   : [0,0] }
        
    def genPopulation(self):
        #done at sim time to optimize distributed performance
        for i, slvl in enumerate(self.people_skill):
            self.pop.append(People(slvl, self.initial_coins))
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

    def plotSkillLevelvsJobs(self):
        count, bins, ignored = plt.hist(self.people_skill, 30)
        count, bins, ignored = plt.hist(self.jobs, 30)
        plt.show()
    

    def getAvgTax(self):
        avg_tax = []
        for value in self.taxes_collected.values():
            if value[0]:
                avg_tax.append(value[1]/value[0])
            else:
                avg_tax.append(0)
        return avg_tax

    def getAvgWelfare(self):
        avg_welfare = []
        for value in self.welfare_provided.values():
            if value[0]:
                avg_welfare.append(value[1]/value[0])
            else:
                avg_welfare.append(0)
        return avg_welfare
    
    def getAvgWealth(self):
        avg_wealth = []
        for value in self.wealth_info.values():
            if value[0]:
                avg_wealth.append(value[1]/value[0])
            else:
                avg_wealth.append(0)
        return avg_wealth

    def getWealthInfo(self):
        for person in self.pop:
            self.total_wealth += person.coins

            if person.skill_lvl <= self.LOW_SKILL:
                self.wealth_info['<LOW'][1] += person.coins
                self.wealth_info['<LOW'][0] += 1

            if person.skill_lvl > self.LOW_SKILL and person.skill_lvl <=  self.MED_SKILL:
                self.wealth_info['LOW>MED'][1] += person.coins
                self.wealth_info['LOW>MED'][0] += 1

            if person.skill_lvl > self.MED_SKILL and person.skill_lvl <= self.HIGH_SKILL:
                self.wealth_info['MED>HIGH'][1] += person.coins
                self.wealth_info['MED>HIGH'][0] += 1

            if person.skill_lvl > self.HIGH_SKILL:
                self.wealth_info['>HIGH'][1] += person.coins        
                self.wealth_info['>HIGH'][0] += 1     

        
    def collectTax(self, tax):
        self.total_tax += tax[0]

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


    def provideSocialWelfare(self, support_availed):
        if  support_availed:
            self.total_welfare += support_availed[0]

            if support_availed[1] <= self.LOW_SKILL:
                self.welfare_provided['<LOW'][1] += support_availed[0]
                self.welfare_provided['<LOW'][0] += 1

            if support_availed[1] > self.LOW_SKILL and support_availed[1] <=  self.MED_SKILL:
                self.welfare_provided['LOW>MED'][1] += support_availed[0]
                self.welfare_provided['LOW>MED'][0] += 1

            if support_availed[1] > self.MED_SKILL and support_availed[1] <= self.HIGH_SKILL:
                self.welfare_provided['MED>HIGH'][1] += support_availed[0]
                self.welfare_provided['MED>HIGH'][0] += 1

            if support_availed[1] > self.HIGH_SKILL:
                self.welfare_provided['>HIGH'][1] += support_availed[0]        
                self.welfare_provided['>HIGH'][0] += 1 
            

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

                self.provideSocialWelfare(person.spend(self.basic_spending))

                person.accquireSkill(self.education_cost, 2)

                person.dayEnd()
            
            self.genJobs(self.mean_skill, self.no_people)

        return score
    

    def getScores(self):
        coins = []
        skill_lvl = []
        
        
        for person in self.pop:
            skill_lvl.append(person.skill_lvl)
            coins.append(person.coins)
        
        print("Taxes ----------------------")
        print(self.taxes_collected)
        print(self.total_tax)
        print("Avg tax", self.getAvgTax(), "\n")
        

        print("Welfare ----------------------")
        print(self.welfare_provided)
        print(self.total_welfare)
        print("Avg welfare", self.getAvgWelfare(), "\n")

        print("Wealth ----------------------")
        self.getWealthInfo()
        print(self.total_wealth)
        print(self.wealth_info)
        print("Avg wealth", self.getAvgWealth(), "\n")

        print("Skill Level")
        print(np.array(skill_lvl))
        return None


if __name__ == "__main__":
    SIM_POP_SIZE            = 100
    SIM_MEAN_SKILL          = 50
    SIM_N_DAYS              = 1000
    SIM_SKILL_SD            = None
    SIM_BASIC_SPENDING      = 20
    SIM_EDUCATION_COST      = 50
    SIM_INITIAL_COINS       = 100

    env = Environment(  network         = None, 
                        people          = SIM_POP_SIZE, 
                        mean_skill      = SIM_MEAN_SKILL, 
                        no_days         = SIM_N_DAYS, 
                        basic_spending  = SIM_BASIC_SPENDING, 
                        skill_sd        = SIM_SKILL_SD,
                        education_cost  = SIM_EDUCATION_COST,
                        initial_coins   = SIM_INITIAL_COINS)

    starttime = time.time()
    env.runGov()
    print(f"Exec time : {time.time()-starttime}")
    print(env.getScores())
    env.plotSkillLevelvsJobs()