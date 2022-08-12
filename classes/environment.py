import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.stats import truncnorm
import sys, os
from numpy import exp
from sklearn import preprocessing
import colored
from colored import stylize, fg, bg, attr

sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from people import People
from utils.termColors import TermColors
#=====================================================================================
class Environment:
    def __init__(   self, 
                    network, 
                    args):
        # values obtained from percentile values of the distribution
        # now job level control  how much everyone gets paid
        # try incorporating inflation not hardcoded like % increase per year 
        # more dynamic like when money is printed
        # for india                             tax rate
        # under 200,000 is low income           0%
        # 200,000 - 500,000 is middle income    5% 
        # 500,000 - 10,00,000 is high income    12.5% averaged
        # > 10,00,000 above high income         25%


        self.LOW_SKILL          = 30
        self.MED_SKILL          = 50
        self.HIGH_SKILL         = 75

        INDIAN_APPROX           = (0.0, 0.10, 0.25, 0.50)
        ZERO                    = (0,0,0,0)
        INDIAN_APPROX_REV       = (0.5, 0.25, 0.10, 0.0)

        self.tax_rate           = INDIAN_APPROX_REV
        # FAQ
        # Why TF am i doing this exponent =====================================
        # Refer payTax and work funtion from People class
        # we are paying people the 10th of thier skill  which is raised to the expoenent 
        # we are using the same function to decide the tax bracket as with the same exponent 
        # so that there is the same funtio that decides pay and tax boundaries based upon our skill dist
        self.tax_bracket        = ( (self.LOW_SKILL/10) ** args["expo"], 
                                    (self.MED_SKILL/10) ** args["expo"], 
                                    (self.HIGH_SKILL/10)  ** args["expo"])


        self.network            = network
        self.no_people          = args["sim_pop_size"]
        self.mean_skill         = args["sim_mean_skill"]
        self.no_days            = args["sim_n_days"]
        self.basic_spending     = args["sim_basic_spending"]
        self.skill_sd           = args["sim_skill_sd"]
        if not args["sim_skill_sd"]:
            self.skill_sd       =  self.mean_skill/4
        self.education_cost     = args["sim_education_cost"]
        self.education_mult     = args["sim_education_mult"]
        self.expo = args["expo"]

        self.genObj              = truncnorm((0 - self.mean_skill)   / self.skill_sd, 
                                             (100 - self.mean_skill) / self.skill_sd, 
                                             loc=self.mean_skill, 
                                             scale=self.skill_sd)
        
        self.people_skill       = list(self.genObj.rvs(self.no_people))

        
        self.pop                = []
        self.initial_coins      = args["sim_initial_coins"]
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
        
        self.skill_distribution = { '<LOW'    : [0,0],
                                    'LOW>MED' : [0,0],
                                    'MED>HIGH': [0,0],
                                    '>HIGH'   : [0,0] }
        
    def genPopulation(self):
        #done at sim time to optimize distributed performance
        self.pop                = []
        for i, slvl in enumerate(self.people_skill):
            if slvl <= self.LOW_SKILL:
                self.skill_distribution['<LOW'][1] += slvl
                self.skill_distribution['<LOW'][0] += 1

            if slvl > self.LOW_SKILL and slvl <=  self.MED_SKILL:
                self.skill_distribution['LOW>MED'][1] += slvl
                self.skill_distribution['LOW>MED'][0] += 1

            if slvl > self.MED_SKILL and slvl <= self.HIGH_SKILL:
                self.skill_distribution['MED>HIGH'][1] += slvl
                self.skill_distribution['MED>HIGH'][0] += 1

            if slvl > self.HIGH_SKILL:
                self.skill_distribution['>HIGH'][1] += slvl      
                self.skill_distribution['>HIGH'][0] += 1 

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
        count, bins, ignored = plt.hist(self.people_skill, int(self.no_people*0.05 + 1))
        count, bins, ignored = plt.hist(self.jobs, int(self.no_people*0.05 + 1) )
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
        self.wealth_info= { '<LOW'    : [0,0],
                            'LOW>MED' : [0,0],
                            'MED>HIGH': [0,0],
                            '>HIGH'   : [0,0] }

        self.total_wealth = 0

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
            
    def evaluateGini(self, arr=None):
        # https://zhiyzuo.github.io/Plot-Lorenz/
        # higher is bad
        if not arr:
            arr = []
            for person in self.pop:
                arr.append(person.coins)
            
        arr = np.array(arr)
        sorted_arr = arr.copy()
        sorted_arr.sort()
        n = arr.size
        coef_ = 2. / n
        const_ = (n + 1.) / n
        weighted_sum = sum([(i+1)*yi for i, yi in enumerate(sorted_arr)])
        return  (coef_*weighted_sum/(sorted_arr.sum()) - const_)

    def plotLorenz(self, X):
        X = np.array(X)
        X_lorenz = X.cumsum() / X.sum()
        X_lorenz = np.insert(X_lorenz, 0, 0) 
        X_lorenz[0], X_lorenz[-1]
        fig, ax = plt.subplots(figsize=[6,6])
        ## scatter plot of Lorenz curve
        ax.scatter(np.arange(X_lorenz.size)/(X_lorenz.size-1), X_lorenz, 
                marker='.', color='red', s=10)
        ## line plot of equality
        ax.plot([0,1], [0,1], color='k')
        plt.show()

    def runGov(self, debug=False, test=False):
        self.genPopulation()

        # creating input vector =================================================
        if not debug:
            inputs = []
            for i, (k, v) in enumerate(self.skill_distribution.items()): 
                inputs.append(v[0])
            inputs.append(self.basic_spending/100)

        # creating output vector =================================================
            outputs = self.network.activate(inputs)
            e   = exp(outputs)
            sfm = e / e.sum()
            self.tax_rate = sfm
        
        if test:
            print(outputs)
            print(self.tax_rate)

        # optimize this loop
        for day in range(self.no_days):

            self.jobs.sort()
            self.pop.sort(key = lambda x : x.skill_lvl)
            for person in self.pop:

                if  person.work(self.jobs[0], self.expo):
                    del self.jobs[0]

                self.collectTax(person.payTax(self.tax_rate, self.tax_bracket))

                self.provideSocialWelfare(person.spend(self.basic_spending))

                person.accquireSkill(self.education_cost, self.education_mult)

                person.coins += person.wage
                person.worked = False
                # person.dayEnd()
            
            # self.genJobs(self.mean_skill, self.no_people)
            # make a function for job generation with different 
            # mean and SD
            
            self.jobs = list(self.genObj.rvs(self.no_people))
        
        # min max scale the tax vs welfare 
        # subtract tax from welfare
        # 0 = both are same
        # 1 = no welfare    [availed]
        # -1 = no tax       [collected]
        welfare_per = self.total_welfare/(self.total_tax + self.total_welfare)
        # one plus because when the % of welfare becomes low it will ignore gini index 
        # manage this somehow i ma leavinng this for future me

        self.getWealthInfo()
        avg_wealth_reci = (self.no_days * self.no_people)/(self.total_tax + self.total_wealth)
        # print(f"Gini:  {self.evaluateGini()}, Welfare % : {welfare_per}, Avg Wealth reci : {avg_wealth_reci}")
        # print(stylize((avg_wealth_reci), TermColors.danger))
        # print(f"{(self.no_days * self.no_people)} = {(self.total_tax + self.total_wealth, self.total_wealth, self.total_tax)} = {(1 + avg_wealth_reci)}")
        return (1 + self.evaluateGini()) * (1 + welfare_per) * (1 + avg_wealth_reci * 10)# have changes here to maximize tax+ wealth and minimize welfare

    

    def getScores(self):
        coins = []
        skill_lvl = []
        
        
        for person in self.pop:
            skill_lvl.append(person.skill_lvl)
            coins.append(person.coins)
        # print("Coins : ", coins)
        # print(stylize("Taxes ----------------------", TermColors.dangerHead ))
        # print(self.taxes_collected)
        # print(self.total_tax)
        # print("Avg tax", self.getAvgTax(), "\n")
        

        # print(stylize("Welfare ----------------------", TermColors.successHead))
        # print(self.welfare_provided)
        # print(self.total_welfare)
        # print("Avg welfare", self.getAvgWelfare(), "\n")

        # print(stylize("Wealth ----------------------", TermColors.warnHead))
        # print(self.total_wealth)
        # print(self.wealth_info)
        # print("Avg wealth", self.getAvgWealth(), "\n")

        # print(stylize("Skill Dist ----------------------", TermColors.infoHead))
        # print(self.skill_distribution)
        # for i, (k, v) in enumerate(self.skill_distribution.items()): 
        #     print(f"{k}      \t: {v[0]/self.no_people * 100}")

        # print(stylize("Welfare to tax ratio ------------------", TermColors.info))
        # print(self.total_welfare/ (self.total_tax + self.total_welfare))

        # print(stylize("Gini Index : " + str(self.evaluateGini(coins)), TermColors.success))
        # #self.plotLorenz(coins)

        # #print(stylize(f"Skill : {np.array(skill_lvl)}", TermColors.info))
        print("Skill dist ", self.skill_distribution.values());
        print("Taxes ", self.taxes_collected.values());
        print("TTaxes ", self.total_tax);
        print("Welfare ", self.welfare_provided.values());
        print("TWelfare ", self.total_welfare);
        print("Wealth ", self.wealth_info.values());
        print("TWealth ", self.total_wealth);
        return None


