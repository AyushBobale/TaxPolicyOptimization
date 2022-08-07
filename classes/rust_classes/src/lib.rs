
use pyo3::prelude::*;
use pyo3::types::PyTuple;
// =====================================================================

#[pyclass]
struct RustPeople {
    #[pyo3(get,set)]
    coins       : f64, 
    skill_lvl   : f64,
    wage        : f64,
    worked      : bool,
}

#[pymethods]
impl RustPeople {
    #[new]
    fn new(coins: f64, skill_lvl: f64) -> Self {
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