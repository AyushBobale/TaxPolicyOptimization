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
        return self.worked
    
    def payTax(self, tax_rate, tax_bracket):
        # Try doing it dynamically
        wage_before_tax = self.wage

        if self.wage <= tax_bracket[0]:
            tax = self.wage * tax_rate[0]

        if self.wage > tax_bracket[0] and self.wage <= tax_bracket[1]:
            tax = (tax_bracket[0] * tax_rate[0])  
            tax += (self.wage - tax_bracket[0]) * tax_rate[1]
        
        if self.wage > tax_bracket[1] and self.wage <= tax_bracket[2]:
            tax = (tax_bracket[0] * tax_rate[0])  
            tax += (tax_bracket[1] - tax_bracket[0]) * tax_rate[1]
            tax += (self.wage - tax_bracket[1]) * tax_rate[2]

        if self.wage > tax_bracket[2]:
            tax = (tax_bracket[0] * tax_rate[0])  
            tax += (tax_bracket[1] - tax_bracket[0]) * tax_rate[1]
            tax += (tax_bracket[2] - tax_bracket[1]) * tax_rate[2]
            tax += (self.wage - tax_bracket[2]) * tax_rate[3]
        
        self.wage -= tax
        return tax, wage_before_tax
    
    def spend(self, basic_need):
        
        if self.wage > basic_need:
            self.wage -= basic_need
            return 0

        support_needed  =  basic_need - self.wage 
        self.wage = 0
        
        return support_needed, self.skill_lvl

    def accquireSkill(self):
        pass
    
    def availSocialWelfare(self):
        pass

    def dayEnd(self):
        self.coins += self.wage
        self.worked = False 
    

        




