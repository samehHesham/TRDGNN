# E9: Wallet Fusion - Implementation Plan

**Date:** November 11, 2025  
**Status:** Ready to implement  
**Prerequisites:** E7-A3 model complete (0.5846 PR-AUC)  
**Goal:** Combine GNN embeddings with tabular features for hybrid fraud detection

---

## 🎯 Objective

Demonstrate that **GNN embeddings + tabular features > either alone** by combining:
- **Graph structure** learned by E7-A3 (Simple-HHGTN)
- **Tabular features** from wallet/address data
- **XGBoost** as fusion model (industry-standard ensemble)

**Hypothesis:** GNN captures relational patterns, tabular captures statistical patterns → fusion captures both

---

## 📊 High-Level Approach

```
┌─────────────────────────────────────────────────────┐
│                  E9 Wallet Fusion                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Step 1: Extract E7-A3 Embeddings                  │
│  ├─ Transaction embeddings [N_tx, 128]             │
│  └─ Address embeddings [N_addr, 128]               │
│                                                      │
│  Step 2: Load Tabular Features                     │
│  ├─ Transaction features (AF1-AF93) [N_tx, 93]     │
│  └─ Address features [N_addr, 52]                   │
│                                                      │
│  Step 3: Create Fusion Features                    │
│  ├─ Transaction: [embeddings | tabular] [N_tx, 221]│
│  └─ Address: [embeddings | tabular] [N_addr, 180]  │
│                                                      │
│  Step 4: Train Three Models                        │
│  ├─ XGBoost (tabular only)                         │
│  ├─ XGBoost (embeddings only)                      │
│  └─ XGBoost (fusion) ⭐ EXPECTED BEST              │
│                                                      │
│  Step 5: Evaluate & Compare                        │
│  └─ PR-AUC, ROC-AUC, F1 for all three              │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Implementation Steps

### Step 1: Extract E7-A3 Embeddings

**Goal:** Get learned representations from trained Simple-HHGTN model

**Implementation:**

```python
# Load trained E7-A3 model
import torch
from src.models.simple_hhgtn import SimpleHHGTN

# Load model checkpoint
checkpoint = torch.load('reports/Kaggle_results/a3_best.pt')
model = SimpleHHGTN(...)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Load heterogeneous graph
hetero_data = torch.load('data/hetero_graph.pt')

# Extract embeddings (forward pass without classifier)
with torch.no_grad():
    embeddings = model.get_embeddings(hetero_data)
    
    # Transaction embeddings: [203,769, 128]
    tx_embeddings = embeddings['transaction'].cpu().numpy()
    
    # Address embeddings: [100,000, 128]
    addr_embeddings = embeddings['address'].cpu().numpy()

# Save embeddings
np.save('reports/Kaggle_results/e9_tx_embeddings.npy', tx_embeddings)
np.save('reports/Kaggle_results/e9_addr_embeddings.npy', addr_embeddings)
```

**Note:** Need to modify Simple-HHGTN to expose embeddings before classifier:

```python
class SimpleHHGTN(nn.Module):
    # ... existing code ...
    
    def get_embeddings(self, x_dict, edge_index_dict):
        """Extract embeddings before classification"""
        # Project inputs
        x_dict = {
            'tx': self.tx_proj(x_dict['tx']),
            'addr': self.addr_proj(x_dict['addr'])
        }
        
        # Message passing
        for conv in self.convs:
            x_dict = conv(x_dict, edge_index_dict)
            x_dict = {key: F.relu(x).dropout(0.4) for key, x in x_dict.items()}
        
        # Return embeddings (before classifier)
        return x_dict
```

---

### Step 2: Load Tabular Features

**Goal:** Load original features for transactions and addresses

**Implementation:**

```python
import pandas as pd

# Load transaction features
tx_features_df = pd.read_csv('data/Elliptic++ Dataset/txs_features.csv')
tx_features = tx_features_df.iloc[:, 2:95].values  # AF1-AF93 (skip txId, Time step)

# Load address features
addr_features_df = pd.read_csv('data/Elliptic++ Dataset/wallets_features.csv')
addr_features = addr_features_df.iloc[:, 2:].values  # 52 features

# Align with graph node order (use node mappings from E5)
with open('reports/Kaggle_results/node_mappings_sample.json') as f:
    mappings = json.load(f)

# Reorder features to match graph indices
tx_features_aligned = align_features(tx_features, mappings['transaction'])
addr_features_aligned = align_features(addr_features, mappings['address'])

