from tree.evaluation import get_accuracies, get_trees_depths, get_trees_sizes
import numpy as np

from aenum import Enum, extend_enum


def get_accuracy(trees: np.array, **kwargs) -> np.array:
    return np.array(get_accuracies(trees))


def get_accuracy_and_size(trees: np.array, size_factor: float = 0.0001, **kwargs) -> np.array:
    accuracy = np.array(get_accuracies(trees))
    size = np.array(get_trees_sizes(trees))
    return accuracy - size_factor * size


def get_accuracy_and_depth(trees: np.array, depth_factor: float = 0.01, **kwargs) -> np.array:
    accuracy = np.array(get_accuracies(trees))
    depth = np.array(get_trees_depths(trees))
    return accuracy - depth_factor * depth


class Metric(Enum):
    """
    Metric is enumerator with possible metrics to use during evaluation:
        Accuracy -- number of proper classified observations divided by \
        number of all observations
        AccuracyMinusSize -- accuracy + constant times number of nodes of tree
        AccuracyMinusDepth -- accuracy + constant times maximal depth of tree

    To add new Metric see genetic.selector.SelectionType
    """
    def __new__(cls, function, *args):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)
        obj.evaluate = function
        return obj

    @staticmethod
    def add_new(name, function):
        extend_enum(Metric, name, function)

    # after each entry should be at least delimiter
    # (also can be more arguments which will be ignored)
    # this is needed because value is callable type
    Accuracy = get_accuracy,
    AccuracyMinusSize = get_accuracy_and_size,
    AccuracyMinusDepth = get_accuracy_and_depth,


class Evaluator:
    """
    Evaluator is responsible for evaluating each individuals' score
    It evaluates each individual and give them a score

    There are plenty of possible metrics:
    - accuracy
    - accuracy minus size (means number of nodes)
    - accuracy minus depth (means maximal depth of tree)

    Args:
        metric: a metric used to evaluate single tree
    """

    def __init__(self,
                 metric: Metric = Metric.AccuracyMinusDepth,
                 **kwargs):
        self.metric: Metric = self._check_metric_(metric)

    def set_params(self,
                   metric: Metric = None,
                   **kwargs):
        """
        Function to set new parameters for Selector

        Arguments are the same as in __init__
        """
        if metric is not None:
            self.metric = self._check_metric_(metric)

    @staticmethod
    def _check_metric_(metric):
        if isinstance(metric, Metric):
            return metric
        else:
            raise TypeError(f"Passed metric={metric} with type {type(metric)}, "
                            f"Needed argument with type Metric")

    def get_best_tree_index(self, trees) -> int:
        """
        Args:
            trees: List with all trees

        Returns:
            Index of best tree from trees array
        """
        trees_metric = self.evaluate(trees)
        best_index = np.argmax(trees_metric)
        return best_index

    def evaluate(self, trees) -> np.array:
        """
        Function evaluates each tree's metric from trees array

        Args:
            trees: List with all trees to evaluate
        """
        return self.metric.evaluate(trees)
