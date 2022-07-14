# Tax policy Sim

## Actors 
     Government [our agent]
     Population [observable environment]
        Lower skill [labor jobs]
        Middle skill [general professions]
        High skill [specialized professionals/business owners]

## Basic requirements in a functional economy [yet to be considered for simulation]
    Food / Basic bag of goods []
    Shelter
    Medical Support [can be privatized or social welfare]
    Education [for skill enhancement and growing into the class above]

## Scenario lets say 
    All people work in the industry of food production.
        Low skill [work on fields do manual labor]
        Middle skill [work in management and coordination]
        High skill [work as business owner / scientist ]
    
## Say they harvest a imaginary tree that grows bread
    Workers collect that bread and bring it to the processing plant
    Managers manage the workers and optimize the workforce
    Scientist / business owners work on improving the product


## How can we model it
***
* Environment 
    * has people with random inital skill level [with appropriate distribution of skill level people]
    * like 10% high skill, 30% med skill, 60% lew level
    * people from any class can avail any work it just changes their productivity [prod cannot go beyond 100%]
    * [Skill Distribution](https://www.thehindu.com/business/Economy/skill-levels-of-indian-workforce/article24035708.ece)

    * ![SkillDist](https://github.com/AyushBobale/TaxPolicyOptimization/blob/main/imgs/skill-dist.PNG?raw=True)

    * Total productivity is the function of sum of skill level of all people
    * Over time people can increase their skill level
    * coins will be alloted for work done
    * coins will be deducted for goods
    * coins will be deducted for tax
    * remaining coins will be considered as wealth
    * agents can avail social welfare
    * product flow from low level to high level
    * higher skill income is earned only and only when lower skill people work [their income is a function of lower income level work]
***
* Agent

    * optimizes productivity * equality 
    * Equality is the happines measure
    * productivity [total bread produced]
    * equality [how much bread can one buy with thier wealth/coins]
    * depending on the state of the env
    * agent changes taxation 
    * and social welfare
    * over time agent should maximize 
***
* Simulation
    * Get a input for taxation thats is or control var
    * the gov runs for specific no of days
    * at the end of the days metrics are calculated
    * score is given i.e gini index
    * such multiple envs are intantiated with differnt genomes i.e agents 
    * and optimization is performed 

***
* TODO
    * People Class
        * based on job level have a min_wage
        * inside work function have tolerance for lower skill workers working higher skill jobs
        * based on earned wage cut taxes
        * write function for basic need spending
        * write a function for increasing skill [shall use coins and cannot be done if already worked]
        * write function to avail social welfare
        * finaliser function resets and day-to-day values [ dayEnd ]

    * Environment class 
        * optimize genJobs function to accout for variability
        * job matching function
        * such that it almost always optimally matches people with proper skill level


***

## Points for documentation
    Points of consideration for the simulation that are differnt from real world

    why gentic algorithm and not any other ? 
        - due to high variablility, no of params, chaotic nature, search space
