# 🔧 CLONE_INIT_PROMPT_v3 — Bootstrapping the **TRD-GNN Temporal Extension**

**Purpose:** Set up a fresh repository for **leakage-safe temporal GNNs** using **Time-Relaxed Directed (TRD) sampling** on the **Elliptic++** dataset, while **reusing** baseline artifacts (splits + metrics) from `FRAUD-DETECTION-GNN`.

> **Work on `main` only.** No branches.

---

## 📎 Assumptions & Names

* **Baseline (source of truth):** `FRAUD-DETECTION-GNN`
* **New repo (this project):** `elliptic-trd-gnn`
  *(If you’ve already created the GitHub repo with a different name, replace it below.)*
* **Dataset location:** `data/Elliptic++ Dataset/` (local, user-provided)

---

## ✅ One-Shot Checklist

1. Clone **baseline** (read-only; do **not** modify it).
2. Create **new repo** folder and scaffold (TRD-GNN).
3. **Copy** only the allowed baseline artifacts:

   * `data/Elliptic++ Dataset/splits.json`
   * `reports/metrics_summary.csv` *(baseline* metrics table; keep filename)*
4. Write **provenance** lock (`docs/baseline_provenance.json`).
5. Drop in **v3** control docs:

   * `docs/PROJECT_SPEC_v3.md`
   * `docs/AGENT_v3.MD`
   * `docs/START_PROMPT_v3.md`
   * this file `docs/CLONE_INIT_PROMPT_v3.md`
6. Install deps, run quick **dataset checks**, run **TRD sampler unit test**.
7. First commit on **main**.

---

## 🧰 Commands (copy–paste, idempotent)

> Replace `<GITHUB_USERNAME>` and repo URLs as needed.

```bash
# ---- 0) Workspace prep -------------------------------------------------------
mkdir -p ~/work && cd ~/work

# ---- 1) Clone baseline (read-only) ------------------------------------------
git clone https://github.com/<GITHUB_USERNAME>/FRAUD-DETECTION-GNN.git baseline_gnn
cd baseline_gnn
# (Optional) lock to a known commit used in your DOI
# git checkout <BASELINE_COMMIT_SHA>
cd ..

# ---- 2) Create new repo skeleton --------------------------------------------
mkdir -p elliptic-trd-gnn/{data,notebooks,src/{data,models,train,utils,eval},tests,reports/plots,docs,configs,scripts,tools}
cd elliptic-trd-gnn
git init -b main

# ---- 3) Import baseline artifacts (strictly limited set) --------------------
mkdir -p "data/Elliptic++ Dataset" reports
cp ../baseline_gnn/data/Elliptic++\ Dataset/splits.json "data/Elliptic++ Dataset/splits.json"
cp ../baseline_gnn/reports/metrics_summary.csv reports/metrics_summary.csv

# ---- 4) Write provenance lock ------------------------------------------------
cat > docs/baseline_provenance.json << 'JSON'
{
  "baseline_repo": "https://github.com/<GITHUB_USERNAME>/FRAUD-DETECTION-GNN",
  "commit_sha": "<BASELINE_COMMIT_SHA_OR_TAG>",
  "zenodo_doi": "<BASELINE_ZENODO_DOI>",
  "imported_files": [
    "data/Elliptic++ Dataset/splits.json",
    "reports/metrics_summary.csv"
  ],
  "import_date_utc": "<YYYY-MM-DDTHH:MM:SSZ>"
}
JSON

# ---- 5) Drop v3 control docs (paste exact contents you prepared) ------------
#   - docs/PROJECT_SPEC_v3.md
#   - docs/AGENT_v3.MD
#   - docs/START_PROMPT_v3.md
#   - docs/CLONE_INIT_PROMPT_v3.md  (this file)
#   - README.md (stub acceptable for now)
#   (Create files now; the agent/user will paste content into each.)

# Stubs so the tree is valid; you will overwrite with real content next:
echo "# TRD-GNN Temporal Extension" > README.md
echo "# TODO: paste PROJECT_SPEC_v3.md" > docs/PROJECT_SPEC_v3.md
echo "# TODO: paste AGENT_v3.MD"        > docs/AGENT_v3.MD
echo "# TODO: paste START_PROMPT_v3.md" > docs/START_PROMPT_v3.md
echo "# (this file) CLONE_INIT_PROMPT_v3.md" > docs/CLONE_INIT_PROMPT_v3.md

# ---- 6) Minimal TRD sampler/test scaffolding --------------------------------
cat > src/data/trd_sampler.py << 'PY'
# Placeholder: real implementation will enforce time(nei) <= time(target)
class TRDSampler:
    def __init__(self, fanouts=(10,10), directed=True):
        self.fanouts = fanouts
        self.directed = directed
    def sample(self, graph, targets, timestamps):
        raise NotImplementedError("Implement leakage-safe temporal neighbor sampling.")
PY

cat > tests/test_trd_sampler.py << 'PY'
def test_trd_sampler_exists():
    from src.data.trd_sampler import TRDSampler
    s = TRDSampler()
    assert hasattr(s, "sample")
PY

# ---- 7) Python deps ----------------------------------------------------------
cat > requirements.txt << 'REQ'
torch
torch-geometric
pandas
numpy
scikit-learn
xgboost
matplotlib
pyyaml
tqdm
pytest
REQ
python -m pip install -r requirements.txt

# ---- 8) Smoke checks ---------------------------------------------------------
python - << 'PY'
# Verify imported artifacts exist
import os, sys
assert os.path.exists("data/Elliptic++ Dataset/splits.json"), "missing splits.json"
assert os.path.exists("reports/metrics_summary.csv"), "missing baseline metrics"

print("OK: baseline artifacts present.")
PY

pytest -q tests/test_trd_sampler.py

# ---- 9) First commit on main -------------------------------------------------
git add .
git commit -m "Initialize TRD-GNN extension: scaffold, baseline imports, provenance lock, tests."
# (Optional) add remote then push
# git remote add origin https://github.com/<GITHUB_USERNAME>/elliptic-trd-gnn.git
# git push -u origin main
```

---

## 🔒 Safety Gates (must pass before modeling)

1. `data/Elliptic++ Dataset/splits.json` exists **and** matches baseline provenance.
2. `reports/metrics_summary.csv` present (imported baseline metrics unmodified).
3. `pytest -q tests/test_trd_sampler.py` passes.
4. `docs/baseline_provenance.json` filled with real `commit_sha` and `zenodo_doi`.
5. Control docs **v3** are pasted and saved:

   * `docs/PROJECT_SPEC_v3.md`
   * `docs/AGENT_v3.MD`
   * `docs/START_PROMPT_v3.md`

---

## 🚫 Do **NOT** Import from Baseline

* **Do not** copy training notebooks, checkpoints, or raw data files.
* **Do not** copy code that would re-train legacy baselines.
* **Do not** relax temporal rules (no future neighbors).

---

## 📍 Next Step

After this file completes successfully:

* Paste your finalized **v3** docs into `docs/PROJECT_SPEC_v3.md`, `docs/AGENT_v3.MD`, and `docs/START_PROMPT_v3.md`.
* Start the agent using `docs/START_PROMPT_v3.md`.
* Implement `src/data/trd_sampler.py` per `PROJECT_SPEC_v3.md`, then proceed to training.

---

**End — CLONE_INIT_PROMPT_v3**
