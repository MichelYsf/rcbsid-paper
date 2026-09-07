# findings_ecod_composition — batch content at fixed size and fixed model

Generating run: `ecod_batch_composition_20260907T061817_7d2ec490`. Every number is a provenance macro.

Model: ECOD fitted on the timestamp arm's benign-only training rows, the same fit repeated identically for each batch. Evaluated: the 78000 records both arms hold out, in natural-position order. Batches: the timestamp-order held-out slice and the day-round-robin held-out slice, 240000 records each, differing in 162000 records.

| batch (same model, same size) | AUC-PR | AUC-ROC |
|---|---|---|
| timestamp-order slice (Table 6 slice value) | 0.844487 | 0.799910 |
| day-round-robin slice | 0.852039 | 0.809006 |

Difference from reported values: AUC-PR 0.007552, AUC-ROC 0.009096. Composition alone moves the AUC-PR.

Reproduction of the archived slice-batch value (0.844487): exact.

Wall time: 150 s.
