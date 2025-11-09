\# 🧭 AGENTv3.MD — Operational Discipline for Codex Agent



\## 🎯 Project Context



\*\*Project:\*\* `elliptic-trd-gnn` (Temporal GNN Extension)

\*\*Status:\*\* 🧩 \*\*IN PROGRESS\*\* (Phase III of Elliptic++ Study — extending baselines)

\*\*Goal:\*\* Build, train, and evaluate \*\*leakage-safe temporal GNNs\*\* using \*\*Time-Relaxed Sampling (TRD-GNN)\*\* on the \*\*Elliptic++\*\* dataset; optionally add \*\*heterogeneous (HHGTN-lite)\*\* and \*\*hypergraph\*\* variants.

\*\*Purpose:\*\* Extend the baseline study into \*\*deployable temporal graph models\*\*—quantifying when temporal message passing adds value under honest, no-future evaluation.



\*\*🎯 Notebook Target Environment:\*\* All notebooks are compatible with \*\*Kaggle\*\* (and Colab). Paths and dependencies are kept Kaggle-friendly (`data/Elliptic++ Dataset/…`).



---



\### Agent Mode Toggle



To enable flexible behavior across repositories, the agent can operate in different modes:



| Mode           | Description                                                                        | Typical Use                                   |

| -------------- | ---------------------------------------------------------------------------------- | --------------------------------------------- |

| `RESEARCH`     | Full verification, logging, \*\*temporal integrity (no-future)\*\* checks.             | Default for active experiments and ablations. |

| `MAINTENANCE`  | Reduces verbosity; skips heavy verification for quick bugfixes.                    | Routine updates or post-publication fixes.    |

| `EXPERIMENTAL` | Allows architectural freedom — HHGTN-lite, relation buckets, hypergraph incidence. | Prototyping temporal/hetero variants.         |

| `ANALYTICS`    | Evaluation-only mode — runs saved models and aggregates metrics.                   | Comparative analysis and write-up tables.     |



Set with environment variable or config flag:



```bash

export AGENT\_MODE=RESEARCH

```



---



\## 🧠 Core Philosophy



\*\*Rule:\*\* \*Think before you code.\*

Every action follows this discipline:



> \*\*Plan → Verify → Execute → Log\*\*



1\. \*\*Plan\*\*: Explain what you intend to do (in comments or markdown).

2\. \*\*Verify\*\*: Check dataset availability, paths, imports, \*\*splits\*\*, and TRD constraints.

3\. \*\*Execute\*\*: Run only when context and inputs are validated.

4\. \*\*Log\*\*: Record metrics, plots, and notes; never just say “done”.



---



\## 📝 To-Do List Discipline



Use an explicit, living TODO checklist to drive every action.

Never start a new task until the current task’s checklist is ✅ complete.



\*\*Rules\*\*



\* Maintain a single project checklist in `TASKS.md` and a mini-checklist at the top of each notebook.

\* Every task has: \*\*ID, Goal, Steps, Done criteria\*\* (must include verification).

\* Update the checklist before and after each operation:



&nbsp; \*\*Before:\*\* mark planned steps as pending and state expected outputs.

&nbsp; \*\*After:\*\* mark completed steps, attach artifact paths, and note warnings/errors.



If blocked > 5 fix attempts → stop, write an escalation note (what was tried, errors, hypotheses), and request guidance.



\*\*Allowed statuses\*\*



```

\[ ] pending

\[~] in progress

\[?] blocked (requires input)

\[x] done (after verification)

```



\### Project-level template (TASKS.md)



