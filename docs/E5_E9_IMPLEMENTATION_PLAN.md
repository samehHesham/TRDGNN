# E5-E9 Implementation Plan: HHGTN + TRD Extension

**Date:** November 10, 2025  
**Extension:** Direction A - Heterogeneous & Temporal Graph Learning  
**Baseline:** TRD-GraphSAGE (E1-E4 Complete)

---

## 🎯 Executive Summary

This plan extends the TRD-GraphSAGE baseline to handle **heterogeneous multi-relational graphs** with temporal constraints. We will implement TRD-HHGTN (Heterogeneous & Temporal GNN) using the full Elliptic++ dataset including addresses, transactions, and multiple relation types.

**Key Innovation:** Combine semantic attention over relation types with TRD temporal sampling for deployment-ready heterogeneous fraud detection.

---

## 📊 Current State (E1-E4 Complete)

✅ **Achievements:**
- TRD sampler: Zero temporal leakage verified (7/7 tests)
- TRD-GraphSAGE: PR-AUC 0.5582 (baseline established)
- Comparison report: "Temporal tax" quantified at 16.5%
- Clean codebase with comprehensive documentation

**Infrastructure Ready:**
- `src/data/trd_sampler.py` - Can be extended for hetero graphs
- `tests/test_trd_sampler.py` - Test framework established
- Training pipeline - Kaggle-ready notebooks
- Evaluation metrics - PR-AUC, ROC-AUC, F1, Recall@K

---

## 🧩 E5: Heterogeneous Graph Construction

### Objective
Build PyG `HeteroData` object from CSV files with proper node/edge type separation and temporal information preservation.

### Implementation Steps

#### 5.1 Create Data Loader

**File:** `src/data/build_hetero_graph.py`

```python
class HeteroGraphBuilder:
    def __init__(self, data_root):
        self.data_root = Path(data_root)
        
    def load_nodes(self):
        # Load transaction nodes
        # Load address nodes  
        # Create node mappings
        
    def load_edges(self):
        # Load tx->tx edges
        # Load addr->tx edges
        # Load tx->addr edges
        # Load addr->addr edges
        
    def build_hetero_data(self):
        # Construct PyG HeteroData
        # Add node features
        # Add edge indices per type
        # Add temporal information
        # Add labels
        # Add train/val/test masks
```

**Key Functions:**
1. `load_transaction_nodes()` - 204K transactions with 93 local features
2. `load_address_nodes()` - 823K addresses with 52 features
3. `load_edges_by_type()` - 4 edge types with temporal filtering
4. `create_temporal_splits()` - Reuse 60/20/20 from E3
5. `validate_hetero_graph()` - Sanity checks (node counts, edge connectivity)

#### 5.2 Handle Scale

**Strategy:**
- **MVP:** Full transactions + top 100K addresses (most active)
- **Full:** All nodes if memory allows (Kaggle has 16GB RAM)
- **Sampling:** Prioritize addresses connected to labeled transactions

#### 5.3 Temporal Integration

**Critical:** Preserve timestamps for ALL nodes
- Transaction timestamps: `Time step` column
- Address timestamps: Last active `Time step`
- Edge timestamps: Inferred from source node timestamp

**TRD Constraint:** For edge (u, v), only include if `time(u) ≤ time(v)`

#### 5.4 Outputs

```
data/
├── hetero_graph.pt (PyG HeteroData object)
├── hetero_graph_summary.json (statistics)
└── node_mappings.json (ID mappings)
```

**Summary JSON:**
```json
{
  "num_nodes": {"transaction": 203769, "address": 100000},
  "num_edges": {
    "tx_to_tx": 234355,
    "addr_to_tx": 487231,
    "tx_to_addr": 612481,
    "addr_to_addr": 0
  },
  "num_labeled": {"transaction": 49000, "address": 15000},
  "temporal_range": [1, 49],
  "feature_dims": {"transaction": 93, "address": 52}
}
```

#### 5.5 Testing

**Test:** `tests/test_hetero_graph.py`
- Verify node counts match CSV files
- Verify edge indices are valid (no out-of-bounds)
- Verify temporal ordering (no future edges)
- Verify feature dimensions
- Verify label distribution

