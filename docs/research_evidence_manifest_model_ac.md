# Research evidence manifest — Model A+C

## Primary C (current production)

| Evidence item | Frozen result |
| --- | --- |
| Calibration partition | 25 cycles / 13 farmers |
| Final untouched holdout | 11 cycles / 6 farmers |
| Production parameter | `Y0_C = 50 kg/are` |
| Descriptive bootstrap interval | `[42.81, 55.78] kg/are` |
| Holdout MAE / RMSE / MedAE / Bias | `11.979091 / 15.990032 / 9.580000 / +7.306364 kg/are` |

C0 is the sole production and economics path. The interval is parameter uncertainty, not an individual-field prediction interval. No post-holdout retuning is permitted.

## Literature reference A (diagnostic only)

| Evidence item | Result |
| --- | --- |
| Source | Xiong et al. (2014) |
| General practical density range | `0–600 ducks/ha` (lower bound exclusive in runtime guard) |
| Literature duration domain | `50–80 days` |
| Local duration evidence | `28–40 days` |
| Density-compatible local records | `33/36` |
| Outside-density local records | `3/36` |
| Local records duration-compatible with Xiong | `0/36` |

The Xiong reference workbook also contains a specific example constraint with `d <= 650`, but the practical/general density range used for the validity guard is `0–600 ducks/ha`. This distinction is intentional and prevents treating the example constraint as the research-domain guard.

When the reference is inside its guard it is reported as `VALID_DOMAIN`; otherwise it is `OUTSIDE_LITERATURE_DOMAIN` with null reference values. Reference output and `literature_gap` are diagnostic only and never alter C0 yield, rice revenue, or cash contribution.
