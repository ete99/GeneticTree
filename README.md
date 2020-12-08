# GeneticTree

The main objective of the package is to allow creating decision trees that are better in some aspects than trees made by greedy algorithms.

The creation of trees is made by genetic algorithm.
In order to achive as fast as possible evolution of trees the most time consuming components are wrtitten in Cython.
Also there are implemented mechanisms for using old trees to create new ones without need to classify all observations from beggining (currently in developmnet).
There is planned to allow multithreading evolution.

The created trees should have smaller sizes with comparable accuracy to the trees made by greedy algorithms.

Project is currently in development (before first version).
The first working official version should be developed in the January 2021 (with documentation and installation by pip).
