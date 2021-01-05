from aenum import Enum, extend_enum
from tree.builder import Builder, FullTreeBuilder, SplitTreeBuilder
from tree.tree import Tree
import numpy as np
import warnings


def initialize_full(X, y, sample_weight, thresholds, initializer):
    """
    Function to initialize forest

    Args:
        initializer:
        thresholds:
        sample_weight:
        y:
        X:
    """
    trees = []
    tree: Tree
    n_classes: int = np.unique(y).shape[0]

    for tree_index in range(initializer.n_trees):
        tree: Tree = Tree(n_classes, X, y, sample_weight, thresholds, np.random.randint(10 ** 8))
        tree.resize_by_initial_depth(initializer.initial_depth)
        initializer.builder.build(tree, initializer.initial_depth)
        tree.initialize_observations()
        trees.append(tree)
    return trees


def initialize_half(X, y, sample_weight, thresholds, initializer):
    """
    Function to initialize forest

    Args:
        initializer:
        thresholds:
        sample_weight:
        y:
        X:
    """
    trees = []
    tree: Tree
    n_classes: int = np.unique(y).shape[0]

    for tree_index in range(initializer.n_trees):
        if tree_index % 2 == 0:
            tree: Tree = Tree(n_classes, X, y, sample_weight, thresholds, np.random.randint(10 ** 8))
            tree.resize_by_initial_depth(initializer.initial_depth)
            initializer.builder.build(tree, initializer.initial_depth)
            tree.initialize_observations()
            trees.append(tree)
        else:
            if initializer.initial_depth > 1:
                depth = np.random.randint(low=1, high=initializer.initial_depth)
            else:
                depth = initializer.initial_depth
            tree: Tree = Tree(n_classes, X, y, sample_weight, thresholds, np.random.randint(10 ** 8))
            tree.resize_by_initial_depth(depth)
            initializer.builder.build(tree, depth)
            tree.initialize_observations()
            trees.append(tree)
    return trees


def initialize_split(X, y, sample_weight, thresholds, initializer):
    """
    Function to initialize forest

    Args:
        initializer:
        thresholds:
        sample_weight:
        y:
        X:
    """
    trees = []
    tree: Tree
    n_classes: int = np.unique(y).shape[0]

    for tree_index in range(initializer.n_trees):
        tree: Tree = Tree(n_classes, X, y, sample_weight, thresholds, np.random.randint(10 ** 8))
        tree.resize_by_initial_depth(initializer.initial_depth)
        initializer.builder.build(tree, initializer.initial_depth, initializer.split_prob)
        tree.initialize_observations()
        trees.append(tree)
    return trees


class Initialization(Enum):
    """
    Initialization is enumerator with possible initialization methods to use:
        Full --
        Half --
        Split --

    To add new Initialization method see genetic.initialization.Initialization
    """

    def __new__(cls, function, *args):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)
        obj.initialize = function
        return obj

    @staticmethod
    def add_new(name, function):
        extend_enum(Initialization, name, function)

    # after each entry should be at least delimiter
    # (also can be more arguments which will be ignored)
    # this is needed because value is callable type
    Full = initialize_full,
    Half = initialize_half,
    Split = initialize_split,


class Initializer:
    """
    Initializer is responsible for initializing population

    Mainly it creates trees with random features and thresholds inside decision
    nodes and with random classes inside leaves. The depth is set or chosen
    randomly.

    Args:
        n_trees: number of trees to create
        initial_depth: depth of all trees (if initialization type use it)
        initialization: how to initialize trees
    """

    def __init__(self,
                 n_trees: int = 400, initial_depth: int = 1,
                 initialization: Initialization = Initialization.Split,
                 split_prob: float = 0.7,
                 **kwargs):
        self.n_trees: int = self._check_n_trees(n_trees)
        self.initial_depth: int = self._check_initial_depth(initial_depth)
        self.initialization: Initialization = self._check_initialization(initialization)
        self.split_prob: float = self._check_split_prob(split_prob)
        self.builder: Builder = self.initialize_builder()

    @staticmethod
    def _check_initialization(initialization):
        # comparison of strings because after using Selection.add_new() Selection is reference to other class
        if str(type(initialization)) == str(Initialization):
            return initialization
        else:
            raise TypeError(f"Passed selection={initialization} with type {type(initialization)}, "
                            f"Needed argument with type Selection")

    @staticmethod
    def _check_n_trees(n_trees):
        if n_trees <= 0:
            warnings.warn(f"Try to set n_trees={n_trees}. Changed to n_trees=1, "
                          f"but try to set n_trees manually for value at least 20")
            n_trees = 1
        return n_trees

    @staticmethod
    def _check_initial_depth(initial_depth):
        if initial_depth <= 0:
            warnings.warn(f"Try to set initial_depth={initial_depth}. Changed to initial_depth=1.")
            initial_depth = 1
        return initial_depth

    @staticmethod
    def _check_split_prob(split_prob):
        if split_prob < 0 or split_prob > 1:
            warnings.warn(f"Try to set split_prob={split_prob}. Changed to initial_depth=0.7. "
                          f"Split prob should have value between 0 and 1")
            split_prob = 1
        return split_prob

    def initialize_builder(self):
        """
        Returns:
            Builder: cython builder to initialize new trees
        """
        if self.initialization == Initialization.Full \
                or self.initialization == Initialization.Half:
            return FullTreeBuilder()
        elif self.initialization == Initialization.Split:
            return SplitTreeBuilder()

    def set_params(self, initial_depth: int = None,
                   initialization: Initialization = None,
                   **kwargs):
        """
        Function to set new parameters for Initializer

        Arguments are the same as in __init__
        """
        if initial_depth is not None:
            self.initial_depth = initial_depth
        if initialization is not None:
            self.initialization = initialization

    def initialize(self, X, y, sample_weight, threshold):
        """
        Function to initialize forest

        Args:
            X:
            y:
            sample_weight:
            threshold:
        """
        return self.initialization.initialize(X, y, sample_weight, threshold, self)