if __name__ == "__main__":
    EXPO                    = 1
    SIM_POP_SIZE            = 10
    SIM_MEAN_SKILL          = 50
    SIM_N_DAYS              = 300
    SIM_SKILL_SD            = 20
    SIM_BASIC_SPENDING      = (10/10) ** EXPO
    SIM_EDUCATION_COST      = (5/10) ** EXPO
    SIM_EDUCATION_MULT      = 1
    SIM_INITIAL_COINS       = 100
    starttime = time.time()

    # for future me change it to args 
    args = {"expo"              : EXPO,
            "sim_pop_size"      : SIM_POP_SIZE,
            "sim_mean_skill"    : SIM_MEAN_SKILL,
            "sim_n_days"        : SIM_N_DAYS,
            "sim_skill_sd"      : SIM_SKILL_SD,
            "sim_basic_spending": SIM_BASIC_SPENDING,
            "sim_education_cost": SIM_EDUCATION_COST,
            "sim_education_mult": SIM_EDUCATION_MULT,
            "sim_initial_coins" : SIM_INITIAL_COINS}

    env = Environment(  network     = None, 
                        args        = args )

    env.runGov(debug=True)
    print(stylize(f"Exec time : {time.time()-starttime} Seconds ", TermColors.infoHead))
    print(env.getScores())
    env.plotSkillLevelvsJobs()