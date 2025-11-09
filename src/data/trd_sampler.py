# Placeholder: real implementation will enforce time(nei) <= time(target)
class TRDSampler:
    def __init__(self, fanouts=(10,10), directed=True):
        self.fanouts = fanouts
        self.directed = directed
    def sample(self, graph, targets, timestamps):
        raise NotImplementedError("Implement leakage-safe temporal neighbor sampling.")
