import pickle
import networkx as nx
import argparse
import random

def get_accuracy(standard, graph, clusters):
    total = 0
    common_edges = 0
    common_cluster_edges = 0
    parent_child_edges = 0
    lengths = {}
    parent_child_lengths = {}
    misoriented_by_inclusion = 0
    strictly_misoriented_by_inclusion = 0

    unoriented_graph = nx.Graph(graph)

    for source, target in standard.edges:
        if source == target:
            continue
        formatted_source = "_".join(source.split())
        formatted_target = "_".join(target.split())
        if not formatted_source in clusters or not formatted_target in clusters:
            continue

        total += 1
        taxogen_source = clusters[formatted_source]
        taxogen_target = clusters[formatted_target]

        try:
            if taxogen_source in graph[taxogen_target] or taxogen_target in graph[taxogen_source]:
                common_edges += 1
        except:
            pass

        if taxogen_source == taxogen_target:
            common_cluster_edges += 1

        l = nx.shortest_path_length(unoriented_graph, source=taxogen_source, target=taxogen_target)
        if l not in lengths:
            lengths[l] = 0
        lengths[l] += 1
        try:
            dl = nx.shortest_path_length(
                graph, source=taxogen_source, target=taxogen_target)
            parent_child_edges += 1
            if dl not in parent_child_lengths:
                parent_child_lengths[dl] = 0
            parent_child_lengths[dl] += 1
        except:
            p = nx.shortest_path(unoriented_graph, source=taxogen_source, target=taxogen_target)
            mis = False
            strictly_mis = True
            for i in range(len(p) - 1):
                if p[i+1] not in graph[p[i]]:
                    if set(p[i+1].split()).issubset(p[i].split()):
                        mis = True
                    else:
                        strictly_mis = False
            if mis:
                misoriented_by_inclusion += 1
                if strictly_mis:
                    strictly_misoriented_by_inclusion += 1

    max_length = 0
    for l in lengths:
        max_length = l if l > max_length else max_length

    # TODO add coder la parenté et détecter si un noeud est bien enfant (indirect d'un autre)

    directed_weight_sum = float(sum([l * parent_child_lengths[l] for l in parent_child_lengths
        if l > 0]))
    directed_sum = float(sum([parent_child_lengths[l] for l in parent_child_lengths 
        if l > 0]))

    return (common_edges,
            common_cluster_edges,
            total,
            parent_child_edges,
            misoriented_by_inclusion,
            strictly_misoriented_by_inclusion,
            parent_child_lengths[0] if 0 in parent_child_lengths else 0, 
            directed_weight_sum /
                directed_sum if directed_sum > 0 else -1,
            directed_weight_sum / float(parent_child_edges) if float(parent_child_edges) > 0 else 0,
            float(sum([l * lengths[l] for l in lengths if l > 0])) /
                float(sum([lengths[l] for l in lengths if l > 0])),
            *[lengths[i] if i in lengths else 0 for i in range(1, max_length)])

def main():
    parser = argparse.ArgumentParser(
        description='Compute the author similarities')
    parser.add_argument("--standard_graph", dest="standard_graph", type=str,
                        help="pickle file of the standard graph (networkx.DiGraph)")
    parser.add_argument("--graph", dest="graph", type=str,
                        help="pickle file of the taxogen graph")
    parser.add_argument("--clusters", dest="clusters", type=str,
                        help="pickle file of the taxogen clusters")
    parser.add_argument("--random", dest="random", action="store_true")
    parser.add_argument("--out", dest="out", type=str,
                        help="output file prefix")

    args = parser.parse_args()

    graph = pickle.load(open(args.graph, "rb"))
    clusters = pickle.load(open(args.clusters, "rb"))
    standard_graph = pickle.load(open(args.standard_graph, "rb"))

    if args.random:
        nodes = list(clusters.keys())
        new_graph = nx.DiGraph()
        new_graph.add_node("*")
        hierarchy = random.choices(nodes, k=155)
        for i in range(len(hierarchy)):
            new_graph.add_node(hierarchy[i])
            if i < 5:
                new_graph.add_edge("*", hierarchy[i])
            elif i < 30:
                new_graph.add_edge(hierarchy[i % 5], hierarchy[i])
            else:
                new_graph.add_edge(hierarchy[i % 25 + 5], hierarchy[i])
        new_clusters = {}
        for node in nodes:
            new_clusters[node] = random.choice(hierarchy)
        
        r = get_accuracy(standard_graph, new_graph, new_clusters)

    else:
        r = get_accuracy(standard_graph, graph, clusters)

    with open(args.out + ".csv", "w") as fout:
        fout.write("common edges,common cluster edges,total edges," +
        "directed edges,misoriented by inclusion,strictly misoriented by inclusion," +
        "cluster directed edges,average distance directed edges,average distance," +
        "average distance without cluster" +
                   ",".join([str(i) for i in range(1, len(r) - 10)]) + "\n")

        fout.write(",".join([str(x) for x in r]) + "\n")


if __name__ == "__main__":
    main()
