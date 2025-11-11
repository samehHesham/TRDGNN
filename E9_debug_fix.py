# Quick fix for E9 - Add this cell right after loading hetero_data

# Debug: Check actual node and edge type names
print("Debugging hetero_data structure...")
print(f"Node types: {hetero_data.node_types}")
print(f"Edge types: {hetero_data.edge_types}")

# The node types should be correct, but let's verify
# Access with actual names from the data
node_types = hetero_data.node_types
edge_types = hetero_data.edge_types

print(f"\nNode type details:")
for nt in node_types:
    print(f"  {nt}: {hetero_data[nt].x.shape}")

print(f"\nEdge type details:")
for et in edge_types:
    print(f"  {et}: {hetero_data[et].edge_index.shape}")

# Map to expected names (in case they're named differently)
# E5 used: 'transaction', 'address'
# Edge types: ('transaction', 'tx_to_tx', 'transaction'), etc.

# If node types are named differently, create mapping
tx_type = [nt for nt in node_types if 'tx' in nt.lower() or 'transaction' in nt.lower()][0]
addr_type = [nt for nt in node_types if 'addr' in nt.lower()][0]

print(f"\nMapped types:")
print(f"  Transaction type: '{tx_type}'")
print(f"  Address type: '{addr_type}'")
