#=====================================================================================
# write function for max edge
# it will define how much one can get extra pay for the extra skill at each job lvl
class People:
    def __init__(self, skill_lvl):
        self.skill_lvl          = skill_lvl
        self.coins              = 0
        self.wage               = 0

        # deprecated
        # self.base_wage          = 10 should be dependent on job level
        # point to be considered base wage should be such that 
        # higher skill person should almost always earn more doing a higher skill job 
        # than getting a better edge in lower skill job
    
    def work(self, work_lvl):
        # alternative implenetation
        # if skill lvl satifies a higher job 
        # and higher lvl job available 
        # work higher lvl job
        # pay = job level/work level

        if work_lvl > self.skill_lvl:
            self.worked = False
            self.wage = 0
            return self.worked

        self.worked = True
        self.wage = work_lvl
        self.coins += self.wage 
        return self.worked
    
    def payTax(self):
        pass
    
    def spend(self):
        pass

    def accquireSkill(self):
        pass
    
    def availSocialWelfare(self):
        pass

    def dayEnd(self):
        self.worked = False 
    

        




