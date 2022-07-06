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
* Environment 
    * has people with random inital skill level [with appropriate distribution of skill level people]
    * like 10% high skill, 30% med skill, 60% lew level
    * people from any class can avail any work it just changes their productivity [prod cannot go beyond 100%]
    * [Skill Distribution](https://www.thehindu.com/business/Economy/skill-levels-of-indian-workforce/article24035708.ece)

    * ![Skill Dist](/imgs/skill-dist.png "Image")

    * Total productivity is the function of sum of skill level of all people
    * Over time people can increase their skill level
    * coins will be alloted for work done
    * coins will be deducted for goods
    * coins will be deducted for tax
    * remaining coins will be considered as wealth
    * agents can avail social welfare
    * product flow from low level to high level
    * higher skill income is earned only and only when lower skill people work [their income is a function of lower income level work]
    * 

### people class

    skill level = number [from 1-100]
    productivity = derived value [function of skill level and job level]

* Agent

    * optimizes productivity * equality 
    * Equality is the happines measure
    * productivity [total bread produced]
    * equality [how much bread can one buy with thier wealth/coins]
    * depending on the state of the env
    * agent changes taxation 
    * and social welfare
    * over time agent should maximize 
    
