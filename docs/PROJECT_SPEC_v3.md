# PROJECT_SPEC (v3 — TRD-GNN Temporal Extension, **Extension of Baseline**)

## 0) Purpose (single source of truth)

Define the **what** of this extension: minimal scope to deliver a **leakage-safe temporal GNN** on Elliptic++ using **Time-Relaxed Directed (TRD) sampling**. This project **reuses baseline artifacts** (`splits.json` + baseline metrics) from the completed repo and **does not** re-train prior GNN/tabular baselines. All tasks align with this spec.

---

## 1) Goal & Scope

**Project:** `elliptic-trd-gnn`
**Goal:** Implement a clean, reproducible **temporal graph baseline** by enforcing **no-future neighbors** and time-aware neighborhood sampling (TRD) on the same Elliptic++ splits as baseline; quantify whether temporal message passing adds value.
**Audience:** Recruiters, collaborators, future-you.
**Deliverable type:** Portfolio/demo repo — readable notebooks first, reusable `src/` utilities second.

**In scope**

* Import **`splits.json`** and **baseline `metrics_summary.csv`** (source of truth).
* Implement **TRD sampler** with strict rule: for a target node at time `t*`, **no neighbor with timestamp > `t*`**.
* Train **TRD-GraphSAGE** (primary) and **TRD-GCN** (optional).
* (Optional) **HHGTN-lite**: relation buckets (e.g., in/out/self) without full-blown hetero DSL.
* (Optional) **Hypergraph** incidence pass for tx–entity–tx motifs (minimal, demonstrative).
* Evaluate with **same metrics** and **temporal splits**; produce side-by-side table including imported baseline metrics vs TRD results.

**Out of scope (for this repo)**

* Re-training previous baselines (GCN/GraphSAGE/GAT, XGB/RF/MLP) — already done.
* Heavy foundation hetero models (e.g., Griffin), curvature/geometry pipelines, production serving.
* Any synthetic/mock data.

---

## 2) Dataset (Elliptic++)

