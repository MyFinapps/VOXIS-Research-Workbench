# EX-GRAMMAR-002A — Stage B deterministic computation specification

**Specified before Stage B execution:** yes  
**Frozen inventory SHA-256:** `735d9a58ab0305048617ffa20d99c2f86826e5863f7f0355eacd476740d810d7`

The runner must refuse execution if the frozen inventory hash differs. It measures the complete Cartesian product of the three accepted STEM actors and two accepted Y targets using `measure_point`, identity geometry, and tolerance `0.03`.

Ranking is by ascending `target_distance`; smaller is better. Ties use competition rank. The reported distance percentile is the percentage of all opportunity distances less than or equal to the indexed distance. The within-stem next-best difference is `second-smallest distance - indexed distance`; a negative value therefore means that another target is closer for the indexed stem.

Summary means use the arithmetic mean. Medians use the ordinary midpoint convention for even counts. No inferential population-significance test is performed.
