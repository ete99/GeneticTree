import os
os.chdir("../")

from tests.set_up_variables_and_imports import *
from genetic_tree import GeneticTree
from tree.thresholds import prepare_thresholds_array
from tree.tree import copy_tree, _test_independence_of_copied_tree
from tree.mutator import mutate_random_node, mutate_random_class_or_threshold
from tree.mutator import mutate_random_feature, mutate_random_threshold
from tree.mutator import mutate_random_class

import pickle

n_thresholds: int = 2
X = GeneticTree._check_X_(GeneticTree(), X, True)

# thresholds array have unique values
# it is needed to proper test mutating thresholds
thresholds = prepare_thresholds_array(n_thresholds, X)


def test_builder_tree_size():
    builder: FullTreeBuilder = FullTreeBuilder()
    for initial_depth in range(5, 0, -1):
        tree: Tree = Tree(np.unique(y).shape[0], X, y, thresholds)
        tree.resize_by_initial_depth(initial_depth)
        builder.build(tree, initial_depth)
        assert tree.node_count == tree.feature.shape[0] == tree.threshold.shape[0] == 2 ** (initial_depth+1) - 1


def build(depth: int = 1, n_trees: int = 10):
    builder: FullTreeBuilder = FullTreeBuilder()
    trees = []
    for i in range(n_trees):
        tree: Tree = Tree(np.unique(y).shape[0], X, y, thresholds)
        tree.resize_by_initial_depth(depth)
        builder.build(tree, depth)
        tree.initialize_observations()
        trees.append((tree, np.array(tree.feature), np.array(tree.threshold)))
    return trees


@pytest.mark.parametrize("function,features_assertion,threshold_assertion",
                         [(mutate_random_node,     10,  0),
                          (mutate_random_feature,  10, 10),
                          (mutate_random_threshold, 0, 10),
                          (mutate_random_class,    10,  0)])
def test_mutator(function: callable, features_assertion: int, threshold_assertion: int):
    trees = build(3, 10)
    not_same_features: int = 0
    not_same_thresholds: int = 0
    for tree, feature, threshold in trees:
        function(tree)
        not_same_features += assert_array_not_the_same_in_at_most_one_index(feature, tree.feature)
        not_same_thresholds += assert_array_not_the_same_in_at_most_one_index(threshold, tree.threshold)
    assert not_same_features >= features_assertion
    assert not_same_thresholds >= threshold_assertion


def assert_array_not_the_same_in_at_most_one_index(array, other) -> int:
    counter: int = 0
    for before, after in zip(array, other):
        if before != after:
            counter += 1
    assert counter <= 1
    return counter


def test_crossing_one_leaf():
    trees = build(2, 10)
    trees[0][0].initialize_observations()
    trees[1][0].initialize_observations()
    cross_trees(trees[0][0], trees[1][0], 0, 6)


def test_crossing_only_from_second_parent():
    trees = build(2, 10)
    trees[0][0].initialize_observations()
    trees[1][0].initialize_observations()
    cross_trees(trees[0][0], trees[1][0], 0, 0)


@pytest.mark.parametrize("first, second",
                         [(6, 1), (6, 0), (0, 0), (0, 1), (1, 6), (1, 3),
                          (1, 0), (6, 3), (3, 0), (3, 1), (3, 2), (3, 3), (3, 6)])
def test_crossing(first, second):
    trees = build(2, 10)
    trees[0][0].initialize_observations()
    trees[1][0].initialize_observations()
    cross_trees(trees[0][0], trees[1][0], first, second)


def test_crosser():
    trees = build(2, 10)
    tree: Tree = cross_trees(trees[0][0], trees[1][0], 2, 0)
    new_features = np.append(np.append(np.append(trees[0][1][0:2], np.array([trees[1][1][6], trees[0][1][3], trees[0][1][4]])),
                                       np.array([trees[1][1][2], trees[1][1][0], trees[1][1][5]])),
                             np.array([trees[1][1][1], trees[1][1][4], trees[1][1][3]]))
    new_depth = np.array([0, 1, 3, 2, 2, 2, 1, 3, 2, 3, 3])
    assert_array_equal(new_features, tree.feature)
    assert_array_equal(new_depth, tree.nodes_depth)


def test_independence_of_created_trees_by_crosser(crosses: int = 10, mutations: int = 10):
    trees = build(1, 10)

    # cross tree many times with the same tree
    tree: Tree = cross_trees(trees[0][0], trees[1][0], 1, 0)
    for i in range(1, crosses):
        tree = cross_trees(trees[0][0], tree, 1, 0)

    # check if crossing is proper
    new_features = np.repeat(np.array([[trees[0][1][0], trees[0][1][2]]]).transpose(), crosses, axis=1).reshape(crosses*2, order='F')
    new_features[1] = trees[0][1][0]
    new_features[2] = trees[0][1][2]
    new_features = np.append(new_features, np.array([trees[1][1][0], trees[1][1][2], trees[1][1][1]]))
    assert_array_equal(new_features, tree.feature)

    # each mutation should mutate maximum one place in genom
    # if there are no two pointers for exactly the same node it should not mutate more than one place in genom
    old_features = np.array(tree.feature)
    for i in range(mutations):
        mutate_random_node(tree)
        new_features = np.array(tree.feature)
        assert_array_not_the_same_in_at_most_one_index(new_features, old_features)
        old_features = new_features


def test_tree_pickling():
    tree: Tree = build(10, 1)[0][0]
    depth = tree.depth
    feature = tree.feature
    node_count = tree.node_count
    bytes_io = io.BytesIO()
    pickle.dump(tree, bytes_io)
    bytes_io.seek(0)
    tree = pickle.load(bytes_io)
    assert_array_equal(feature, tree.feature)
    assert depth == tree.depth
    assert node_count == tree.node_count


def test_tree_copying():
    tree: Tree = build(10, 1)[0][0]
    tree_copied: Tree = copy_tree(tree)
    assert tree.node_count == tree_copied.node_count
    assert_array_equal(tree.X, tree_copied.X)
    assert_array_equal(tree.y, tree_copied.y)
    assert_array_equal(tree.thresholds, tree_copied.thresholds)
    assert id(tree.node_count) != id(tree_copied.node_count)
    assert id(tree.X) == id(tree_copied.X)
    # following lines don't have to be true
    # because two memoryviews of the same object can have different ids
    # assert id(tree.y) == id(tree_copied.y)
    # assert id(tree.thresholds) == id(tree_copied.thresholds)


def test_independence_of_copied_tree():
    tree: Tree = build(10, 1)[0][0]
    _test_independence_of_copied_tree(tree)

