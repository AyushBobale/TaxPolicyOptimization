#=====================================================================================
class People:
    def __init__(self, skill_lvl, coins = 0):
        self.skill_lvl          = skill_lvl
        self.coins              = coins
        self.wage               = 0

    
    def work(self, work_lvl, expo):
        # instead of linear scaling have exp
        if work_lvl > self.skill_lvl:
            self.worked = False
            self.wage = 0
            return self.worked

        self.worked = True
        self.wage = (work_lvl/10) ** expo
        return self.worked
    
    def payTax(self, tax_rate, tax_bracket):
        # Try doing it dynamically
        # progressive tax
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
        # acts as both spending function for basic needs
        # and avails social welfare
        
        if self.wage > basic_need:
            self.wage -= basic_need
            return 0

        support_needed  =  basic_need - self.wage 
        self.wage = 0
        
        return support_needed, self.skill_lvl

    def accquireSkill(self, cost, multiplier):
        
        # idea is that the lower level of skill one has 
        # the faster one can aqquire skill
        # less money it takes to acquire the skill 
        # points for consideration should debt be included
        

        if self.worked:
            return
        
        # could square the values
        calc_cost = cost * (self.skill_lvl/100) ** 2

        if self.coins > calc_cost:
            self.coins -= calc_cost
            # for eg [square can be changed with other scaler]
            # skill_lvl = 20
            # then 20/100 = 0.2
            # 0.2 ^ 2 = 0.04
            # 1 + 0.04 = 1.04
            # final skill = 20 * 1.04 = 2.08
            self.skill_lvl += multiplier/self.skill_lvl
            
            
        

    

    def dayEnd(self):
        self.coins += self.wage
        self.worked = False 
    

        




