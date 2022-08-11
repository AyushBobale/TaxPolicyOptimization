
use pyo3::prelude::*;
use rand::distributions::{Normal, Distribution};
//use std::collections::HashMap;
//use pyo3::types::PyTuple;
// =====================================================================
// TODO 
// Remove PyO3 decorators from the RustPeople struct after completion of Rust Env
// get correct values for the final output of run gov
// code clean up optimizations


struct RustPeople {
    coins       : f64, 
    skill_lvl   : f64,
    wage        : f64,
    worked      : bool,
}

impl RustPeople {
    fn new(skill_lvl: f64, coins: f64) -> Self {
        RustPeople{ coins       : coins, 
                    skill_lvl   : skill_lvl,
                    wage        : 0.0,
                    worked      : false }
    }

    fn work(&mut self, work_lvl: f64, expo: f64) -> bool {

        if work_lvl > self.skill_lvl {
            self.worked = false;
            self.wage = 0.0;
            return false;
        }

        self.worked = true;
        self.wage = f64::powf(work_lvl/10.0, expo);

        return true;
    }

    fn payTax(&mut self, tax_rate: [f64; 4], tax_bracket: [f64; 3]) -> [f64; 2] {

        let wage_before_tax = self.wage;
        let mut tax: f64 = 0.0;
        
        if self.wage <= tax_bracket[0]{
            tax = self.wage * tax_rate[0];
        }

        if self.wage > tax_bracket[0] &&  self.wage <= tax_bracket[1]{
            tax = tax_bracket[0] * tax_rate[0];
            tax = tax + ((self.wage - tax_bracket[0]) * tax_rate[2]);
        }

        if self.wage > tax_bracket[1] && self.wage <= tax_bracket[2]{
            tax = tax_bracket[0] * tax_rate[0];
            tax = tax + ((tax_bracket[1] - tax_bracket[0]) * tax_rate[1]);
            tax = tax + ((self.wage - tax_bracket[1]) * tax_rate[2]);
        }

        if self.wage > tax_bracket[2]{
            tax = tax_bracket[0] * tax_rate[0];
            tax = tax + ((tax_bracket[1] - tax_bracket[0]) * tax_rate[1]);
            tax = tax + ((tax_bracket[2] - tax_bracket[1]) * tax_rate[2]);
            tax = tax + ((self.wage - tax_bracket[2]) * tax_rate[3]);
        }

        self.wage = self.wage - tax;
        return [tax , wage_before_tax];

    }

    fn spend(&mut self, basic_need: f64) -> [f64; 2] {

        if self.wage > basic_need{
            self.wage = self.wage - basic_need;
            return [0.0, self.skill_lvl];
        }

        let support_needed = basic_need - self.wage;
        self.wage = 0.0;

        return [support_needed, self.skill_lvl];
    }

    fn accquireSkill(&mut self, cost: f64, multiplier: f64) -> f64{
        if self.worked{
            return 0.0;
        }

        let calc_cost = cost * f64::powf(self.skill_lvl/100.0, 2.0);

        if self.coins > calc_cost{
            self.coins = self.coins - calc_cost;
            self.skill_lvl = self.skill_lvl + multiplier/self.skill_lvl;
            return 1.0;
        }

        return 0.5;
    }

    fn dayEnd(&mut self){
        self.coins = self.coins + self.wage;
        self.worked = false;
    }
}
// =====================================================================
/* 
would need an initailzation stage
where we get some constant vars for intialization
*/


#[pyclass]
struct RustEnvironment {
    // remove getter and setter in final implenetation 
    LOW_SKILL       : f64,  
    MED_SKILL       : f64,   
    HIGH_SKILL      : f64,  
    
    tax_rate        : [f64; 4],
    tax_bracket     : [f64; 3],

    no_people       : usize,
    mean_skill      : f64,
    no_days         : usize,
    basic_spending  : f64,
    skill_sd        : f64,
    education_cost  : f64,
    education_mult  : f64,
    expo            : f64,

    // genObj creates a genrater for normal distrubution with cut offs 
    genObj          : Normal,
    people_skill    : Vec<f64>,

    pop             : Vec<RustPeople>,
    inttial_coins   : f64,
    jobs            : Vec<f64>,

    /*
    1 - <LOW
    2 - LOW>MED
    3 - MED>HIGH
    4 - >HIGH
    */
    // array implementation
    taxes_collected : [[f64; 2]; 4],
    total_tax       : f64,
    welfare_provided: [[f64; 2]; 4],
    total_welfare   : f64,
    wealth_info     : [[f64; 2]; 4],
    total_wealth    : f64,
    skill_dist      : [[f64; 2]; 4],

}


