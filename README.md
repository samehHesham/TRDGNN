# TRD-GNN: Temporal Graph Neural Networks for Fraud Detection

**Leakage-safe temporal GNN** for cryptocurrency fraud detection on the Elliptic++ dataset using **Time-Relaxed Directed (TRD) sampling**.

## 🎯 Overview

This project implements temporal Graph Neural Networks with strict temporal constraints to prevent information leakage. The core innovation is the TRD sampler, which enforces `time(neighbor) ≤ time(target)` during message passing, ensuring realistic fraud detection that respects transaction chronology.

## ✨ Key Features

- **🕐 TRD Sampler**: Time-aware neighbor sampling preventing future information leakage
- **🧠 Temporal Models**: TRD-GraphSAGE and TRD-GCN implementations
- **📊 Baseline Integration**: Direct comparison with static GNN baselines
- **✅ Fully Tested**: Comprehensive test suite (7/7 tests passing)
- **📝 Well Documented**: Complete specification and provenance tracking

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/test_trd_sampler.py -v
```

### Project Structure

```
.
├── src/              # Source code
│   ├── data/        # Data loaders and TRD sampler
│   ├── models/      # GNN model implementations
│   ├── utils/       # Utilities and metrics
│   └── train.py     # Training scripts
├── tests/           # Unit tests
├── notebooks/       # Jupyter notebooks for experiments
├── configs/         # Model configurations
├── reports/         # Results and visualizations
└── docs/            # Documentation
```

## 📚 Documentation

- [**PROJECT_SPEC.md**](PROJECT_SPEC.md) - Complete project specification
- [**AGENT.md**](AGENT.md) - AI agent development guidelines
- [**START_PROMPT.md**](START_PROMPT.md) - Quick start instructions
- [**CLONE_INIT_PROMPT.md**](CLONE_INIT_PROMPT.md) - Setup procedures
- [**docs/baseline_provenance.json**](docs/baseline_provenance.json) - Baseline tracking

## 📊 Results & Baseline Comparison

### Performance Summary

| Model | PR-AUC | ROC-AUC | F1 | Type |
|-------|--------|---------|----|----|
| **XGBoost** (Baseline) | **0.6689** | 0.8881 | 0.6988 | Tabular |
| Random Forest (Baseline) | 0.6583 | 0.8773 | 0.6945 | Tabular |
| **Simple-HHGTN (E7-A3)** ⭐ | **0.5846** | 0.8306 | 0.2584 | **Temporal Hetero GNN (BEST)** |
| **TRD-GraphSAGE (E3)** | **0.5582** | 0.8055 | 0.5860 | **Temporal GNN** |
| MLP (Baseline) | 0.3639 | 0.8297 | 0.4864 | Neural Net |

### Key Finding: "The Temporal Tax" (Reduced via E7!)

Enforcing realistic temporal constraints costs **12.6% PR-AUC** (down from 16.5% after E7 improvements). This quantifies the cost of deployment-ready, leakage-free fraud detection.

**E7 Breakthrough:**
- ⭐ **E7-A3 (Simple-HHGTN)** achieves **0.5846 PR-AUC** (+4.7% over E3)
- Simplified architecture with heterogeneous structure **beats complex models**
- Removed semantic attention → better generalization

**Implications:**
- ✅ **E7-A3** is the new **best temporal GNN** model
- ✅ Heterogeneous graphs help when architecture is properly regularized
- ✅ Simpler aggregation (sum) beats complex attention on small datasets
- 💡 Feature engineering (XGBoost) still leads, but gap narrowing

### Visualizations

<details>
<summary>Click to view comparison charts</summary>

![Model Comparison](reports/plots/model_comparison_top5.png)
![Performance Gap](reports/plots/performance_gap.png)
![PR vs ROC](reports/plots/pr_roc_scatter.png)

</details>

**Full Analysis:** See [COMPARISON_REPORT.md](reports/COMPARISON_REPORT.md)

### Baseline Source

This project extends: [Revisiting-GNNs-FraudDetection](https://github.com/BhaveshBytess/Revisiting-GNNs-FraudDetection)  
Commit: `ccab3f9` | Date: Nov 9, 2025

## 🧪 Project Status

✅ **E1 - Bootstrap & Provenance:** Complete  
✅ **E2 - TRD Sampler MVP:** Complete (7/7 tests passing)  
✅ **E3 - TRD-GraphSAGE Training:** Complete (Kaggle results acquired)  
✅ **E4 - Comparison Report:** Complete  
✅ **E5 - Heterogeneous Graph Construction:** Complete (303K nodes, 422K edges)  
✅ **E6 - TRD-HHGTN (Complex):** Complete (negative result documented)  
✅ **E7 - Ablation Study:** **COMPLETE** - Found improved model! ⭐  
⏳ **E8-E9:** Available for future enhancements

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built upon the Elliptic++ dataset and baseline GNN implementations from the original fraud detection project.
