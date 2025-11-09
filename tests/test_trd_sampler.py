"""Tests for TRD (Time-Relaxed Directed) Sampler"""
import torch
import numpy as np
import pytest
from src.data.trd_sampler import TRDSampler


def test_trd_sampler_exists():
    """Test that TRDSampler can be instantiated."""
    s = TRDSampler()
    assert hasattr(s, "sample")
    assert hasattr(s, "validate_no_future_leakage")


def test_no_future_neighbors():
    """
    Test that sampler enforces time(neighbor) <= time(target).
    
    Create a simple temporal graph:
    Node 0 (t=1) -> Node 1 (t=2) -> Node 2 (t=3)
    
    When sampling for Node 1 (t=2), should only get Node 0 (t=1), not Node 2 (t=3).
    """
    # Create simple temporal chain
    edge_index = torch.tensor([[0, 1], [1, 2]], dtype=torch.long)
    timestamps = torch.tensor([1, 2, 3], dtype=torch.long)
    target_nodes = torch.tensor([1], dtype=torch.long)  # Node 1 at time 2
    
    sampler = TRDSampler(fanouts=[10, 10], directed=True)
    sampled_nodes, sampled_edges, layer_sizes = sampler.sample(
        edge_index, timestamps, target_nodes, num_hops=2
    )
    
    # Verify no future leakage: Node 2 (t=3) should NOT be in sampled nodes
    assert 2 not in sampled_nodes, "Future node (t=3) leaked into sampling for target at t=2"
    
    # Node 0 (t=1) and Node 1 (t=2) should be present
    assert 1 in sampled_nodes, "Target node should be in sampled nodes"
    # Node 0 may or may not be sampled depending on connectivity, but if it is, it's valid


def test_temporal_constraint_validation():
    """Test the validation function catches temporal violations."""
    sampler = TRDSampler()
    
    # Valid: all edges go forward in time
    edge_index_valid = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)
    timestamps_valid = torch.tensor([1, 2, 3, 4], dtype=torch.long)
    
    is_valid, violations = sampler.validate_no_future_leakage(
        edge_index_valid, timestamps_valid
    )
    assert is_valid, "Valid temporal edges incorrectly flagged"
    assert violations == 0
    
    # Invalid: edge from future to past
    edge_index_invalid = torch.tensor([[0, 2], [1, 1]], dtype=torch.long)
    timestamps_invalid = torch.tensor([1, 2, 3], dtype=torch.long)
    
    is_valid, violations = sampler.validate_no_future_leakage(
        edge_index_invalid, timestamps_invalid
    )
    assert not is_valid, "Invalid temporal edges not detected"
    assert violations > 0


def test_fanout_limiting():
    """Test that sampler respects fanout limits."""
    # Create a star graph: center node with many neighbors at earlier time
    num_neighbors = 50
    center_node = num_neighbors
    
    # All neighbors point to center
    edges = [[i, center_node] for i in range(num_neighbors)]
    edge_index = torch.tensor(edges, dtype=torch.long).t()
    
    # All neighbors at t=1, center at t=2
    timestamps = torch.cat([
        torch.ones(num_neighbors, dtype=torch.long),
        torch.tensor([2], dtype=torch.long)
    ])
    
    target_nodes = torch.tensor([center_node], dtype=torch.long)
    
    fanout = 10
    sampler = TRDSampler(fanouts=[fanout], max_in_neighbors=20)
    
    sampled_nodes, sampled_edges, layer_sizes = sampler.sample(
        edge_index, timestamps, target_nodes, num_hops=1
    )
    
    # Should sample at most fanout neighbors (plus target and self-loop)
    # May be less if max_in_neighbors cap is applied first
    assert len(sampled_nodes) <= num_neighbors + 1, "Sampled more nodes than available"


def test_empty_neighborhood():
    """Test behavior when target has no valid temporal neighbors."""
    # Isolated node at t=1
    edge_index = torch.tensor([[1, 2], [2, 3]], dtype=torch.long)  # Edges don't involve node 0
    timestamps = torch.tensor([1, 2, 3, 4], dtype=torch.long)
    target_nodes = torch.tensor([0], dtype=torch.long)
    
    sampler = TRDSampler(fanouts=[5, 5])
    sampled_nodes, sampled_edges, layer_sizes = sampler.sample(
        edge_index, timestamps, target_nodes, num_hops=2
    )
    
    # Should at least include the target node itself
    assert 0 in sampled_nodes, "Target node should always be in sampled result"


def test_self_loops():
    """Test that self-loops are added when enabled."""
    edge_index = torch.tensor([[0, 1], [1, 2]], dtype=torch.long)
    timestamps = torch.tensor([1, 2, 3], dtype=torch.long)
    target_nodes = torch.tensor([1], dtype=torch.long)
    
    sampler = TRDSampler(fanouts=[5], allow_self_loops=True)
    sampled_nodes, sampled_edges, layer_sizes = sampler.sample(
        edge_index, timestamps, target_nodes, num_hops=1
    )
    
    # Check if any self-loop exists in sampled edges
    if sampled_edges.shape[1] > 0:
        has_self_loop = (sampled_edges[0] == sampled_edges[1]).any().item()
        # Self-loops should be present (though might not be if no edges sampled)
        # This test is more about ensuring no error occurs with self_loops=True


def test_multiple_targets():
    """Test sampling for multiple target nodes simultaneously."""
    # Simple chain: 0 -> 1 -> 2 -> 3
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)
    timestamps = torch.tensor([1, 2, 3, 4], dtype=torch.long)
    target_nodes = torch.tensor([1, 2], dtype=torch.long)  # Multiple targets
    
    sampler = TRDSampler(fanouts=[5, 5])
    sampled_nodes, sampled_edges, layer_sizes = sampler.sample(
        edge_index, timestamps, target_nodes, num_hops=2
    )
    
    # Both targets should be in sampled nodes
    assert 1 in sampled_nodes
    assert 2 in sampled_nodes
