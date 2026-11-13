# Probabilistic Structures (Data Sketches) trade a tiny, controlled margin of error for massive reductions in memory and constant-time processing over data streams.
class ProbabilisticStructure:
    def __init__(self, error_rate=0.01):
        self.error_rate = error_rate