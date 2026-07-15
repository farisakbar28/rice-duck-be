# BACKEND_GRAPH_PLAN.md

## A. API Endpoint & DTO Design

New endpoint `POST /api/v1/dss/visualize` provides read-only mathematical curves. (POST used to accept DSSSimulationRequest payload for financial breakdown).

### DTOs (app/schemas/dss.py)
```python
from typing import List
from pydantic import BaseModel

class Point(BaseModel):
    x: float
    y: float

class DensitySeries(BaseModel):
    density_bio: List[Point] # x: d, y: F_density_bio
    k_safe_jarwo: float = 4.0
    k_safe_tegel: float = 3.0
    k_max: float = 8.0

class AgeSeries(BaseModel):
    r_age: List[Point] # x: U_duck, y: R_age
    lambda_eff: List[Point] # x: U_duck, y: lambda_eff (assuming p_over=0)

class FinanceBreakdown(BaseModel):
    core_validated_liquid_cash: float
    empirically_uncorrelated_isolated_shadow_costs: float

class VisualizationResponse(BaseModel):
    density_jarwo: DensitySeries
    density_tegel: DensitySeries
    age_vulnerability: AgeSeries
    finance_breakdown: FinanceBreakdown
```

## B. Mathematical Service Integration

Add `get_visualization_series(payload: DSSSimulationRequest) -> VisualizationResponse` to `DSSService` (`app/services/simulation_service.py`).

1. **Density Curve (F_density_bio)**:
   - Loop `d` from 0.0 to 10.0 (step 0.2).
   - Use internal math logic isolated from `compute_yield_components` to avoid regression and extract `F_density_bio` cleanly:
     ```python
     def calc_f_density(d_val: float) -> float:
         # alpha_bio=0.15, k_opt=4.0, beta_tramp=0.25, k_max=8.0
         d_dec = Decimal(str(d_val))
         exp_term = _dec_exp(-d_dec / Decimal("4.0"))
         boost = Decimal("0.15") * (Decimal("1") - exp_term)
         penalty_base = max(Decimal("0"), (d_dec - Decimal("8.0")) / Decimal("8.0"))
         penalty = Decimal("0.25") * (penalty_base ** 2)
         return float(Decimal("1") + boost - penalty)
     ```
   - Build X, Y points for Jarwo and Tegel (F_sys doesn't change F_density_bio directly in the formula provided, but keep structures separate if F_sys scaling applies later).

2. **Age Vulnerability Curve (R_age & lambda_eff)**:
   - Loop `U_duck` from 1 to 45 (step 1).
   - Call `compute_duck_age_status(U_duck)`. Extract `R_age`.
   - Call `compute_surviving_ducks(duck_count=10000, r_age=float(R_age), p_over=0.0)`. Divide result by 10000 to get `lambda_eff` ratio.
   - Cast all Decimal results to `float`.

3. **Financial Breakdown**:
   - Run standard simulation `self.simulate(payload)` (or equivalent core run).
   - Core Validated = `actual.cost_total_cash`.
   - Isolated Shadow Costs = sum of `actual.cost_weed_isolated`, `actual.cost_pest_isolated`, `actual.cost_labor_isolated`, `actual.cost_infra_isolated`, `actual.cost_feed_isolated`, `actual.cost_fert_isolated`.

## C. Step-by-Step Execution Plan

1. **Schema Update**: Add `Point`, `DensitySeries`, `AgeSeries`, `FinanceBreakdown`, and `VisualizationResponse` DTOs to `app/schemas/dss.py`.
2. **Service Method**: Add `get_visualization_series(self, payload: DSSSimulationRequest) -> VisualizationResponse` to `DSSService`.
3. **Loop Logic**: Implement the loops (d: 0..10, U_duck: 1..45) inside the new service method. Convert all Decimal to float before assigning to DTOs.
4. **Financial Call**: Invoke the existing simulation method within `get_visualization_series` to pull the financial numbers.
5. **Router Update**: Add `@router.post("/visualize")` in `app/api/routes/dss.py` pointing to the new service method.
6. **Validation**: Run `pytest` to confirm 44/44 tests still pass. Add a basic sanity test for `/visualize`.
