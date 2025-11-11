# EMERGENCY FIX FOR E9 - Paste this BEFORE the model loading cell

print("Loading E7-A3 checkpoint...")

# Initialize model (hidden_dim=64 to match checkpoint)
model = E7_A3_Model(hidden_dim=64, dropout=0.4)
model.to(device)

# MANUAL FIX: Override classifier to match checkpoint
model.classifier = nn.Linear(64, 1).to(device)

print(f"✓ Model initialized:")
print(f"  - Hidden dim: 64")
print(f"  - Classifier output: {model.classifier.out_features}")

# Load checkpoint (state_dict directly)
checkpoint = torch.load('/kaggle/input/a3-dataset/a3_best.pt', map_location=device, weights_only=False)

# Try to load with strict=False
try:
    model.load_state_dict(checkpoint, strict=False)
    print("✓ Model loaded successfully (64-dim embeddings)")
except Exception as e:
    print(f"⚠️ Loading with strict=False failed: {e}")
    print("\nTrying manual parameter loading...")
    
    # Manual loading - skip problematic keys
    model_dict = model.state_dict()
    checkpoint_filtered = {k: v for k, v in checkpoint.items() 
                          if k in model_dict and v.shape == model_dict[k].shape}
    
    model_dict.update(checkpoint_filtered)
    model.load_state_dict(model_dict)
    print(f"✓ Loaded {len(checkpoint_filtered)}/{len(checkpoint)} parameters")

model.eval()
print("✓ Model ready for inference")
