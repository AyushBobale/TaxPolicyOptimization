
use pyo3::prelude::*;
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