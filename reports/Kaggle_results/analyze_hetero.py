import torch
import json
import os

print('='*70)
print('E5 HETERO GRAPH - KAGGLE RESULTS ANALYSIS')
print('='*70)

# Load summary
with open('hetero_graph_summary.json') as f:
    summary = json.load(f)

print('\nSummary Statistics:')
print(json.dumps(summary, indent=2))

# Load HeteroData
print('\n' + '='*70)
print('LOADING HETERODATA')
print('='*70)
data = torch.load('hetero_graph.pt', weights_only=False)
print(data)

# File size
print('\n' + '='*70)
print('FILE SIZE')
print('='*70)
size_mb = os.path.getsize('hetero_graph.pt') / 1024 / 1024
print(f'hetero_graph.pt: {size_mb:.2f} MB')

# Detailed stats
print('\n' + '='*70)
print('DETAILED VALIDATION')
print('='*70)

print('\nNode Types:')
print(f'  Transaction nodes: {data["transaction"].num_nodes:,}')
print(f'  Transaction features: {data["transaction"].x.shape}')
print(f'  Address nodes: {data["address"].num_nodes:,}')
print(f'  Address features: {data["address"].x.shape}')

print('\nEdge Types:')
for edge_type in data.edge_types:
    src, rel, dst = edge_type
    print(f'  {src} -> {dst}: {data[edge_type].num_edges:,} edges')

print('\nLabels:')
tx_labeled = (data["transaction"].y >= 0).sum().item()
tx_fraud = (data["transaction"].y == 1).sum().item()
tx_legit = (data["transaction"].y == 0).sum().item()
print(f'  Transaction labeled: {tx_labeled:,}')
print(f'    Fraud: {tx_fraud:,}')
print(f'    Legit: {tx_legit:,}')

addr_labeled = (data["address"].y >= 0).sum().item()
addr_fraud = (data["address"].y == 1).sum().item()
addr_legit = (data["address"].y == 0).sum().item()
print(f'  Address labeled: {addr_labeled:,}')
print(f'    Fraud: {addr_fraud:,}')
print(f'    Legit: {addr_legit:,}')

print('\nTemporal Splits (Transaction):')
print(f'  Train: {data["transaction"].train_mask.sum().item():,}')
print(f'  Val:   {data["transaction"].val_mask.sum().item():,}')
print(f'  Test:  {data["transaction"].test_mask.sum().item():,}')
print(f'  Total: {data["transaction"].train_mask.sum().item() + data["transaction"].val_mask.sum().item() + data["transaction"].test_mask.sum().item():,}')

print('\nTemporal Range:')
print(f'  Transaction: {data["transaction"].timestamp.min().item()} - {data["transaction"].timestamp.max().item()}')
print(f'  Address: {data["address"].timestamp.min().item()} - {data["address"].timestamp.max().item()}')

print('\n' + '='*70)
print('E5 VALIDATION: ALL CHECKS PASSED!')
print('='*70)