print(f"Transaction features: {tx_features_aligned.shape}")  # [203,769, 93]
print(f"Address features: {addr_features_aligned.shape}")      # [100,000, 52]
```

---

### Step 3: Create Fusion Features

**Goal:** Concatenate embeddings with tabular features

**Implementation:**

```python
import numpy as np

# Load embeddings from Step 1
tx_embeddings = np.load('reports/Kaggle_results/e9_tx_embeddings.npy')
addr_embeddings = np.load('reports/Kaggle_results/e9_addr_embeddings.npy')

# Normalize features (fit on train, apply to all)
from sklearn.preprocessing import StandardScaler

# Transaction features
tx_scaler = StandardScaler()
tx_features_norm = tx_scaler.fit_transform(tx_features_aligned[train_mask])
tx_features_norm_all = tx_scaler.transform(tx_features_aligned)

# Address features
addr_scaler = StandardScaler()
addr_features_norm = addr_scaler.fit_transform(addr_features_aligned[addr_train_mask])
addr_features_norm_all = addr_scaler.transform(addr_features_aligned)

# Create fusion features
tx_fusion = np.concatenate([tx_embeddings, tx_features_norm_all], axis=1)  # [N, 128+93=221]
addr_fusion = np.concatenate([addr_embeddings, addr_features_norm_all], axis=1)  # [N, 128+52=180]

print(f"Transaction fusion features: {tx_fusion.shape}")
print(f"Address fusion features: {addr_fusion.shape}")
```

---

### Step 4: Train Three Models (Transaction-Level)

**Goal:** Compare tabular-only, embedding-only, and fusion approaches

**Implementation:**

```python
import xgboost as xgb
from sklearn.metrics import precision_recall_curve, auc, roc_auc_score, f1_score

# Load labels and splits
labels = ...  # Transaction labels (1=fraud, 2=licit)
train_mask, val_mask, test_mask = ...  # From E3 splits

# Prepare labels (convert to binary: 1=fraud, 0=licit)
y = (labels == 1).astype(int)

# Calculate class weights
pos_weight = (y[train_mask] == 0).sum() / (y[train_mask] == 1).sum()

# XGBoost parameters
xgb_params = {
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'scale_pos_weight': pos_weight,
    'random_state': 42,
    'tree_method': 'hist',
    'device': 'cuda'  # if GPU available
}

# Model 1: Tabular Only (AF1-AF93)
print("Training Model 1: Tabular Only")
model_tabular = xgb.XGBClassifier(**xgb_params)
model_tabular.fit(
    tx_features_norm_all[train_mask], 
    y[train_mask],
    eval_set=[(tx_features_norm_all[val_mask], y[val_mask])],
    verbose=False
)

# Predictions
pred_tabular = model_tabular.predict_proba(tx_features_norm_all[test_mask])[:, 1]

# Model 2: Embeddings Only (128-dim from GNN)
print("Training Model 2: Embeddings Only")
model_embeddings = xgb.XGBClassifier(**xgb_params)
model_embeddings.fit(
    tx_embeddings[train_mask], 
    y[train_mask],
    eval_set=[(tx_embeddings[val_mask], y[val_mask])],
    verbose=False
)

pred_embeddings = model_embeddings.predict_proba(tx_embeddings[test_mask])[:, 1]

# Model 3: Fusion (221-dim: embeddings + tabular)
print("Training Model 3: Fusion")
model_fusion = xgb.XGBClassifier(**xgb_params)
model_fusion.fit(
    tx_fusion[train_mask], 
    y[train_mask],
    eval_set=[(tx_fusion[val_mask], y[val_mask])],
    verbose=False
)

pred_fusion = model_fusion.predict_proba(tx_fusion[test_mask])[:, 1]
```

---

### Step 5: Evaluate & Compare

**Goal:** Compute metrics and visualize results

**Implementation:**

```python
from sklearn.metrics import precision_recall_curve, auc, roc_auc_score, f1_score, roc_curve
import matplotlib.pyplot as plt

# Ground truth
y_test = y[test_mask]

# Function to compute metrics
def compute_metrics(y_true, y_pred_proba):
    # PR-AUC
    precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
    pr_auc = auc(recall, precision)
    
    # ROC-AUC
    roc_auc = roc_auc_score(y_true, y_pred_proba)
    
    # F1 (at optimal threshold)
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    y_pred_binary = (y_pred_proba >= optimal_threshold).astype(int)
    f1 = f1_score(y_true, y_pred_binary)
    
    return {
        'pr_auc': pr_auc,
        'roc_auc': roc_auc,
        'f1': f1,
        'threshold': optimal_threshold
    }

# Compute metrics for all three models
results = {
    'tabular_only': compute_metrics(y_test, pred_tabular),
    'embeddings_only': compute_metrics(y_test, pred_embeddings),
    'fusion': compute_metrics(y_test, pred_fusion)
}