#[pymethods]
impl RustEnvironment {

    #[new]
    fn new( expo                : f64, 
            sim_pop_size        : usize,
            sim_mean_skill      : f64,
            sim_n_days          : usize,
            sim_skill_sd        : f64,
            sim_basic_spending  : f64,
            sim_education_cost  : f64,
            sim_education_mult  : f64,
            sim_initial_coins   : f64
            ) -> Self {
        RustEnvironment{
            LOW_SKILL           : 30.0,
            MED_SKILL           : 50.0,
            HIGH_SKILL          : 75.0,

            tax_rate            : [0.05, 0.05, 0.05, 0.05],
            tax_bracket         : [ f64::powf(30.0/10.0, expo),
                                    f64::powf(50.0/10.0, expo),
                                    f64::powf(75.0/10.0, expo)],
            
            // Network how to get values to be discussed
            // network = [f64; 4];

            no_people           : sim_pop_size,
            mean_skill          : sim_mean_skill,
            no_days             : sim_n_days,
            basic_spending      : sim_basic_spending,
            skill_sd            : sim_skill_sd,
            education_cost      : sim_education_cost,
            education_mult      : sim_education_mult,
            expo                : expo,

            // genrator obj for generating distribution
            genObj              : Normal::new(sim_mean_skill, sim_skill_sd),
            people_skill        : Vec::<f64>::with_capacity(sim_pop_size),

            pop                 : Vec::<RustPeople>::with_capacity(sim_pop_size),
            inttial_coins       : sim_initial_coins,
            jobs                : Vec::<f64>::with_capacity(sim_pop_size),

            taxes_collected     : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_tax           : 0.0,
            welfare_provided    : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_welfare       : 0.0,
            wealth_info         : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_wealth        : 0.0,
            skill_dist          : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],

        }
    }

    fn genPopulation(&mut self) {
        self.pop = Vec::<RustPeople>::with_capacity(self.no_people);

        while self.pop.len() < self.no_people{

            let slvl = self.genObj.sample(&mut rand::thread_rng());

            if slvl >= 0.0 && slvl < self.LOW_SKILL{

                self.skill_dist[0][1] = self.skill_dist[0][1] + slvl;
                self.skill_dist[0][0] = self.skill_dist[0][0] + 1.0;
                self.pop.push( RustPeople{  skill_lvl   : slvl, 
                                            coins       : self.inttial_coins,
                                            wage        : 0.0,
                                            worked      : false} );
            }
            if slvl >= self.LOW_SKILL && slvl < self.MED_SKILL{

                self.skill_dist[1][1] = self.skill_dist[1][1] + slvl;
                self.skill_dist[1][0] = self.skill_dist[1][0] + 1.0;
                self.pop.push( RustPeople{  skill_lvl   : slvl, 
                                            coins       : self.inttial_coins,
                                            wage        : 0.0,
                                            worked      : false} );
            }
            if slvl >= self.MED_SKILL && slvl < self.HIGH_SKILL{

                self.skill_dist[2][1] = self.skill_dist[2][1] + slvl;
                self.skill_dist[2][0] = self.skill_dist[2][0] + 1.0;
                self.pop.push( RustPeople{  skill_lvl   : slvl, 
                                            coins       : self.inttial_coins,
                                            wage        : 0.0,
                                            worked      : false} );
            }
            if slvl >= self.HIGH_SKILL && slvl <= 100.0{

                self.skill_dist[3][1] = self.skill_dist[3][1] + slvl;
                self.skill_dist[3][0] = self.skill_dist[3][0] + 1.0;
                self.pop.push( RustPeople{  skill_lvl   : slvl, 
                                            coins       : self.inttial_coins,
                                            wage        : 0.0,
                                            worked      : false} );
            }
        }
        
    }

    fn genJobs(&mut self, mean_skill: f64, no_jobs: usize, skill_sd: f64){
        while self.jobs.len() < no_jobs{
            let jlvl = self.genObj.sample(&mut rand::thread_rng());
            if jlvl >= 0.0 &&  jlvl <= 100.0{
                self.jobs.push(jlvl)
            }
        }
    }

