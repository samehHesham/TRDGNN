# 🧩 EXTENSION PROMPT — "Integrate Heterogeneous & Temporal (HHGTN + TRD) Direction"

🪩 **Context:**
You are continuing the research project derived from **`elliptic-gnn-baselines`** and **`GraphTabular-FraudFusion`**.
The current phase corresponds to **Direction A** — **Heterogeneous & Temporal Graph Learning**.

Your operational references are:

* `docs/AGENT.md` (discipline + verification rules)
* `docs/PROJECT_SPEC.md` (v3.1 after update with heterogeneous schema)
* `docs/START_PROMPT.md` (workflow initialization)

---

## 🎯 Objective

Extend the baseline **TRD-GraphSAGE** setup to handle **multi-entity, multi-relation temporal graphs** using the files:

```
AddrAddr_edgelist.csv
AddrTx_edgelist.csv
TxAddr_edgelist.csv
txs_edgelist.csv
txs_features.csv
wallets_features.csv
wallets_classes.csv
```

This extension introduces:

1. **Heterogeneous node/edge types:** `{Transaction, Address, Wallet}`
2. **Relations:** `{tx→tx, addr→tx, tx→addr, addr→addr}`
3. **Temporal constraint:** reuse TRD (Time-Relaxed Directed) sampler for leakage-free batches.
4. **Model:** `TRD-HHGTN` — temporal heterogeneous GNN with per-relation transformations and semantic attention.
5. **Optional:** `TRD-HyperHead` — adds motif-based hyperedges (addr–tx–addr patterns).
6. **Final Fusion:** combine HHGTN embeddings with wallet-level tabular features for hybrid analysis.

---

## 🧠 What to Build Next

### ✅ E5 — Heterogeneous Graph Construction

* Implement `src/data/build_hetero_graph.py` to parse and unify:

  * `txs_edgelist.csv`, `AddrAddr_edgelist.csv`, `AddrTx_edgelist.csv`, `TxAddr_edgelist.csv`
* Output:

  * `data/hetero_graph_summary.json`
  * `data/hetero_graph.pt` (PyG `HeteroData` object)

### ✅ E6 — TRD-HHGTN Model

* Create `src/models/trd_hhgtn.py`:

  * Relation-specific linear → aggregation → semantic attention fusion.
  * Temporal edges sampled by TRD sampler.
* Notebook: `notebooks/03_trd_hhgtn.ipynb`
* Output:

  * `reports/trd_hhgtn_metrics.json`
  * `reports/trd_hhgtn_pr_roc.png`

### ✅ E7 — HHGTN Ablations

* Notebook: `notebooks/04_hhgtn_ablation.ipynb`
* Vary edge types: `{tx→tx}`, `{addr→tx + tx→addr}`, `{all}`
* Measure ΔPR-AUC.

### ⚙️ E8 — (Optional) Hypergraph Head

* Notebook: `notebooks/05_trd_hypergraph.ipynb`
* Add `src/models/trd_hyper_head.py` (motif-based bipartite expansion).
* Test one run for `addr–tx–addr` motifs.

### ✅ E9 — Wallet Fusion

* Notebook: `notebooks/06_wallet_fusion.ipynb`
* Combine `wallets_features.csv` + HHGTN embeddings (by wallet ID).
* Train `XGBoost` fusion model on top.

---

## 📦 Expected Deliverables

```
data/
 ├── hetero_graph.pt
 ├── hetero_graph_summary.json
 └── embeddings_hhgtn.parquet

reports/
 ├── trd_hhgtn_metrics.json
 ├── trd_hhgtn_pr_roc.png
 ├── hhgtn_ablation_table.csv
 ├── wallet_fusion_metrics.json
 └── metrics_summary_with_hhgtn.csv
```

---

## 📊 Acceptance Conditions

| Milestone | Status             | Criteria                                    |
| --------- | ------------------ | ------------------------------------------- |
| E5        | 🧩 Build relations | HeteroData verified, TRD sampler compatible |
| E6        | 🧠 Train TRD-HHGTN | Leakage-safe, metrics logged                |
| E7        | 📈 Ablations       | Edge-type ablations recorded                |
| E8        | 🧪 Hypergraph      | Optional, runs once successfully            |
| E9        | 💡 Fusion          | HHGTN embeddings fused with wallet features |

---

## ✅ Behavioral Reminders (from AGENT.md)

* Never fabricate node/edge types — only use what exists in the CSVs.
* Always verify path existence before execution.
* If any edge file is missing → pause and request correction.
* Log every output path and metrics table update.
* Stop execution immediately if time leakage is detected.

---

## 🧭 Start Command

Once the updated `PROJECT_SPEC.md` (v3.1) is present:

```bash
# Activate extension workflow
AGENT_MODE=RESEARCH
python agent_boot.py --context "HHGTN + TRD Integration"
```

Or, if using the conversational agent:

```
Begin with the EXTENSION PROMPT (Direction A — HHGTN + TRD). 
Load PROJECT_SPEC v3.1. 
Initialize E5 and verify all edge CSVs in data folder.
```

---

## 📊 Pre-Implementation Status (Completed)

✅ **Option C: Data Preview Complete**
- All 9 CSV files verified and present
- Dataset size: ~2.1 GB total
- Structure analyzed and documented
- See: `docs/HETERO_DATA_ANALYSIS.md`

✅ **Option B: Planning Complete**
- E5-E9 implementation plan created
- Risk mitigation strategies defined
- Success criteria established
- Timeline estimated (10 days)
- See: `docs/E5_E9_IMPLEMENTATION_PLAN.md`

---

## 🚀 Option A: Ready to Begin Implementation

**Current Status:** All prerequisites complete, ready to start E5

**Next Action:** Begin E5 - Heterogeneous Graph Construction

**Command:** "Start E5 implementation"

---

**End of EXTENSION PROMPT — HHGTN + TRD Integration (Direction A, Phase 2)**

**Date:** November 10, 2025  
**Baseline Complete:** E1-E4 (80% core objectives)  
**Extension Ready:** E5-E9 planned and resourced