**Success Criteria:**
- HeteroData loads without errors
- All edge types have > 0 edges
- No temporal leakage detected
- Memory usage < 10GB

---

## 🧠 E6: TRD-HHGTN Model

### Objective
Implement heterogeneous GNN with relation-specific transformations and semantic attention, using TRD temporal sampling.

### Architecture

#### 6.1 Model Components

**File:** `src/models/trd_hhgtn.py`

```python
class TRD_HHGTN(nn.Module):
    def __init__(self, node_types, edge_types, hidden_dim=128):
        # Per-node-type input projections
        self.node_projections = ModuleDict({
            ntype: Linear(in_dim, hidden_dim) 
            for ntype, in_dim in node_type_dims.items()
        })
        
        # Per-relation message passing
        self.relation_convs = ModuleList([
            RelationConv(hidden_dim) for _ in edge_types
        ])
        
        # Semantic attention over relations
        self.semantic_attention = SemanticAttention(
            num_relations=len(edge_types),
            hidden_dim=hidden_dim
        })
        
        # Output classifier
        self.classifier = Linear(hidden_dim, 2)
```

**Key Layers:**
1. **Node Projection:** Map different feature spaces to common hidden dim
2. **Relation Conv:** GraphSAGE-style aggregation per edge type
3. **Semantic Attention:** Weight and combine relation-specific embeddings
4. **Classifier:** Binary fraud prediction

#### 6.2 TRD Sampler Extension

**File:** `src/data/hetero_trd_sampler.py`

Extend existing `TRDSampler` to handle heterogeneous graphs:

```python
class HeteroTRDSampler(TRDSampler):
    def sample(self, hetero_data, target_nodes, target_type='transaction'):
        # Sample per edge type
        # Enforce temporal constraints per relation
        # Return HeteroData subgraph
```

**Per-Relation Sampling:**
- For each edge type, apply TRD constraint independently
- Fanout per relation: `{'tx-tx': [15,10], 'addr-tx': [10,5], ...}`
- Aggregate multi-relation neighborhoods

#### 6.3 Training Loop

**Notebook:** `notebooks/03_trd_hhgtn.ipynb`

Key sections:
1. Load HeteroData
2. Initialize TRD-HHGTN model
3. Setup HeteroTRD sampler
4. Training loop (similar to E3)
5. Evaluation on test set
6. Save results

**Loss Function:**
- CrossEntropyLoss on transaction nodes (primary target)
- Optional: Multi-task loss if predicting address labels too

**Optimization:**
- Adam optimizer, lr=0.001
- Early stopping on val PR-AUC
- Train on transaction fraud labels

#### 6.4 Outputs

```
reports/
├── trd_hhgtn_metrics.json
├── trd_hhgtn_pr_roc.png
├── trd_hhgtn_training_history.png
└── checkpoints/trd_hhgtn_best.pt
```

**Success Criteria:**
- Model trains without errors
- Val PR-AUC improves over epochs
- Test PR-AUC > 0.55 (match or beat TRD-GraphSAGE)
- No temporal leakage in sampling

---

## 📈 E7: HHGTN Ablations

### Objective
Measure the contribution of each edge type to model performance.

### Ablation Study Design

**Notebook:** `notebooks/04_hhgtn_ablation.ipynb`

#### Configurations to Test

| Config | Edge Types | Purpose |
|--------|------------|---------|
| 1. tx-only | tx→tx | Baseline (matches E3) |
| 2. tx+bipartite | tx→tx, addr↔tx | Add address context |
| 3. all-no-addr | tx→tx, addr↔tx | Full except addr→addr |
| 4. full | All 4 types | Complete heterogeneous |

#### Metrics per Config
- Train time
- Memory usage
- Test PR-AUC, ROC-AUC, F1
- Δ PR-AUC vs baseline

#### Analysis

**Questions:**
1. Do address connections improve performance?
2. Which edge type contributes most?
3. Is addr→addr necessary or redundant?

**Output:** `reports/hhgtn_ablation_table.csv`

```csv
config,edge_types,pr_auc,roc_auc,f1,delta_pr_auc,train_time_min
tx-only,tx-tx,0.5582,0.8055,0.586,0.0000,12
tx+bipartite,tx-tx;addr-tx;tx-addr,0.5834,0.8123,0.601,0.0252,18
all-no-addr,tx-tx;addr-tx;tx-addr,0.5834,0.8123,0.601,0.0252,18
full,all,0.5912,0.8201,0.614,0.0330,25
```

