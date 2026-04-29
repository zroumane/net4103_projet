from abc import ABC, abstractmethod


class LinkPrediction(ABC):
    def __init__(self, graph):
        self.graph = graph
        self.N = len(graph)

    def neighbors(self, v):
        return list(self.graph.neighbors(v))

    @abstractmethod
    def fit(self):
        raise NotImplementedError("Fit must be implemented")

    @abstractmethod
    def predict(self, u, v):
        raise NotImplementedError("predict must be implemented")