# Print results
print("\n" + "="*60)
print("E9 WALLET FUSION RESULTS (Transaction-Level)")
print("="*60)
for model_name, metrics in results.items():
    print(f"\n{model_name.upper()}:")
    print(f"  PR-AUC:   {metrics['pr_auc']:.4f}")
    print(f"  ROC-AUC:  {metrics['roc_auc']:.4f}")
    print(f"  F1:       {metrics['f1']:.4f}")

# Calculate improvements
fusion_vs_tabular = (results['fusion']['pr_auc'] - results['tabular_only']['pr_auc']) / results['tabular_only']['pr_auc'] * 100
fusion_vs_embeddings = (results['fusion']['pr_auc'] - results['embeddings_only']['pr_auc']) / results['embeddings_only']['pr_auc'] * 100

print(f"\nFUSION IMPROVEMENT:")
print(f"  vs Tabular:    {fusion_vs_tabular:+.1f}%")
print(f"  vs Embeddings: {fusion_vs_embeddings:+.1f}%")

# Save results
import json
with open('reports/Kaggle_results/e9_fusion_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

### Step 6: Visualization

**Goal:** Create comparison plots

**Implementation:**

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 5)

# Create comparison bar chart
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

models = ['Tabular\nOnly', 'Embeddings\nOnly', 'Fusion']
metrics_names = ['PR-AUC', 'ROC-AUC', 'F1']

for idx, metric_key in enumerate(['pr_auc', 'roc_auc', 'f1']):
    values = [
        results['tabular_only'][metric_key],
        results['embeddings_only'][metric_key],
        results['fusion'][metric_key]
    ]
    
    bars = axes[idx].bar(models, values, color=['#3498db', '#e74c3c', '#2ecc71'])
    axes[idx].set_ylabel(metrics_names[idx], fontsize=12)
    axes[idx].set_ylim([0, 1])
    axes[idx].set_title(f'{metrics_names[idx]} Comparison', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        axes[idx].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                      f'{val:.4f}', ha='center', va='bottom', fontsize=10)
    
    # Highlight best
    best_idx = np.argmax(values)
    bars[best_idx].set_edgecolor('gold')
    bars[best_idx].set_linewidth(3)