```

\# TASKS (single source of truth)



\## T-01 Bootstrap TRD Extension

Goal: Scaffold TRD repo, import baseline splits/metrics, create stubs.

Steps:

\- \[ ] Create folder tree + empty notebooks

\- \[ ] Add requirements.txt and install

\- \[ ] Import splits.json + metrics\_summary.csv from baseline

Done when:

\- \[x] pip install -r requirements.txt succeeds

\- \[x] Tree matches scaffold; README renders; splits present



\## T-02 TRD Sampler MVP

Goal: Implement time-relaxed neighborhood rule (no future neighbors).

Steps:

\- \[ ] Implement src/data/trd\_sampler.py

\- \[ ] Add unit test to assert timestamp(neighbor) <= timestamp(target)

\- \[ ] Run 01\_trd\_sampler\_mvp.ipynb on a subset; plot PR/ROC

Done when:

\- \[x] Tests pass; no-future constraint verified

\- \[x] reports/metrics\_summary.csv updated (subset run)



\## T-03 TRD-GraphSAGE Full Run

Goal: Train TRD-GraphSAGE end-to-end on Elliptic++ splits.

Steps:

\- \[ ] Configure configs/trd\_graphsage.yaml

\- \[ ] Run 02\_trd\_graphsage.ipynb; save metrics \& plots

\- \[ ] Append metrics\_summary.csv; log run meta

Done when:

\- \[x] reports/metrics.json + plots/\*.png saved

\- \[x] checkpoints/trd\_graphsage\_best.pt saved

```



\### Notebook-level header template



```

\# Notebook TODO (auto-discipline)

\- \[ ] Load real Elliptic++ data from data/Elliptic++ Dataset/

\- \[ ] Validate splits.json and timestamp monotonicity

\- \[ ] Enforce TRD: neighbors' time <= target time

\- \[ ] Train/evaluate (subset → full) with fixed seeds

\- \[ ] Save: reports/metrics.json, plots/, append metrics\_summary.csv

\- \[ ] Verify metrics + artifact paths printed in last cell

\- \[ ] Clear TODOs before commit

```



\*\*Execution protocol with TODOs\*\*



Plan → expand TASKS.md + header checklist → Verify paths/config/\*\*TRD rule\*\* → Execute steps sequentially → Log artifacts.

Blocked? mark `\[?]` and add Escalation Note before asking.



---



\## ⚙️ Decision Chain Discipline



The agent must never assume. It must reason and confirm.



1\. Describe intended change and expected outcome.

2\. Validate environment (paths, packages, variables, \*\*TRD constraints\*\*).

3\. Run minimal safe code to verify correctness.

4\. Summarize results and check warnings/errors.

5\. If uncertain → pause and ask.



\*\*Forbidden behaviors:\*\*

– Blind continuation after exceptions

– Skipping error resolution

– Fabricating synthetic data



---



\## 🧩 Data Handling Rules



\*\*Dataset Identity:\*\*

`Elliptic++` — real Bitcoin transaction dataset with timestamps, directed edges, and tabular features.



\*\*Data Policy:\*\*



\* 📁 Data lives in `data/Elliptic++ Dataset/`:



&nbsp; \* `txs\_features.csv` — 182 tabular features

&nbsp; \* `txs\_classes.csv` — labels (1=Fraud, 2=Legit, 3=Unknown)

&nbsp; \* `txs\_edgelist.csv` — directed edges (tx → tx)

&nbsp; \* `splits.json` — \*\*imported\*\* temporal splits (from baseline)

\* 🛑 Never fabricate or mock data.

\* 🧾 Always verify file existence \& schema before import.