**Identity:** Elliptic++ Bitcoin transaction graph (nodes=transactions; edges=directed flows).
**Location:** `data/Elliptic++ Dataset/` (local only; user provides files).
**Download:** [https://drive.google.com/drive/folders/1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l](https://drive.google.com/drive/folders/1MRPXz79Lu_JGLlJ21MDfML44dKN9R08l)

**Required files**

* `txs_features.csv` — `txid`, `timestamp`, **Local_feature_1..93**, **Aggregate_feature_1..89** (total 182)
* `txs_classes.csv` — `txid`, `class` (1=fraud, 2=legit, 3=unknown)
* `txs_edgelist.csv` — `txId1`, `txId2`

**Data policy**

* **No synthetic data.** Stop if files/columns mismatch; request correct path.
* Notebooks must verify file presence before running.
* Any preprocessing is deterministic and logged.

---

## 3) Temporal Split (no leakage)

**Source of truth:** Reuse **baseline** `splits.json`.

* Train/Val/Test membership **identical** to baseline.
* For **TRD sampling**, enforce **split isolation for supervision** and **no-future neighbors**: for node `u` with time `t*`, sampled neighbors `v` must satisfy `time(v) ≤ t*`.
* Keep counts/boundaries identical; persist `splits.json` copy under `data/Elliptic++ Dataset/`.

---

## 4) Preprocessing & Features

* Map `txid` → contiguous indices `[0..N-1]` (persist mapping; must match splits).
* Filter edges to known nodes; coalesce duplicates.
* Optional normalization for GNN inputs (fit on **train only**; apply to val/test).
* **Feature policy:** start with **Local (AF1–AF93)** to avoid double-encoding aggregate neighbor stats; optionally compare with **All (AF1–AF182)** and document any redundancy.

---

## 5) Models

### 5.1 TRD Sampler (core)

* Enforce directed time-aware neighborhood: **no neighbor with `timestamp > target`**.
* Configurable caps: `max_in_neighbors`, `max_out_neighbors`, `fanout_per_layer`.
* Reject/flag any violation; unit test must pass.

### 5.2 Temporal GNNs

* **TRD-GraphSAGE (primary)** — mean/concat aggregators with TRD neighborhoods.
* **TRD-GCN (optional)** — GCN layers over TRD-induced subgraphs.

**Common:** `in_channels`, `hidden_channels`, `out_channels=2`, `num_layers`, `dropout`, ReLU.
**Output:** logits `[N,2]` for labeled nodes in each split.

---

## 🔮 SECTION 5.4 — TRD-HHGTN (Heterogeneous Temporal GNN)

**Purpose:** Extend TRD-GraphSAGE to multi-entity, multi-relation graphs using Elliptic++’s full relational structure
(`Transaction`, `Address`, `Wallet`).

**Motivation:**
Baseline GNNs and fusion models treat the Elliptic graph as *homogeneous* (single node/edge type).
However, fraud behavior occurs *across* entities: wallets ↔ addresses ↔ transactions.
Hence, a **Heterogeneous Temporal GNN (HHGTN)** integrates relation-specific learning and temporal realism.

### **Graph Schema**

| Node Type     | Source File            | Key Fields                 |
| ------------- | ---------------------- | -------------------------- |
| `Transaction` | `txs_features.csv`     | txid, timestamp, AF1–AF182 |
| `Address`     | `Addr*` files          | addr_id                    |
| `Wallet`      | `wallets_features.csv` | wallet_id, features, label |

| Edge Type   | Source → Target               | Source File             |
| ----------- | ----------------------------- | ----------------------- |
| `tx→tx`     | transaction flow              | `txs_edgelist.csv`      |
| `addr→tx`   | address input to transaction  | `AddrTx_edgelist.csv`   |
| `tx→addr`   | transaction output to address | `TxAddr_edgelist.csv`   |
| `addr→addr` | address peer relations        | `AddrAddr_edgelist.csv` |

Each edge list must contain:

```csv
src_id,dst_id,timestamp
```

and all edges are filtered by TRD time windows.

### **Model Architecture**

```
Input  →  Per-relation linear transform
        →  TRD-sampled message passing (per edge type)
        →  Semantic attention fusion (relation importance)
        →  Node-type projection (Transaction / Address / Wallet)
        →  Temporal readout (wallet-level or tx-level logits)
```

**Key Modules**

| Module           | Function                                          |
| ---------------- | ------------------------------------------------- |
| `RelationConv`   | learns message functions per edge type            |
| `SemanticFusion` | attention weighting of relation embeddings        |
| `TRDSampler`     | time-relaxed, direction-preserving batch sampling |
| `ReadoutHead`    | aggregation by node type or wallet cluster        |

**Output:**
`reports/trd_hhgtn_metrics.json` + `reports/trd_hhgtn_pr_roc.png`

---

## ⚙️ SECTION 5.5 — TRD-HyperHead (Optional Hypergraph Extension)

**Purpose:** Capture higher-order motifs (e.g., addr–tx–addr groups, wallet clusters).
Derived from **HHGTN embeddings**, extended via *bipartite expansion*.

**Procedure:**

1. Construct hyperedges where ≥2 addresses interact with same tx in short temporal window.
2. Represent hyperedges as auxiliary adjacency matrices.
3. Add `HyperHead` that aggregates motif embeddings and re-injects into node states.

**Files:**
`src/models/trd_hyper_head.py`
`notebooks/05_trd_hypergraph.ipynb`

---

## 🧠 SECTION 6 — Updated Evaluation Plan

| Setting          | Model                    | Target    | Metric     |
| ---------------- | ------------------------ | --------- | ---------- |
| Temporal         | TRD-GraphSAGE            | Tx        | PR-AUC     |
| Hetero+Temporal  | TRD-HHGTN                | Tx/Wallet | PR-AUC     |
| Hypergraph (opt) | TRD-HHGTN+HyperHead      | Wallet    | PR-AUC     |
| Fusion           | WalletFusion (XGB + Emb) | Wallet    | PR-AUC, F1 |

*Leakage control:* Each relation’s edges filtered per split.
*Baseline comparison:* Merge `metrics_summary_with_hhgtn.csv` with previous results.

---

## 🧩 SECTION 8 — Repo Additions

```
src/
 ├── data/
 │    └── build_relations.py        # merge all edgelists → HeteroData
 ├── models/
 │    ├── trd_hhgtn.py              # main model
 │    └── trd_hyper_head.py         # optional extension
 ├── train/
 │    └── trd_hhgtn_train.py
 └── eval/
      └── hhgtn_report.py
```

---

## 🧾 SECTION 11 — New Acceptance Milestones

| ID     | Milestone                 | Goal                                       | Deliverables                                        |
| ------ | ------------------------- | ------------------------------------------ | --------------------------------------------------- |
| **E5** | Heterogeneous Graph Build | integrate all edge types → `HeteroData`    | `data/hetero_graph.pt`, `hetero_graph_summary.json` |
| **E6** | TRD-HHGTN Train           | train leakage-safe hetero model            | `reports/trd_hhgtn_metrics.json`, `plots/`          |
| **E7** | Ablation                  | relation & edge-type sensitivity           | `reports/hhgtn_ablation_table.csv`                  |
| **E8** | Hypergraph Head (opt)     | test higher-order patterns                 | `reports/trd_hyper_metrics.json`                    |
| **E9** | Wallet Fusion             | combine HHGTN embeddings + wallet features | `reports/wallet_fusion_metrics.json`                |

---

## 🧩 SECTION 13 — Risk Control Addendum

| Risk                   | Mitigation                                          |
| ---------------------- | --------------------------------------------------- |
| Cross-split leakage    | enforce TRD filtering per edge type                 |
| Missing node alignment | `build_relations.py` auto-verifies ID overlap       |
| Memory overload        | edge sampling + per-relation batching               |
| Feature duplication    | run Protocol A (local features only) first          |
| Temporal skew          | verify timestamp monotonicity during relation merge |


---

## 6) Training & Evaluation

**Loss**

* `CrossEntropyLoss` on logits `[N,2]` (or `BCEWithLogits` consistently).
* Use `pos_weight` / class weights computed from **train** labels.

**Optimization**

* Adam, `lr` (default 1e-3), `weight_decay` (default 5e-4).
* Early stopping on **val PR-AUC** (patience ≈ 15 epochs).

**Evaluation protocol**

* Threshold selected on **val** to maximize F1; reuse on **test**.
* Report on **test**:

  * PR-AUC (primary), ROC-AUC, F1 at val-selected threshold, Recall@K (K ∈ {0.5%, 1%, 2%}).
* **Side-by-side comparison**:

  * Import prior baseline metrics (tabular & static GNNs) from baseline `reports/metrics_summary.csv`.
  * Append new **TRD** rows computed here.
  * Produce consolidated table + PR/ROC plots.

**Artifacts**

* `checkpoints/trd_graphsage_best.pt` (and/or `trd_gcn_best.pt`)
* `reports/metrics.json`
* `reports/plots/*.png` (PR/ROC; TRD diagnostics)
* Append to `reports/metrics_summary.csv`:

  * `timestamp, experiment, model, split, pr_auc, roc_auc, f1, recall@1%`

---

## 7) Reproducibility

Always:

```python
from src.utils.seed import set_all_seeds
set_all_seeds(seed)

import torch
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False
```

* Save `splits.json`, scaler params, library versions.
* Avoid absolute paths; use project-relative paths.
* **Provenance lock:** `docs/baseline_provenance.json` with:

  * baseline repo URL, commit SHA, Zenodo DOI, date imported.

---

## 8) Repository Scaffold

```
elliptic-trd-gnn/
│
├── data/
│   └── Elliptic++ Dataset/             # user-provided dataset + baseline splits.json
│
├── notebooks/
│   ├── 01_trd_sampler_mvp.ipynb        # TRD checks + subset PR/ROC
│   └── 02_trd_graphsage.ipynb          # Full TRD-GraphSAGE run
│
├── src/
│   ├── data/
│   │   ├── elliptic_loader.py          # masks + splits (reused)
│   │   └── trd_sampler.py              # time-relaxed, no-future neighbors
│   ├── models/
│   │   ├── trd_graphsage.py
│   │   └── trd_gcn.py
│   ├── utils/
│   │   ├── metrics.py
│   │   ├── seed.py
│   │   └── logger.py
│   ├── train.py                        # CLI wrappers (config-driven)
│   └── eval.py
│
├── configs/
│   ├── trd_graphsage.yaml
│   └── trd_gcn.yaml
│
├── tests/
│   └── test_trd_sampler.py             # assert no future neighbors
│
├── reports/
│   ├── plots/
│   └── metrics_summary.csv
│
├── docs/
│   ├── PROJECT_SPEC_v3.md
│   ├── AGENT_v3.MD
│   ├── START_PROMPT_v3.md
│   ├── CLONE_INIT_PROMPT_v3.md
│   └── baseline_provenance.json
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 9) Configuration (YAML)

```yaml
experiment: "elliptic-trd-gnn"
seed: 42
device: "cuda"   # or "cpu"

baseline:
  provenance: "docs/baseline_provenance.json"
  metrics_csv: "../FRAUD-DETECTION-GNN/reports/metrics_summary.csv"  # or local copy
  reuse_splits: true

data:
  root: "data/Elliptic++ Dataset"
  features: "txs_features.csv"
  labels: "txs_classes.csv"
  edges: "txs_edgelist.csv"
  splits_file: "splits.json"

trd:
  forbid_future_neighbors: true
  max_in_neighbors: 15
  max_out_neighbors: 15
  fanout_per_layer: [15, 10]   # l1, l2
  direction_weight: {in: 1.0, out: 1.0}
  allow_backward_if_past: true

model:
  name: "trd_graphsage"        # trd_graphsage | trd_gcn
  hidden_channels: 128
  num_layers: 2
  dropout: 0.4

train:
  epochs: 80
  batch_size: null             # full-batch if feasible; else micro-batch
  lr: 0.001
  weight_decay: 0.0005
  early_stopping_patience: 15

eval:
  recall_k_fracs: [0.005, 0.01, 0.02]
  save_plots: true

logging:
  out_dir: "reports"
```

---

## 10) Metrics & File Formats

**`reports/metrics.json` (per split)**

```json
{
  "pr_auc": 0.5721,
  "roc_auc": 0.8663,
  "best_f1": 0.4987,
  "threshold": 0.421,
  "recall@1%": 0.392
}
```

**Append row to `reports/metrics_summary.csv`:**

```
timestamp,experiment,model,split,pr_auc,roc_auc,f1,recall@1%
1731143000,elliptic-trd-gnn,TRD-GraphSAGE,test,0.572100,0.866300,0.498700,0.392000
```

**Consolidated table**

* A small utility merges imported baseline rows and the new TRD rows for the README.

---

## 11) Acceptance Criteria (extension milestones)

**M1 — Bootstrap & Import**

* Repo scaffold matches Section 8; `pip install -r requirements.txt` succeeds.
* `baseline_provenance.json` created; baseline `metrics_summary.csv` imported/copied.

**M2 — TRD Sampler MVP**

* `trd_sampler.py` implemented; **unit test passes** (no future neighbors).
* `01_trd_sampler_mvp.ipynb` runs a subset; saves mini PR/ROC; appends CSV.

**M3 — TRD-GraphSAGE Full**

* `02_trd_graphsage.ipynb` completes; saves metrics, plots, checkpoint; CSV appended.

**M4 — Comparison Report**

* Consolidated table (baseline vs TRD) produced; plots saved to `reports/plots/`; README updated.

**M5 — (Optional) Variants**

* HHGTN-lite or Hypergraph toy pass run once; notes added to README.

---

## 12) Risks & Pitfalls (and how we avoid them)

* **Temporal leakage:** TRD sampler enforces `time(neighbor) ≤ time(target)`; unit test guards this.
* **Split contamination:** Supervision restricted by split masks; edges for sampling may span times **only if** they obey the no-future rule; document policy per notebook.
* **Double-encoding with AF aggregates:** Prefer Local AF1–AF93 as default; document any changes.
* **ID misalignment:** Persist and validate `txid`↔index mapping before training.
* **Non-reproducibility:** Seeds + deterministic ops; reuse exact splits; log versions.

---

## 13) Roadmap (future, not here)

* Add calibrated thresholds under shift (expected prevalence drift).
* Rich heterogeneous modeling (full HHGTN), real entity graphs.
* End-to-end temporal contrastive pretraining (future repo).
* Serve lightweight scoring for batch inference (separate project).

---

## 14) License & Acknowledgements

* Respect Elliptic++ dataset licensing/terms.
* Cite the dataset and the baseline repo’s DOI in README.
* This repo is educational/demonstrative.

---

**End of `PROJECT_SPEC_v3.md` (TRD-GNN Temporal Extension).**
