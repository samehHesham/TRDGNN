# Heterogeneous Graph Data Structure Analysis

**Date:** November 10, 2025  
**Purpose:** Pre-analysis for HHGTN+TRD Extension (E5-E9)

---

## 📊 Dataset Overview

### File Sizes

| File | Size | Type |
|------|------|------|
| `txs_features.csv` | 662.6 MB | Transaction node features |
| `wallets_features.csv` | 578.4 MB | Wallet/Address node features |
| `wallets_features_classes_combined.csv` | 580.8 MB | Combined wallet data |
| `AddrAddr_edgelist.csv` | 191.3 MB | Address-to-Address edges |
| `TxAddr_edgelist.csv` | 35.0 MB | Transaction-to-Address edges |
| `wallets_classes.csv` | 29.0 MB | Wallet labels |
| `AddrTx_edgelist.csv` | 20.3 MB | Address-to-Transaction edges |
| `txs_edgelist.csv` | 4.3 MB | Transaction-to-Transaction edges |
| `txs_classes.csv` | 2.3 MB | Transaction labels |

**Total Dataset Size:** ~2.1 GB

---

## 🔍 Graph Structure

### Node Types (3 types)

#### 1. Transaction Nodes
- **Count:** 203,769 transactions
- **Features:** 184 columns
  - Time step (temporal)
  - Local features (1-93): Transaction-specific attributes
  - Aggregate features (1-72): Neighbor aggregations
  - Graph features: degrees, BTC amounts, fees, etc.
- **Labels:** 3 classes (1=illicit, 2=licit, 3=unknown)
- **Sample IDs:** 230425980, 232022460, 232438397

#### 2. Address Nodes
- **Count:** 822,942 addresses
- **Features:** 52 columns
  - Time step
  - Transaction counts (sender/receiver)
  - Temporal features (lifetime, blocks)
  - BTC statistics (sent/received/transacted)
  - Fee statistics
  - Inter-transaction timing features
- **Labels:** 3 classes (1=illicit, 2=licit, 3=unknown)
- **Sample IDs:** "111112TykSw72ztDN2WJger4cynzWYC5w", "1111DAYXhoxZx2tsRnzimfozo783x1yC2"

#### 3. Wallet Nodes (Same as Addresses)
- Wallets and addresses appear to be the same entity
- Separate files provided for convenience
- **Note:** May need to consolidate address/wallet terminology

### Edge Types (4 types)

#### 1. Transaction → Transaction
- **File:** `txs_edgelist.csv`
- **Count:** 234,355 edges
- **Meaning:** Payment flows between transactions
- **Columns:** [txId1, txId2]
- **Directed:** Yes

#### 2. Address → Transaction
- **File:** `AddrTx_edgelist.csv`
- **Count:** Unknown (20.3 MB)
- **Meaning:** Address sends to transaction (input)
- **Directed:** Yes

#### 3. Transaction → Address
- **File:** `TxAddr_edgelist.csv`
- **Count:** Unknown (35.0 MB)
- **Meaning:** Transaction pays to address (output)
- **Directed:** Yes

#### 4. Address → Address
- **File:** `AddrAddr_edgelist.csv`
- **Count:** Unknown (191.3 MB)
- **Meaning:** Direct address-to-address connections
- **Directed:** Probably yes

---

## 🕐 Temporal Information

### Timestamps Available
- **Transaction timestamps:** `Time step` column (49 unique timesteps from E3 results)
- **Address timestamps:** `Time step` column (appears to be last active timestep)
- **Temporal range:** Covers Bitcoin blockchain history in 49-step discretization

### TRD Compatibility
- ✅ Temporal information present for all node types
- ✅ Can enforce `time(neighbor) ≤ time(target)` constraint
- ✅ Existing TRD sampler can be extended to heterogeneous edges

---

## 🎯 Graph Statistics

### Transaction Graph
- **Nodes:** 203,769
- **Edges (tx→tx):** 234,355
- **Average degree:** ~2.3 (from E3 results)
- **Labeled:** ~24% (49,000 / 203,769)

### Address Graph
- **Nodes:** 822,942
- **Edges (addr→addr):** Est. ~5-10 million (based on file size)
- **Much larger than transaction graph**

