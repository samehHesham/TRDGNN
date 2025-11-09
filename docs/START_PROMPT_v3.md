🪩 This runtime prompt assumes the workspace was cloned using:
`CLONE_INIT_PROMPT_v3.md` — setup and provenance verified.

# 🚀 START PROMPT — “Elliptic++ Fraud Detection: TRD-GNN Temporal Extension” Boot

**Context load:**
You are initializing work on the **`elliptic-trd-gnn`** repository — a **temporal extension** of the completed baseline project **`FRAUD-DETECTION-GNN`**. This repo focuses on training **leakage-safe temporal GNNs** via **Time-Relaxed Directed (TRD) sampling** on the **same temporal splits** as baseline.

* **Baseline repo (source of truth):** `FRAUD-DETECTION-GNN` — **COMPLETE**, Zenodo DOI published.
* **This repo (extension):** **temporal GNN only**; we **reuse** the baseline’s `splits.json` and `metrics_summary.csv`. No retraining of legacy tabular or static GNN baselines.

Your full operational context is defined by three documents in this repo:

1. `docs/AGENT_v3.MD` — **behavioral discipline**, verification rules, escalation protocol.
2. `docs/PROJECT_SPEC_v3.md` — **architecture** for TRD sampler, models, metrics, acceptance criteria.
3. `TASKS.md` — **active planner** for milestones/tasks in this extension.

---

## 🧠 Initialization Instructions

1. **Read** `docs/AGENT_v3.MD`, `docs/PROJECT_SPEC_v3.md`, `TASKS.md`.
2. Adopt **Plan → Verify → Execute → Log** from `AGENT_v3.MD`.
3. Treat:

   * `PROJECT_SPEC_v3.md` as **immutable blueprint** for TRD scope.
   * `TASKS.md` as **dynamic plan** (statuses `[ ]`, `[~]`, `[x]`, `[?]`).
4. Confirm dataset path **`data/Elliptic++ Dataset/`** contains **real Elliptic++** files only:

   * `txs_features.csv`, `txs_classes.csv`, `txs_edgelist.csv`, `splits.json` (copied from baseline).
5. Confirm **provenance**: `docs/baseline_provenance.json` records baseline URL/commit/DOI.
6. Ensure **tests/test_trd_sampler.py** exists and will be run before full training.

**Critical constraints:**

* **Do NOT** retrain legacy baselines (LR/XGB/MLP) or static GNNs (GCN/GraphSAGE/GAT). We **reuse** their metrics and the **exact** temporal splits.
* **No future neighbors**: for a node at time `t*`, sampled neighbors must satisfy `time(neighbor) ≤ t*`.

---

## 📈 Current State Snapshot (as of Nov 9, 2025)

**Baseline project (`FRAUD-DETECTION-GNN`)**

* **Status:** ✅ **COMPLETE** (M1–M10)
* **Key finding:** Aggregate tabular features encode neighbor stats → **XGBoost > static GNNs**.
* **Zenodo DOI:** (recorded in baseline_provenance)
* **Artifacts:** `splits.json`, `reports/metrics_summary.csv`, published docs/plots.

**This extension (`elliptic-trd-gnn`)**

* **Status:** 🟡 **INIT** (scaffold + imports to be completed)
* **Goal:** Train **TRD-GraphSAGE** (primary) and optionally **TRD-GCN**, compare against **imported** baseline metrics under strict no-leakage.

---

## 🎯 Research Goal (Extension Scope)

> **Primary Objective:** Quantify the benefit of **temporal message passing** when neighborhoods respect **directed time causality** (no future neighbors), using **exact baseline splits** and reproducible evaluation.

---

## 🔬 TRD Design Principles

* **Time-Directed Neighborhoods:** For target time `t*`, neighbors must satisfy `timestamp ≤ t*`.
* **Directed Sampling:** Separate **in** and **out** edges; configurable caps `fanout_per_layer`.
* **Leakage Gate:** Any neighbor with `timestamp > t*` must be **rejected** (unit-tested).
* **Feature Policy:** Prefer **Local features (AF1–AF93)** initially to avoid double-encoding; optionally document results with **All (AF1–AF182)**.

---

## 🧾 Workflow Discipline (unchanged)