plt.tight_layout()
plt.savefig('reports/Kaggle_results/e9_fusion_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Create PR and ROC curves
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# PR Curves
for name, pred, color, label in [
    ('tabular_only', pred_tabular, '#3498db', 'Tabular Only'),
    ('embeddings_only', pred_embeddings, '#e74c3c', 'Embeddings Only'),
    ('fusion', pred_fusion, '#2ecc71', 'Fusion')
]:
    precision, recall, _ = precision_recall_curve(y_test, pred)
    pr_auc = auc(recall, precision)
    axes[0].plot(recall, precision, color=color, lw=2, 
                label=f'{label} (PR-AUC={pr_auc:.4f})')

axes[0].set_xlabel('Recall', fontsize=12)
axes[0].set_ylabel('Precision', fontsize=12)
axes[0].set_title('Precision-Recall Curves', fontsize=14, fontweight='bold')
axes[0].legend(loc='best')
axes[0].grid(True, alpha=0.3)

# ROC Curves
for name, pred, color, label in [
    ('tabular_only', pred_tabular, '#3498db', 'Tabular Only'),
    ('embeddings_only', pred_embeddings, '#e74c3c', 'Embeddings Only'),
    ('fusion', pred_fusion, '#2ecc71', 'Fusion')
]:
    fpr, tpr, _ = roc_curve(y_test, pred)
    roc_auc = auc(fpr, tpr)
    axes[1].plot(fpr, tpr, color=color, lw=2, 
                label=f'{label} (ROC-AUC={roc_auc:.4f})')

axes[1].plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.3)
axes[1].set_xlabel('False Positive Rate', fontsize=12)
axes[1].set_ylabel('True Positive Rate', fontsize=12)
axes[1].set_title('ROC Curves', fontsize=14, fontweight='bold')
axes[1].legend(loc='best')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('reports/Kaggle_results/e9_fusion_curves.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nPlots saved:")
print("  - reports/Kaggle_results/e9_fusion_comparison.png")
print("  - reports/Kaggle_results/e9_fusion_curves.png")
```

---

## 📦 Deliverables

### Code
- [ ] `src/models/simple_hhgtn.py` - Add `get_embeddings()` method
- [ ] `notebooks/E9_wallet_fusion.ipynb` - Complete implementation

### Results
- [ ] `e9_tx_embeddings.npy` - Transaction embeddings [203K, 128]
- [ ] `e9_addr_embeddings.npy` - Address embeddings [100K, 128]
- [ ] `e9_fusion_results.json` - All metrics
- [ ] `e9_fusion_comparison.png` - Bar chart comparison
- [ ] `e9_fusion_curves.png` - PR/ROC curves
- [ ] `e9_tabular_best.pkl` - Trained XGBoost (tabular)
- [ ] `e9_embeddings_best.pkl` - Trained XGBoost (embeddings)
- [ ] `e9_fusion_best.pkl` - Trained XGBoost (fusion) ⭐

### Documentation
- [ ] Update `COMPARISON_REPORT.md` with E9 section
- [ ] Update `README.md` with E9 results
- [ ] Create `E9_WALLET_FUSION_DOCUMENTATION.md`

---

## 🎯 Success Criteria

### Technical
- ✅ All three models train without errors
- ✅ Fusion model achieves highest PR-AUC
- ✅ Results are reproducible (seed=42)

### Scientific
- ✅ Fusion outperforms individual approaches
- ✅ Clear demonstration of complementary information
- ✅ Insights documented about what each modality captures

### Expected Results (Hypotheses)
- **Tabular Only:** ~0.60-0.63 PR-AUC (good, similar to XGBoost baseline)
- **Embeddings Only:** ~0.55-0.58 PR-AUC (GNN captures structure)
- **Fusion:** ~0.63-0.66 PR-AUC (best, combines both) ⭐

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Embeddings Don't Improve Performance
**Symptom:** Fusion ≈ Tabular Only  
**Solution:** 
- Check if GNN actually learned meaningful patterns (visualize embeddings with t-SNE)
- Try different fusion strategies (early fusion vs late fusion)
- Document as finding: "GNN doesn't add value beyond tabular"

### Issue 2: Memory Issues
**Symptom:** OOM when concatenating features  
**Solution:**
- Use memory-mapped arrays
- Process in batches
- Use float32 instead of float64

### Issue 3: XGBoost Overfits Fusion Features
**Symptom:** Train PR-AUC >> Test PR-AUC  
**Solution:**
- Increase regularization (max_depth=4, min_child_weight=5)
- Use early stopping with validation set
- Add feature dropout

---

## 📊 Timeline

**Estimated Time:** 1-2 days

### Day 1 (4-6 hours)
- [ ] Modify Simple-HHGTN to expose embeddings
- [ ] Extract embeddings from E7-A3 model
- [ ] Load and align tabular features
- [ ] Create fusion features
- [ ] Train first two models (tabular, embeddings)

### Day 2 (3-4 hours)
- [ ] Train fusion model
- [ ] Compute all metrics
- [ ] Create visualizations
- [ ] Write documentation
- [ ] Update main reports

---

## 🎓 Expected Insights

### What E9 Will Show

**If Fusion Wins (Expected):**
- GNN captures **relational patterns** (fraud rings, suspicious flows)
- Tabular captures **statistical patterns** (transaction amounts, fees)
- Combined = **best of both worlds**
- Practical takeaway: Use hybrid models in production

**If Tabular Wins:**
- Feature engineering > learned representations for this task
- GNN doesn't capture additional value beyond aggregate features
- Supports E3/E6/E7 finding: engineered features are powerful
- Still valuable finding: documents when NOT to use GNNs

**If Embeddings Win (Unlikely):**
- Graph structure dominates statistical features
- Would be surprising given E3 results
- Would suggest we should revisit feature selection

---

## 📝 Integration with Existing Work

### How E9 Fits Into Overall Story

**E1-E3:** Baseline temporal GNN  
**E5-E6:** Complex heterogeneous attempt (failed)  
**E7:** Simplified heterogeneous (success, +4.1%)  
**E9:** Hybrid approach showing complementary value ⭐

**Narrative:**
> "After finding the best temporal GNN architecture (E7-A3), we investigate whether GNN embeddings complement tabular features. E9 demonstrates that fusion models combining graph structure and statistical patterns achieve the best performance, validating the value of both modalities."

---

## 🎉 What Success Looks Like

**Best Case Scenario:**
```
Tabular Only:      0.620 PR-AUC
Embeddings Only:   0.570 PR-AUC  
Fusion:            0.655 PR-AUC  ⭐ (+5.6% vs tabular)

Gap to XGBoost baseline (0.669): Only 2.1%!
```

**Conclusion:**
- Fusion nearly matches unrealistic baseline
- GNN adds value when combined with features
- Hybrid approach recommended for production

---

**Ready to implement? Let me know and I'll help create the Kaggle notebook!** 🚀