**Success Criteria:**
- All configs run successfully
- At least one config improves over baseline
- Clear ablation insights documented

---

## 🧪 E8: Hypergraph Head (Optional)

### Objective
Add motif-based hyperedge layer to capture addr-tx-addr patterns.

### Implementation

**File:** `src/models/trd_hyper_head.py`

**Concept:**
- Identify addr→tx→addr motifs (address sends through transaction to another address)
- Create hyperedges connecting (addr1, tx, addr2) triplets
- Add hypergraph message passing layer

**Architecture:**
```python
class HypergraphHead(nn.Module):
    def __init__(self, hidden_dim):
        self.hyperedge_conv = HypergraphConv(hidden_dim)
        
    def forward(self, x, hyperedge_index):
        # Aggregate over hyperedges
        return h_out
```

**Notebook:** `notebooks/05_trd_hypergraph.ipynb`

**Scope:** Single run to demonstrate concept
- Build hyperedge index from motifs
- Train TRD-HHGTN with hypergraph head
- Compare with E6 baseline

**Success Criteria:**
- Runs without errors
- Generates hyperedges successfully
- Performance logged (improvement not required)

---

## 💡 E9: Wallet Fusion

### Objective
Combine HHGTN node embeddings with wallet-level tabular features for hybrid model.

### Implementation

**Notebook:** `notebooks/06_wallet_fusion.ipynb`

#### 9.1 Extract Embeddings

From trained TRD-HHGTN:
```python
# Get final layer embeddings
embeddings = model.get_embeddings(hetero_data)

# Transaction embeddings [N_tx, hidden_dim]
tx_embeds = embeddings['transaction']

# Address embeddings [N_addr, hidden_dim]
addr_embeds = embeddings['address']
```

#### 9.2 Aggregate to Wallet Level

**Strategy:**
- Transactions already have embeddings
- Addresses → Wallets (use address ID as wallet ID)
- Pool multiple transactions per wallet (mean/max)

#### 9.3 Combine Features

```python
# Wallet tabular features (52 dims)
wallet_features = load_wallets_features()

# HHGTN embeddings (128 dims)
wallet_embeddings = addr_embeds

# Concatenate
fusion_features = concat([wallet_features, wallet_embeddings], dim=1)
# Shape: [N_wallets, 52 + 128] = [N_wallets, 180]
```

#### 9.4 Train XGBoost Fusion Model

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    objective='binary:logistic'
)