1. **Plan** intent + expected outputs.
2. **Verify** dataset presence, column schema, split alignment, and TRD rules (no future).
3. **Execute** minimal, reproducible notebooks/scripts.
4. **Log** metrics to `reports/`, update `TASKS.md`, save plots.

Escalate after **≤5** failed fix attempts with a succinct failure memo and options.

---

## 🧩 Extension Milestones (v3)

| Milestone                       | Goal                                                                                            | Deliverables                                                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **E1 — Bootstrap & Provenance** | Scaffold repo; import baseline **`splits.json`** & **`metrics_summary.csv`**; write provenance. | Folder tree; imported CSV; `docs/baseline_provenance.json`.                            |
| **E2 — TRD Sampler MVP**        | Implement **`trd_sampler.py`** with **no-future** check; pass unit test.                        | `src/data/trd_sampler.py`, `tests/test_trd_sampler.py`, mini PR/ROC from MVP notebook. |
| **E3 — TRD-GraphSAGE Train**    | Full training with **Local AF1–AF93**; early stopping on **val PR-AUC**.                        | `checkpoints/trd_graphsage_best.pt`, `reports/metrics.json`, plots, CSV row.           |
| **E4 — Comparison Report**      | Merge **imported baseline** rows with **TRD** rows; produce consolidated table + README update. | Combined table; `reports/plots/*.png`; README section.                                 |
| **E5 — (Optional) Variants**    | **TRD-GCN** and/or **All AF1–AF182** feature run; document redundancy/impact.                   | Added rows + small bar chart.                                                          |

---

## 📊 Evaluation Protocol (unchanged from spec)

* **Primary metric:** PR-AUC; also report ROC-AUC, F1 (threshold from **val**), Recall@K (0.5%, 1%, 2%).
* **Artifacts:** `reports/metrics.json`, append to `reports/metrics_summary.csv`, plots saved to `reports/plots/`.

---

## 🧭 Behavioral Highlights (from AGENT_v3.MD)

* **No synthetic data.**
* **No retraining** of legacy baselines; **reuse** their metrics & splits.
* **Explain before executing.**
* **Leakage gate:** If any sampled neighbor violates `time(neighbor) ≤ time(target)`, **stop** and fix sampler.
* **Sanity gate:** If PR-AUC is implausible (>0.90), trigger **LeakageSuspect** review before acceptance.

---

## ✅ Start Command (for new chat)

1. Summarize `PROJECT_SPEC_v3.md` and `TASKS.md` (TRD scope only).
2. Confirm presence of:

   * `data/Elliptic++ Dataset/{txs_features.csv, txs_classes.csv, txs_edgelist.csv, splits.json}`
   * `docs/baseline_provenance.json`
   * Imported baseline `reports/metrics_summary.csv`
3. Run unit tests: `pytest -q tests/test_trd_sampler.py` — must pass.
4. Execute **E2 → E3**: Validate TRD sampler on a subset, then train **TRD-GraphSAGE** on full splits.
5. Produce **side-by-side** table in README (baseline vs TRD).

---

### 🪩 Output Expectation for New Sessions

* Clear restatement of TRD scope and constraints.
* Confirmation that **baseline artifacts** (splits + metrics) are in place.
* Confirmation that **TRD unit tests pass** (no-future guarantee).
* TRD training results logged and merged with baseline table.
* README updated with a short, honest comparison summary.

---

## 📦 Key Inputs & Paths

* **Dataset folder:** `data/Elliptic++ Dataset/`
* **Baseline imports:** `data/Elliptic++ Dataset/splits.json`, `reports/metrics_summary.csv`
* **Checkpoints:** `checkpoints/trd_graphsage_best.pt` (and/or `trd_gcn_best.pt`)
* **Reports:** `reports/metrics.json`, `reports/plots/*.png`, `reports/metrics_summary.csv`
* **Provenance:** `docs/baseline_provenance.json`
* **Sampler:** `src/data/trd_sampler.py` (unit-tested)

---

## 🏁 Status Policy

* **E1–E4 complete** → TRD MVP accepted.
* **E5 optional** → Variants + feature policy analysis.
* Any violation of TRD/no-leakage rules → **Stop**, summarize, and request a decision.

---

**End of Start Prompt (v3 — TRD-GNN Temporal Extension, updated 2025-11-09)**

---
