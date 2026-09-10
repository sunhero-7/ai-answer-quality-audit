# Draft task and reference checks — 10 September 2026

Prepared 16 original provisional tasks: MP03–MP10 and PR03–PR10. Every task uses version 0.1 and stage `main_draft`; every reference uses version 0.1 and retains `pending_dominic`. These files contain reference keys, not candidate generations or annotation decisions.

All factual inputs are stated inside each original prompt. Calculations use supplied definitions and unit conversions, and the practical tasks use fictional constraints, products and schedules. No live external facts or sources are required.

The script `verify.py` recomputes each numerical result or constraint example using exact fractions, exhaustive finite enumeration or an independent rule implementation. It passed on 10 September 2026. Run it with `python3 verify.py` from this directory, or provide its full path. `build.py` recreates the two JSON files.

| Task | Substantive verification |
| --- | --- |
| MP03 | Exact fractional multipliers independently give 200 kWh, 240 kWh and a 4% decrease relative to the original 250 kWh. |
| MP04 | Weighted sums confirm the formula; solving the equality gives n = 12. A four-person Group B provides the counterexample 8.75 minutes. |
| MP05 | Signed velocity difference is −3 m/s, yielding average acceleration −12 m/s² and average force −6 N. Both point west by the supplied sign convention. |
| MP06 | Power × time gives 60 and 64 Wh; independent conversions give 0.060/0.064 kWh and a difference of 14,400 J. |
| MP07 | Multiplying converted SI lengths agrees with cubic conversion: 60 cm³ = 6 × 10⁻⁵ m³. Density agrees in both unit systems: 3 g/cm³ = 3,000 kg/m³. |
| MP08 | All 15 unordered counter pairs were enumerated; six are blue-blue. This confirms 40% and the complementary 60%. |
| MP09 | Exact heat calculations give rises of 2°C and 1°C. An explicit unequal-start counterexample disproves the unconditional final-temperature ordering. |
| MP10 | Exact endpoint arithmetic gives [11.5, 12.5) m. Included lower inputs attain the lower mean; excluded upper inputs cannot attain the upper mean. The key's shared-offset construction establishes every intermediate mean. |
| PR03 | All five durations, dependencies, printer window, fixed delivery interval and workday bounds pass. Pairwise checks confirm no attention-requiring activities overlap; automatic printing may overlap as expressly permitted. |
| PR04 | Two one-shift helpers cannot cover three shifts. The repaired Asha/Ben/Asha rota preserves availability and adds exactly one permitted Asha shift. A single additional helper on either outer shift is also a valid repair family. |
| PR05 | All 20 possible three-item first boxes were enumerated. Only AEF/BCD satisfies the constraints, apart from swapping box labels; masses are 10/12 kg. |
| PR06 | All nine shuttle/train pairs were examined. Only S1–T2 meets the transfer and arrival limits, with a 25-minute wait and 10:15 arrival. |
| PR07 | A separate scheduler that re-evaluates readiness and priority after each finish produces J2, J3, J1, J4 and finishes at 09:50. |
| PR08 | An eligibility check that keeps unknown separate from false confirms Arden, preserves Bracken as uncertain, and rejects Clover/Dune for their stated failures. |
| PR09 | Exact ceiling arithmetic gives pack counts 3/2/2 and leftovers 3/16/3. One fewer pack of each supply fails, establishing minimality. |
| PR10 | Independent UTC conversion finds original overlap 09:45–10:00. Enumeration checks every 0–15 whole-minute extension; the linear overlap expression 15 + x also rules out fractional extensions below 15 minutes. Local call times convert back correctly. |

Structural checks also passed for 16 unique matching task/reference IDs, required fields, substantive checklists/evidence, draft versions/statuses, and word limits on the reference prose for MP04, MP09, PR04 and PR08. Other expected answers specify structures or display working; their checklists identify the actual response requirements. Every key explicitly permits equivalent correct reasoning or answers where relevant, rather than requiring an exact string match.

Limits: these are AI-authored materials and AI-assisted verification, not Dominic's independent verification or annotation. Manual editorial checks and executable arithmetic reduce key risk but cannot establish how consistently a person will interpret the rubric. The tasks remain provisional pending pilot feedback. No candidate outputs, scores, corrections, human hours or completed reviews have been invented. The same drafting agent performed this verification; a separate reviewer should not be claimed from this file alone.
