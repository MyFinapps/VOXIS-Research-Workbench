# VM.f2v canonical binding patch for EX-GRAMMAR-002A

**Binding version:** `0.2.1` → `0.2.2`  
**Reason:** validation defect `VD-001`  
**Frozen inventory SHA-256:** `735d9a58ab0305048617ffa20d99c2f86826e5863f7f0355eacd476740d810d7`

The canonical `VM.f2v.upper_stem_axis` geometry is replaced by accepted Stage A candidate `S1`, and `VM.f2v.central_y` is replaced by accepted Stage A candidate `Y1`. The superseded coordinates remain recorded in each entity's `binding_correction` payload and in binding version `0.2.1` history.

Accepted candidates `S2`, `S3`, and `Y2` are added as new canonical entities. This patch changes annotation geometry and inventory only. It does not validate any pairwise relation, grammar, function, intent, or meaning claim.
