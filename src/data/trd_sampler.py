"""
Time-Relaxed Directed (TRD) Sampler for Temporal GNNs

Enforces strict temporal constraint: for target node at time t*, 
only neighbors with timestamp <= t* are sampled (no future leakage).
"""
import torch
import numpy as np
from typing import List, Tuple, Optional
from torch_geometric.data import Data


class TRDSampler:
    """
    Time-Relaxed Directed (TRD) neighbor sampler.
    
    Enforces temporal constraint: for each target node at time t*,
    only includes neighbors v where time(v) <= t*.
    
    Args:
        fanouts: List of fanout sizes per layer, e.g., [15, 10] for 2-layer GNN
        directed: Whether to respect edge direction (default: True)
        max_in_neighbors: Max incoming neighbors per node
        max_out_neighbors: Max outgoing neighbors per node
        allow_self_loops: Include self-connections in sampling
    """
    
    def __init__(
        self,
        fanouts: List[int] = (10, 10),
        directed: bool = True,
        max_in_neighbors: int = 15,
        max_out_neighbors: int = 15,
        allow_self_loops: bool = True
    ):
        self.fanouts = list(fanouts)
        self.directed = directed
        self.max_in_neighbors = max_in_neighbors
        self.max_out_neighbors = max_out_neighbors
        self.allow_self_loops = allow_self_loops
        self.num_layers = len(self.fanouts)
        
    def sample(
        self, 
        edge_index: torch.Tensor,
        timestamps: torch.Tensor,
        target_nodes: torch.Tensor,
        num_hops: int = 2
    ) -> Tuple[torch.Tensor, torch.Tensor, List[int]]:
        """
        Sample temporal neighborhood for target nodes.
        
        Args:
            edge_index: [2, E] edge tensor (source, target)
            timestamps: [N] node timestamps
            target_nodes: [T] target node indices
            num_hops: Number of hops to sample (should match len(fanouts))
            
        Returns:
            sampled_nodes: Nodes in sampled subgraph
            sampled_edges: Edge index of sampled subgraph
            layer_sizes: Number of nodes added at each layer
        """
        if num_hops != self.num_layers:
            num_hops = self.num_layers
            
        device = edge_index.device
        
        # Initialize with target nodes
        current_nodes = target_nodes.unique()
        all_sampled_nodes = [current_nodes]
        all_sampled_edges = []
        layer_sizes = [len(current_nodes)]
        
        # Build adjacency list for efficient neighbor lookup
        num_nodes = timestamps.shape[0]
        adj_out = [[] for _ in range(num_nodes)]  # outgoing edges
        adj_in = [[] for _ in range(num_nodes)]   # incoming edges
        
        for i in range(edge_index.shape[1]):
            src, dst = edge_index[0, i].item(), edge_index[1, i].item()
            adj_out[src].append(dst)
            adj_in[dst].append(src)
        
        # Sample layer by layer (backward from targets)
        for layer_idx in range(num_hops):
            fanout = self.fanouts[layer_idx]
            next_layer_nodes = []
            layer_edges = []
            
            for node_idx in current_nodes.cpu().numpy():
                node_time = timestamps[node_idx].item()
                
                # Get temporal neighbors (time <= node_time)
                in_neighbors = [
                    n for n in adj_in[node_idx] 
                    if timestamps[n].item() <= node_time
                ]
                out_neighbors = [
                    n for n in adj_out[node_idx]
                    if timestamps[n].item() <= node_time
                ] if self.directed else []
                
                # Cap neighbors
                if len(in_neighbors) > self.max_in_neighbors:
                    in_neighbors = np.random.choice(
                        in_neighbors, 
                        self.max_in_neighbors, 
                        replace=False
                    ).tolist()
                    
                if self.directed and len(out_neighbors) > self.max_out_neighbors:
                    out_neighbors = np.random.choice(
                        out_neighbors,
                        self.max_out_neighbors,
                        replace=False
                    ).tolist()
                
                # Combine neighbors
                all_neighbors = in_neighbors + out_neighbors
                
                # Sample up to fanout
                if len(all_neighbors) > fanout:
                    sampled = np.random.choice(
                        all_neighbors,
                        min(fanout, len(all_neighbors)),
                        replace=False
                    ).tolist()
                else:
                    sampled = all_neighbors
                
                # Add sampled neighbors
                for neighbor in sampled:
                    next_layer_nodes.append(neighbor)
                    # Add edge (neighbor -> node for message passing)
                    layer_edges.append([neighbor, node_idx])
            
            # Add self-loops if enabled
            if self.allow_self_loops:
                for node_idx in current_nodes.cpu().numpy():
                    layer_edges.append([node_idx, node_idx])
            
            # Update for next layer
            if next_layer_nodes:
                current_nodes = torch.tensor(
                    list(set(next_layer_nodes)),
                    dtype=torch.long,
                    device=device
                )
                all_sampled_nodes.append(current_nodes)
                layer_sizes.append(len(current_nodes))
            else:
                layer_sizes.append(0)
            
            if layer_edges:
                all_sampled_edges.extend(layer_edges)
        
        # Combine all sampled nodes
        all_nodes = torch.cat(all_sampled_nodes).unique()
        
        # Create node mapping
        node_mapping = {n.item(): i for i, n in enumerate(all_nodes)}
        
        # Remap edges
        if all_sampled_edges:
            remapped_edges = [
                [node_mapping[src], node_mapping[dst]]
                for src, dst in all_sampled_edges
                if src in node_mapping and dst in node_mapping
            ]
            sampled_edge_index = torch.tensor(
                remapped_edges,
                dtype=torch.long,
                device=device
            ).t().contiguous() if remapped_edges else torch.zeros((2, 0), dtype=torch.long, device=device)
        else:
            sampled_edge_index = torch.zeros((2, 0), dtype=torch.long, device=device)
        
        return all_nodes, sampled_edge_index, layer_sizes
    
    def validate_no_future_leakage(
        self,
        edge_index: torch.Tensor,
        timestamps: torch.Tensor
    ) -> Tuple[bool, int]:
        """
        Verify no edges point from past to future.
        
        Args:
            edge_index: [2, E] edge indices
            timestamps: [N] node timestamps
            
        Returns:
            (is_valid, num_violations) tuple
        """
        src_times = timestamps[edge_index[0]]
        dst_times = timestamps[edge_index[1]]
        
        # For temporal validity, destination time should be >= source time
        # (or equal for same-time transactions)
        violations = (dst_times < src_times).sum().item()
        
        return violations == 0, violations