### Bipartite Connections
- **addr→tx edges:** Est. ~500K-1M
- **tx→addr edges:** Est. ~1-2M
- **These connect the two graph layers**

---

## 💡 Heterogeneous Graph Schema

```
Elliptic++ Heterogeneous Graph
├── Node Types
│   ├── Transaction (203K nodes, 184 features)
│   ├── Address (823K nodes, 52 features)
│   └── (Wallet = Address alias)
│
└── Edge Types
    ├── tx → tx (234K edges)
    ├── addr → tx (hundreds of thousands)
    ├── tx → addr (1-2 million)
    └── addr → addr (millions)
```

### Semantic Relations

1. **tx → tx:** Transaction flow (BTC payment chain)
2. **addr → tx:** Address inputs to transaction (sender)
3. **tx → addr:** Transaction outputs to address (receiver)
4. **addr → addr:** Direct address connections (inferred from shared txs)

---

## 🔬 Feature Analysis

### Transaction Features (184 total)
- **Local (93):** Transaction-specific (amounts, fees, sizes)
- **Aggregate (72):** Pre-computed neighbor statistics
- **Graph (19):** Degrees, BTC flows, address counts

**For HHGTN:** Use Local features only to avoid double-encoding (same strategy as E3)

### Address Features (52 total)
- **Temporal:** Lifetime, block ranges, timesteps
- **Activity:** Transaction counts (sent/received)
- **Financial:** BTC amounts, fees, transaction rates
- **Behavioral:** Inter-transaction timing, address interaction patterns

**For HHGTN:** Use all address features (not pre-aggregated like tx aggregate features)

---

## ⚠️ Implementation Considerations

### Challenges

1. **Scale Mismatch:**
   - Addresses (823K) >> Transactions (204K)
   - 4:1 ratio - need efficient sampling

2. **Memory:**
   - Full graph: ~2GB on disk
   - In-memory PyG HeteroData: Est. 3-5GB
   - Need to verify Kaggle memory limits (16GB available)

3. **Edge Type Imbalance:**
   - addr→addr edges likely dominate (millions)
   - tx→tx edges are sparse (234K)
   - May need edge type sampling strategies

4. **Temporal Complexity:**
   - Need timestamps for all node types
   - TRD sampler must handle heterogeneous temporal constraints
   - Each edge type needs separate temporal filtering

### Opportunities

1. **Rich Heterogeneity:**
   - Real multi-relational structure (not synthetic)
   - Semantic meaning to each edge type
   - Natural bipartite structure (tx ↔ addr)

2. **Feature Complementarity:**
   - Transaction features: local, per-tx
   - Address features: behavioral, aggregate
   - Can learn complementary representations

3. **Fraud Patterns:**
   - Fraud may manifest differently in different edge types
   - Address connections may reveal wallet clusters
   - Transaction flows show money movement

---

## 🚀 Recommendations for E5

### Data Loading Strategy

1. **Load transactions first** (smaller, already familiar)
2. **Sample addresses** initially (maybe top 100K most active)
3. **Load edges incrementally** by type
4. **Build PyG HeteroData** with node type mapping

### Initial Experiments

**MVP Graph for E5:**
- All transactions (204K)
- Top 100K addresses (most active)
- All tx→tx edges (234K)
- Sample addr↔tx edges (connecting to top addresses)
- Skip addr→addr initially (too large)

**Full Graph (if memory allows):**
- All nodes, all edges
- Test on Kaggle GPU instance (16GB RAM)

### TRD Sampler Extension

Need to modify sampler to handle:
```python
# Current: homogeneous
sampled = sample(edge_index, timestamps, targets)

# New: heterogeneous
sampled = sample(
    edge_dict={'tx-tx': edge_index_tx, 'addr-tx': edge_index_addr_tx, ...},
    timestamps_dict={'tx': ts_tx, 'addr': ts_addr},
    targets={'tx': target_txs}
)
```

---

## 📋 Next Steps (Option B)

Create detailed planning document for:
- E5: HeteroData construction
- E6: TRD-HHGTN architecture
- E7: Ablation study design
- E8: Hypergraph extension
- E9: Wallet fusion strategy

---

**Analysis Complete:** November 10, 2025  
**Status:** Ready for Option B (Planning) → Option A (Implementation)