\* 📥 Download location: \[Google Drive Folder](https://drive.google.com/drive/folders/1MRPXz79Lu\_JGLlJ21MDfML44dKN9R08l)

\* 💾 All metrics and plots must reference the dataset version in use.



---



\## 📓 Notebook Workflow Discipline



\*\*Main work happens in notebooks under `/notebooks`.\*\*



\### Notebook Rules



1\. Each experiment (TRD sampler, TRD-GraphSAGE, optional HHGTN/Hyper) in its own `.ipynb`.

2\. Use markdown cells for objectives + findings.

3\. Keep code concise and readable.

4\. `/src` for reusable utilities (loaders, metrics, TRD sampler, models).

5\. Each notebook should:



&nbsp;  \* Load data

&nbsp;  \* Run one experiment

&nbsp;  \* Produce:



&nbsp;    \* `reports/metrics.json`

&nbsp;    \* `reports/plots/\*.png`

&nbsp;    \* Append `metrics\_summary.csv`



\### Notebook Flow Example



| Step | Notebook                        | Purpose                          |

| ---- | ------------------------------- | -------------------------------- |

| 0    | `01\_trd\_sampler\_mvp.ipynb`      | TRD rule checks + subset run     |

| 1    | `02\_trd\_graphsage.ipynb`        | Full TRD-GraphSAGE experiment    |

| 2    | `03\_hhgtn\_lite\_relations.ipynb` | (Opt.) relation buckets (hetero) |

| 3    | `04\_hypergraph\_incidence.ipynb` | (Opt.) Tx–Entity hypergraph      |



---



\## 🧮 Verification Before Commit



Before declaring any task \*\*complete\*\*, verify:



✅ All notebooks run end-to-end on real Elliptic++ data.

✅ \*\*TRD integrity:\*\* no neighbor with `timestamp > target\_time`.

✅ Metrics logged (`metrics\_summary.csv`, `metrics.json`).

✅ PR-AUC / ROC-AUC / Recall@K plotted and saved.

✅ No TODOs or placeholders remain.

✅ All paths relative (`data/Elliptic++ Dataset/...`).

✅ Seeds set (torch, numpy, python).

✅ No hardcoded absolute paths or env leaks.



---



\## 🧰 Error \& Resolution Protocol



If an error occurs:



1\. \*\*Stop immediately.\*\*

2\. Attempt fix ≤ 5 times with reasoning.

3\. For each attempt log: what / why / result.

4\. If unresolved → summarize causes, notify user, await decision.



Never continue “as if it worked.”



---



\## 📊 Logging \& Artifact Discipline



Every run outputs:



\* `reports/metrics\_summary.csv` — all experiment results

\* `reports/plots/\*.png` — PR/ROC curves \& diagnostics

\* `checkpoints/trd\_\*\_best.pt` (if applicable)

\* `data/Elliptic++ Dataset/splits.json` — temporal splits (read-only here)



Each `metrics\_summary.csv` row must include:



| Field      | Example          |

| ---------- | ---------------- |

| timestamp  | 1731046600       |

| experiment | elliptic-trd-gnn |

| model      | TRD-GraphSAGE    |

| split      | test             |

| pr\_auc     | 0.6123           |

| roc\_auc    | 0.8710           |

| f1         | 0.528            |

| recall@1%  | 0.402            |



---



\## 🧬 Reproducibility



Always call:



```python

from src.utils.seed import set\_all\_seeds

set\_all\_seeds(42)

torch.use\_deterministic\_algorithms(True)

torch.backends.cudnn.benchmark = False

```



before any training step.



Log:



\* Python / PyTorch / PyG versions

\* Random seeds in JSON configs



---



\## 🧑‍💻 Communication Tone \& Escalation



\*\*Tone:\*\* Analytical, cautious, transparent.

Always explain \*why\* before \*doing\*.



If progress stalls or data errors persist:



```

❗ Stopped execution

Attempted fixes:

&nbsp;1. …

&nbsp;2. …

Remaining issue: …

Possible causes: …

Awaiting instruction.

```



Never hide or skip failed cells.



---



\## ✅ Summary



| Aspect            | Policy                                           |

| ----------------- | ------------------------------------------------ |

| Dataset           | Real Elliptic++ only                             |

| Code surface      | Primarily notebooks                              |

| Verification      | Strict, \*\*no-future\*\* temporal integrity         |

| Decision protocol | Plan → Verify → Execute → Log                    |

| Errors            | Resolve or escalate                              |

| Communication     | Transparent \& reasoned                           |

| Goal              | A robust, deployable \*\*Temporal GNN (TRD) repo\*\* |



---



\*\*End of AGENT.MD\*\*



---



