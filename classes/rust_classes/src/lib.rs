
use pyo3::prelude::*;
//use std::collections::HashMap;
//use pyo3::types::PyTuple;
// =====================================================================

#[pyclass]
struct RustPeople {
    // remove getter and setter in final implenetation 
    #[pyo3(get,set)]
    coins       : f64, 
    #[pyo3(get,set)]
    skill_lvl   : f64,
    #[pyo3(get,set)]
    wage        : f64,
    #[pyo3(get,set)]
    worked      : bool,
}

#[pymethods]
impl RustPeople {
    #[new]
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
            tax = tax + ((self.wage - tax_bracket[1]) * tax_rate[2]);
        }

        if self.wage > tax_bracket[1] && self.wage <= tax_bracket[2]{
            tax = tax_bracket[0] * tax_rate[0];
            tax = tax + ((tax_bracket[1] - tax_bracket[0]) * tax_rate[1]);
            tax = tax + ((self.wage - tax_bracket[2]) * tax_rate[2]);
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
    // people_skill list to generate people based on this skill level

    pop             : Vec<RustPeople>,
    inttial_coins   : f64,
    // // jobs normal distribution
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

            tax_rate            : [0.0, 0.10, 0.25, 0.50],
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

            pop                 : Vec::with_capacity(sim_pop_size),

            inttial_coins       : sim_initial_coins,
            taxes_collected     : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_tax           : 0.0,
            welfare_provided    : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_welfare       : 0.0,
            wealth_info         : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            total_wealth        : 0.0,
            skill_dist          : [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],

        }
    }
}


// =====================================================================
/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_classes(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_class::<RustPeople>()?;
    Ok(())
}