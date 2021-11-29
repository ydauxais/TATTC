# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

import os
import json
import pickle
import networkx as nx
from scipy.sparse.csgraph import minimum_spanning_tree

root_dir = "yours"
topics = pickle.load(open(root_dir + "top9-6237k_dkpe_features.pickle", "rb"))
itopics = pickle.load(
    open(root_dir + "top9-6237k_dkpe_ifeatures.pickle", "rb"))
overlaps = pickle.load(
    open(root_dir + "top9-6237k_dkpe_overlaps.pickle", "rb"))
weights = pickle.load(open(root_dir + "top9-6237k_dkpe_weights.pickle", "rb"))

topic_similarities = pickle.load(open("your _topic_similarities.pickle", "rb"))
author_similarities = pickle.load(
    open(root_dir + "your _author_similarities.pickle", "rb"))
author_subsumption = pickle.load(open("your _author_subsumptions.pickle", "rb"))
field_similarities = pickle.load(open("your _field_similarities.pickle", "rb"))
field_subsumption = pickle.load(open("your _field_subsumptions.pickle", "rb"))

def oriented_graph_from_root(graph, root):
    directed_graph = nx.DiGraph()
    node_stack = [root]
    while len(node_stack) > 0:
        node = node_stack.pop()
        directed_graph.add_node(node)
        for _, child in graph.edges(node):
            if child not in directed_graph:
                directed_graph.add_node(child)
                directed_graph.add_edge(node, child, group=1)
                node_stack.append(child)
    return directed_graph


def get_root(words):
    row_sum = overlaps[words, :][:, words].sum(axis=1)
    return topics[row_sum.argmax()]


def get_words(index, overlap_threshold, similarity_threshold):
    interesting_children = set(
        (overlaps[:, index] >= overlap_threshold).nonzero()[0])
    interesting_parents = set(
        (overlaps[index, :] >= overlap_threshold).nonzero()[1])

    interesting_words = interesting_children.union(interesting_parents)
    list_interesting_words = sorted(list(interesting_words))

    author_words = (author_similarities[index, :] >
                    similarity_threshold).nonzero()[1]

    return sorted(list(set(list_interesting_words).union(set(author_words))))


def graph_to_nodes_and_links(graph):
    gnodes = [node for node in graph.nodes]
    reverse_gnodes = {gnodes[i]: i for i in range(len(gnodes))}

    nodes = [{'id': reverse_gnodes[node], 'label': str(
        node), 'group': "1"} for node in gnodes]
    links = [{'source': reverse_gnodes[source],
              'target': reverse_gnodes[target],
              'group': graph.edges[source, target]['group']
              } for source, target in graph.edges]
    return nodes, links


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Ready!")


@app.get('/api/taxonomy')
async def taxonomy(context: str = "",
                   overlap_threshold: float = .05,
                   similarity_threshold: float = 0.01,
                    topic_subsumption_weight = -4.8,
                    topic_similarity_weight = 18.12,
                    author_subsumption_weight = -14.40,
                    author_similarity_weight = 13.11,
                    field_subsumption_weight = 0.43,
                    field_similarity_weight = 0.25):
    context = context.replace('"', "").replace("'", "")
    if context not in itopics:
        print(context)
        return {"error": "Context not known"}

    index = itopics[context]
    lwords = get_words(index, overlap_threshold, similarity_threshold)

    final_matrix = weights * topic_subsumption_weight
    final_matrix -= topic_similarities * topic_similarity_weight
    final_matrix += author_subsumption * author_subsumption_weight
    final_matrix -= author_similarities.similarities * author_similarity_weight
    final_matrix += field_subsumption * field_subsumption_weight
    final_matrix -= field_similarities * field_similarity_weight

    tree = minimum_spanning_tree(final_matrix[lwords, :][:, lwords])

    graph = nx.Graph()
    rows, cols = tree.nonzero()

    for row, col in zip(rows, cols):
        source = topics[lwords[row]]
        target = topics[lwords[col]]
        graph.add_node(source)
        graph.add_node(target)
        graph.add_edge(source, target, weight=1, group=1)

    oriented_graph = oriented_graph_from_root(graph, get_root(lwords))

    nodes, links = graph_to_nodes_and_links(oriented_graph)
    return {"nodes": nodes, "links": links}


@app.get('/api/visualize/file_list')
async def json_file_list():
    return os.listdir("your json folder")


@app.get('/api/visualize')
async def visualize(filename: str = ""):
    try:
        with open("your json folder" + filename, "r") as fin:
            return json.load(fin)
    except:
        return {"error": "Unkwown graph file"}


@app.get('/')
async def status():
    return {"status": "alive"}

if __name__ == "__main__":
    uvicorn.run("your address:app",
                host="0.0.0.0",
                port=5020,
                reload=True,
                ssl_keyfile="/etc/ssl/certs/fi-group.com/wildcard.key",
                ssl_certfile="/etc/ssl/certs/fi-group.com/wildcard.crt"
                )
