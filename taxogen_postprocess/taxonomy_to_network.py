#!/usr/bin/env

import os
import networkx as nx
import pickle

from argparse import ArgumentParser


def convert(graph, folder):
    clusters = {}
    hierarchy = []

    try:
        with open(folder + "/hierarchy.txt", "r") as fin:
            for line in fin:
                edge = line.strip().replace("\n","").split()
                graph.add_node(edge[0])
                graph.add_node(edge[1])
                graph.add_edge(edge[1], edge[0])
                hierarchy.append(edge[0])

                clusters.update(convert(graph, folder + "/" + edge[0]))

        with open(folder + "/cluster_keywords.txt", "r") as fin:
            for line in fin:
                item = line.strip().replace("\n","").split()
                if item[1] not in clusters:
                    clusters[item[1]] = hierarchy[int(item[0])]
    except FileNotFoundError:
        pass

    return clusters


def main():
    parser = ArgumentParser(
        description="convert a taxogen taxonomy into a networkx graph")
    parser.add_argument("--folder", dest="folder", type=str,
                        help="root folder of the taxogen taxonomy")
    args = parser.parse_args()

    graph = nx.DiGraph()
    clusters = convert(graph, args.folder)

    pickle.dump(graph, open("hierarchy_nx.pickle", "wb"))
    pickle.dump(clusters, open("clusters.pickle", "wb"))
    

if __name__ == "__main__":
    main()