/*
    fn collectTax(&mut self, tax: [f64; 2]){
        self.total_tax = self.total_tax + tax[0];

        if tax[1] <= self.LOW_SKILL {
            self.taxes_collected[0][1] = self.taxes_collected[0][1] + tax[0];
            self.taxes_collected[0][0] = self.taxes_collected[0][0] + 1.0;
        }
        if tax[1] > self.LOW_SKILL  && tax[1] <= self.MED_SKILL {
            self.taxes_collected[1][1] = self.taxes_collected[1][1] + tax[0];
            self.taxes_collected[1][0] = self.taxes_collected[1][0] + 1.0;
        }
        if tax[1] > self.MED_SKILL  && tax[1] <= self.HIGH_SKILL {
            self.taxes_collected[2][1] = self.taxes_collected[2][1] + tax[0];
            self.taxes_collected[2][0] = self.taxes_collected[2][0] + 1.0;
        }
        if tax[1] > self.HIGH_SKILL {
            self.taxes_collected[3][1] = self.taxes_collected[3][1] + tax[0];
            self.taxes_collected[3][0] = self.taxes_collected[3][0] + 1.0;
        }

    }

    fn provideSocialWelfare(&mut self, support_availed: [f64; 2]){
        if support_availed[0] > 0.0 {
            self.total_welfare = self.total_welfare + support_availed[0];

            if support_availed[1] <= self.LOW_SKILL{
                self.welfare_provided[0][1] = self.welfare_provided[0][1] + support_availed[0];
                self.welfare_provided[0][0] = self.welfare_provided[0][0] + 1.0;
            }
            if support_availed[1] > self.LOW_SKILL &&  support_availed[1] <= self.MED_SKILL {
                self.welfare_provided[1][1] = self.welfare_provided[1][1] + support_availed[0];
                self.welfare_provided[1][0] = self.welfare_provided[1][0] + 1.0;
            }
            if support_availed[1] > self.MED_SKILL &&  support_availed[1] <= self.HIGH_SKILL {
                self.welfare_provided[2][1] = self.welfare_provided[2][1] + support_availed[0];
                self.welfare_provided[2][0] = self.welfare_provided[2][0] + 1.0;
            }
            if support_availed[1] > self.HIGH_SKILL {
                self.welfare_provided[3][1] = self.welfare_provided[3][1] + support_availed[0];
                self.welfare_provided[3][0] = self.welfare_provided[3][0] + 1.0;
            }
        }
    }
*/

    fn getWealthInfo(&mut self){
        self.wealth_info = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]];
        self.total_wealth = 0.0;

        for person in &mut self.pop{
            self.total_wealth = self.total_wealth + person.coins;
            if person.skill_lvl <= self.LOW_SKILL{
                self.wealth_info[0][1] = self.wealth_info[0][1] + person.coins;
                self.wealth_info[0][0] = self.wealth_info[0][0] + 1.0;
            }
            if person.skill_lvl > self.LOW_SKILL && person.skill_lvl <= self.MED_SKILL{
                self.wealth_info[1][1] = self.wealth_info[1][1] + person.coins;
                self.wealth_info[1][0] = self.wealth_info[1][0] + 1.0;
            }
            if person.skill_lvl > self.MED_SKILL && person.skill_lvl <= self.HIGH_SKILL{
                self.wealth_info[2][1] = self.wealth_info[2][1] + person.coins;
                self.wealth_info[2][0] = self.wealth_info[2][0] + 1.0;
            }
            if person.skill_lvl > self.HIGH_SKILL{
                self.wealth_info[3][1] = self.wealth_info[3][1] + person.coins;
                self.wealth_info[3][0] = self.wealth_info[3][0] + 1.0;
            }
        }
    }

    fn evaluateGini(&mut self) -> f64 {
        let mut coins : Vec<f64> = Vec::with_capacity(self.no_people); 
        for person in &mut self.pop{
            coins.push(person.coins);
        }
        coins.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let n = coins.len();
        let coef = 2.0 / n as f64;
        let const_ = (n as f64 + 1.0)/n as f64;
        let mut weighted_sum = 0.0;
        for i in 0..n{
            weighted_sum = weighted_sum + ((i as f64 + 1.0) * coins[i]);
        }
        return  coef * weighted_sum/coins.iter().sum::<f64>() - const_;
    }

    fn runGov(&mut self) -> f64 {
        self.genPopulation();
        self.genJobs(self.mean_skill, self.no_people, self.skill_sd);

        for day in 0..self.no_days{
            self.jobs.sort_by(|a, b| a.partial_cmp(b).unwrap());
            self.pop.sort_by(|a, b| a.skill_lvl.partial_cmp(&b.skill_lvl).unwrap());

            for person in &mut self.pop{
                if person.work(self.jobs[0], self.expo){
                    self.jobs.remove(0);
                }

                // self.collectTax(person.payTax(self.tax_rate, self.tax_bracket));
                // Learn how to implemnet
                // ===================================================================================
                let tax = person.payTax(self.tax_rate, self.tax_bracket);
                self.total_tax = self.total_tax + tax[0];
                if tax[1] <= self.LOW_SKILL {
                    self.taxes_collected[0][1] = self.taxes_collected[0][1] + tax[0];
                    self.taxes_collected[0][0] = self.taxes_collected[0][0] + 1.0;
                }
                if tax[1] > self.LOW_SKILL  && tax[1] <= self.MED_SKILL {
                    self.taxes_collected[1][1] = self.taxes_collected[1][1] + tax[0];
                    self.taxes_collected[1][0] = self.taxes_collected[1][0] + 1.0;
                }
                if tax[1] > self.MED_SKILL  && tax[1] <= self.HIGH_SKILL {
                    self.taxes_collected[2][1] = self.taxes_collected[2][1] + tax[0];
                    self.taxes_collected[2][0] = self.taxes_collected[2][0] + 1.0;
                }
                if tax[1] > self.HIGH_SKILL {
                    self.taxes_collected[3][1] = self.taxes_collected[3][1] + tax[0];
                    self.taxes_collected[3][0] = self.taxes_collected[3][0] + 1.0;
                }
                // ===================================================================================
                // self.provideSocialWelfare(person.spend(self.basic_spending))
                let support_availed = person.spend(self.basic_spending);
                if support_availed[0] > 0.0 {
                    self.total_welfare = self.total_welfare + support_availed[0];
        
                    if support_availed[1] <= self.LOW_SKILL{
                        self.welfare_provided[0][1] = self.welfare_provided[0][1] + support_availed[0];
                        self.welfare_provided[0][0] = self.welfare_provided[0][0] + 1.0;
                    }
                    if support_availed[1] > self.LOW_SKILL &&  support_availed[1] <= self.MED_SKILL {
                        self.welfare_provided[1][1] = self.welfare_provided[1][1] + support_availed[0];
                        self.welfare_provided[1][0] = self.welfare_provided[1][0] + 1.0;
                    }
                    if support_availed[1] > self.MED_SKILL &&  support_availed[1] <= self.HIGH_SKILL {
                        self.welfare_provided[2][1] = self.welfare_provided[2][1] + support_availed[0];
                        self.welfare_provided[2][0] = self.welfare_provided[2][0] + 1.0;
                    }
                    if support_availed[1] > self.HIGH_SKILL {
                        self.welfare_provided[3][1] = self.welfare_provided[3][1] + support_availed[0];
                        self.welfare_provided[3][0] = self.welfare_provided[3][0] + 1.0;
                    }
                }
                // ===================================================================================

                person.accquireSkill(self.education_cost, self.education_mult);
                person.coins = person.coins + person.wage;
                person.worked = false;
            }

            self.genJobs(self.mean_skill, self.no_people, self.skill_sd);
        }

        self.getWealthInfo();
        let welfare_per = self.total_welfare / (self.total_tax + self.total_welfare);
        let avg_wealth_reci = (self.no_days * self.no_people) as f64/(self.total_tax + self.total_wealth);
        let final_val = (1.0 + self.evaluateGini()) * (1.0 + welfare_per) * (1.0 + 10.0 * avg_wealth_reci);

        println!("Gini : {}, Welfare % : {}, Avg wealth reci :  {}", self.evaluateGini(), welfare_per, avg_wealth_reci );
        return final_val
    }

    fn getScores(&mut self) {
        for person in &self.pop{
            //println!("{}, {}", person.skill_lvl, person.coins);
        }
        
        println!("Skill dist {:?}", self.skill_dist);
        println!("Taxes {:?}", self.taxes_collected);
        println!("TTaxes {:?}", self.total_tax);
        println!("Welfare {:?}", self.welfare_provided);
        println!("TWelfare {:?}", self.total_welfare);
        println!("Wealth {:?}", self.wealth_info);
        println!("TWealth {:?}", self.total_wealth);
        //println!("{:?}", self.jobs)
    }
}


// =====================================================================
/// A Python module implemented in Rust.

#[pymodule]
fn rust_classes(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustEnvironment>()?;
    Ok(())
}