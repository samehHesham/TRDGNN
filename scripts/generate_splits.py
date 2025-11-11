"""Generate splits.json from Elliptic++ dataset for E9."""
import pandas as pd
import numpy as np
import json

def create_temporal_splits(timestamps, train_frac=0.6, val_frac=0.2, test_frac=0.2):
    """Create temporal splits based on timestamps."""
    sorted_times = np.sort(np.unique(timestamps))
    n_timesteps = len(sorted_times)
    
    train_end_idx = int(n_timesteps * train_frac)
    val_end_idx = int(n_timesteps * (train_frac + val_frac))
    
    train_time_end = sorted_times[train_end_idx - 1]
    val_time_end = sorted_times[val_end_idx - 1]
    
    train_mask = timestamps <= train_time_end
    val_mask = (timestamps > train_time_end) & (timestamps <= val_time_end)
    test_mask = timestamps > val_time_end
    
    return {
        'train': train_mask,
        'val': val_mask,
        'test': test_mask,
        'train_time_end': int(train_time_end),
        'val_time_end': int(val_time_end)
    }

# Load transaction features to get timestamps
print("Loading transaction data...")
tx_features = pd.read_csv('../data/Elliptic++ Dataset/txs_features.csv')
tx_classes = pd.read_csv('../data/Elliptic++ Dataset/txs_classes.csv')

# Extract timestamps (Time step column)
timestamps = tx_features['Time step'].values
n_txs = len(timestamps)

print(f"Total transactions: {n_txs:,}")
print(f"Timestamp range: {timestamps.min()} to {timestamps.max()}")

# Create temporal splits (60/20/20)
print("\nCreating temporal splits...")
splits = create_temporal_splits(timestamps, train_frac=0.6, val_frac=0.2, test_frac=0.2)

# Convert boolean masks to indices
train_indices = np.where(splits['train'])[0].tolist()
val_indices = np.where(splits['val'])[0].tolist()
test_indices = np.where(splits['test'])[0].tolist()

print(f"\nSplit sizes:")
print(f"  Train: {len(train_indices):,} ({len(train_indices)/n_txs*100:.1f}%)")
print(f"  Val:   {len(val_indices):,} ({len(val_indices)/n_txs*100:.1f}%)")
print(f"  Test:  {len(test_indices):,} ({len(test_indices)/n_txs*100:.1f}%)")

# Check fraud distribution
y = (tx_classes['class'].values == 1).astype(int)
print(f"\nFraud distribution:")
print(f"  Train: {y[splits['train']].sum():,} / {len(train_indices):,} ({y[splits['train']].mean()*100:.2f}%)")
print(f"  Val:   {y[splits['val']].sum():,} / {len(val_indices):,} ({y[splits['val']].mean()*100:.2f}%)")
print(f"  Test:  {y[splits['test']].sum():,} / {len(test_indices):,} ({y[splits['test']].mean()*100:.2f}%)")

# Save as JSON with indices
splits_json = {
    'train': train_indices,
    'val': val_indices,
    'test': test_indices,
    'metadata': {
        'n_transactions': n_txs,
        'train_time_end': int(splits['train_time_end']),
        'val_time_end': int(splits['val_time_end']),
        'fraud_rate_train': float(y[splits['train']].mean()),
        'fraud_rate_val': float(y[splits['val']].mean()),
        'fraud_rate_test': float(y[splits['test']].mean())
    }
}

# Save to data directory
output_path = '../data/Elliptic++ Dataset/splits.json'
with open(output_path, 'w') as f:
    json.dump(splits_json, f, indent=2)

print(f"\n✓ Splits saved to: {output_path}")
print(f"✓ Ready for E9 notebook!")
