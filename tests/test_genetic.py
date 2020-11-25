import os
os.chdir("../")

from genetic_tree import GeneticTree
from tests.set_up_variables_and_imports import *
from tree.thresholds import prepare_thresholds_array

X = GeneticTree._check_X_(GeneticTree(), X, True)
thresholds = prepare_thresholds_array(10, X)


def initialize_tree(thresholds) -> Tree:
    tree: Tree = Tree(3, X, y, thresholds)
    tree.resize_by_initial_depth(3)
    builder: FullTreeBuilder = FullTreeBuilder()
    builder.build(tree, 3)
    tree.initialize_observations()
    return tree


def initialization():
    tree: Tree = initialize_tree(thresholds)
    print(f'Features of tree: {tree.feature}\n')


def mutate_feature():
    gt = GeneticTree(initial_depth=1, max_iterations=1,
                     remove_other_trees=False, remove_variables=False)
    gt.fit(X, y)
    trees_before = gt._trees_
    gt.crosser.cross_population(trees_before)
    print(f'Features of tree before mutation: {trees_before[0].feature}')
    return trees_before


if __name__ == "__main__":
    trees = mutate_feature()
    for tree in trees[1000:1040]:
        print(tree.feature)