model.fit(fusion_features[train_mask], labels[train_mask])
predictions = model.predict_proba(fusion_features[test_mask])
```

#### 9.5 Evaluation

Compare 3 approaches:
1. **Tabular only:** Wallet features → XGBoost
2. **GNN only:** HHGTN embeddings → Logistic Regression
3. **Fusion:** Combined → XGBoost

**Metrics:** PR-AUC, ROC-AUC, F1 on wallet-level fraud prediction

**Output:** `reports/wallet_fusion_metrics.json`

```json
{
  "tabular_only": {"pr_auc": 0.62, "roc_auc": 0.85},
  "gnn_only": {"pr_auc": 0.58, "roc_auc": 0.81},
  "fusion": {"pr_auc": 0.67, "roc_auc": 0.87}
}
```

**Success Criteria:**
- Fusion model trains successfully
- Performance on par with or better than individual models
- Clear demonstration of complementary information

---

## 📅 Implementation Timeline

### Phase 1: Foundation (Days 1-2)
- [x] Option C: Data preview complete
- [ ] Option B: Planning document complete ← **Current**
- [ ] Save extension prompt
- [ ] Setup E5 branch

### Phase 2: E5 (Days 3-4)
- [ ] Implement `build_hetero_graph.py`
- [ ] Test on small sample
- [ ] Build full HeteroData
- [ ] Write tests
- [ ] Verify TRD compatibility

### Phase 3: E6 (Days 5-7)
- [ ] Extend TRD sampler for heterogeneous
- [ ] Implement TRD-HHGTN model
- [ ] Create training notebook
- [ ] Train and evaluate
- [ ] Save results

### Phase 4: E7 (Day 8)
- [ ] Create ablation notebook
- [ ] Run 4 configurations
- [ ] Analyze results
- [ ] Generate comparison table

### Phase 5: E8-E9 (Days 9-10)
- [ ] Optional: Hypergraph experiment
- [ ] Wallet fusion implementation
- [ ] Final comparison report
- [ ] Update README

---

## 📊 Success Metrics

### Technical Metrics

| Metric | Target | Baseline (E3) |
|--------|--------|---------------|
| **Test PR-AUC** | > 0.56 | 0.5582 |
| Test ROC-AUC | > 0.81 | 0.8055 |
| Test F1 | > 0.59 | 0.5860 |
| Training time | < 60 min | ~15 min (homog) |
| Memory usage | < 12 GB | ~8 GB |

### Scientific Metrics

- [ ] Quantify benefit of heterogeneous relations
- [ ] Identify most valuable edge type
- [ ] Demonstrate address features improve tx prediction
- [ ] Show fusion > individual models

### Deliverables Checklist

#### Code
- [ ] `src/data/build_hetero_graph.py`
- [ ] `src/data/hetero_trd_sampler.py`
- [ ] `src/models/trd_hhgtn.py`
- [ ] `src/models/trd_hyper_head.py` (optional)
- [ ] `tests/test_hetero_graph.py`
- [ ] `tests/test_hetero_trd_sampler.py`

#### Notebooks
- [ ] `notebooks/03_trd_hhgtn.ipynb`
- [ ] `notebooks/04_hhgtn_ablation.ipynb`
- [ ] `notebooks/05_trd_hypergraph.ipynb` (optional)
- [ ] `notebooks/06_wallet_fusion.ipynb`

#### Results
- [ ] `data/hetero_graph.pt`
- [ ] `data/hetero_graph_summary.json`
- [ ] `reports/trd_hhgtn_metrics.json`
- [ ] `reports/hhgtn_ablation_table.csv`
- [ ] `reports/wallet_fusion_metrics.json`
- [ ] `reports/metrics_summary_with_hhgtn.csv`

#### Documentation
- [ ] Update README with E5-E9 results
- [ ] Create HHGTN comparison report
- [ ] Update PROJECT_SPEC to v3.1
- [ ] Document lessons learned

---

## ⚠️ Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Memory overflow | High | Start with MVP graph (100K addresses) |
| Training time too long | Medium | Use mini-batch sampling if needed |
| Heterogeneous sampler bugs | High | Extensive testing, gradual complexity |
| No performance improvement | Low | Document negative results (still valuable) |

### Scientific Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Heterogeneous adds no value | Medium | Ablations will reveal this; negative result OK |
| Temporal constraints too restrictive | Low | Already quantified in E3 ("temporal tax") |
| Address features not informative | Medium | Fusion experiment will test this |

---

## 🎯 Definition of Done

### E5 Complete When:
- [x] HeteroData builds successfully
- [x] All node/edge types present
- [x] Temporal constraints verified
- [x] Tests passing
- [x] Summary JSON generated

### E6 Complete When:
- [x] TRD-HHGTN trains without errors
- [x] Test PR-AUC computed and logged
- [x] Results comparable to E3 baseline
- [x] Checkpoint saved

### E7 Complete When:
- [x] 4 ablation configs run
- [x] Comparison table generated
- [x] Insights documented

### E8 Complete When (Optional):
- [x] Hypergraph runs once successfully
- [x] Results logged

### E9 Complete When:
- [x] Fusion model trained
- [x] 3-way comparison complete
- [x] Insights documented

### Overall Extension Complete When:
- [x] All E5-E9 (or E5-E7+E9) complete
- [x] Results merged with baseline metrics
- [x] README updated
- [x] Final report written

---

## 📚 References

### Existing Codebase
- `src/data/trd_sampler.py` - Extend for heterogeneous
- `src/models/trd_graphsage.py` - Reference architecture
- `notebooks/01_trd_graphsage_train.ipynb` - Training template

### External
- PyG HeteroData documentation
- HHGTN paper (if available)
- Temporal heterogeneous GNN literature

---

**Plan Created:** November 10, 2025  
**Status:** Ready for Option A (Implementation)  
**Next:** Save extension prompt → Start E5

