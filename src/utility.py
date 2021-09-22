import os
import json
import pandas as pd
import networkx as nx
from networkx.algorithms.dag import transitive_reduction
import difflib
import const


class Utils:

    fileDir = os.path.dirname(os.path.abspath(__file__))
    data_dir = fileDir.replace("src", "data")
    # data_dir = os.path.join(fileDir, "data")

    @staticmethod
    def save_json(file_name, json_file):
        with open(os.path.join(Utils.data_dir, file_name), 'w') as outfile:
            json.dump(json_file, outfile)

    @staticmethod
    def load_json(file_name):
        with open(os.path.join(Utils.data_dir, file_name)) as outfile:
            json_file = json.load(outfile)

        return json_file

    @staticmethod
    def read_cats_reason(filename):
        cats_reasons = pd.read_csv(filename)
        return cats_reasons

    @staticmethod
    def read_unseens_reason(filename):
        reasons = pd.read_csv(filename)
        return reasons

    @staticmethod
    def merge(dic_a, dic_b):
        dic = dict()
        for key, values in dic_a.items():
            dic[key] = values + dic_b[key]

        return dic

    @staticmethod
    def get_seen_reason():
        seen_reason_file = os.path.join(Utils.data_dir, "all_seen_reasons.json")
        if os.path.exists(seen_reason_file):
            all_seen_reasons = Utils.load_json(seen_reason_file)
            return all_seen_reasons["all"]
        return []

    @staticmethod
    def get_all_edge(transitive_closure_table):
        all_edge = []
        if transitive_closure_table:
            for node in transitive_closure_table:
                for target in node.get('target'):
                    edge = (node.get("code"),target.get("code"))
                    all_edge.append(edge)

        return all_edge


    @staticmethod
    def shortest_path(transitive_closure_table, source, target):

        if source == target:
            return [source]
        edges = Utils.get_all_edge(transitive_closure_table)

        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        G = transitive_reduction(graph)
        path = []
        if G.has_node(source) and G.has_node(target):
            path = nx.shortest_path(G, source, target)
        return path
        # if path:
        #     return len(path)
        # return 0



    @staticmethod
    def similarity_words(phrase, candidate_codes):
        """
        :param line: input PFV
        :return:
            The most similarity defined section with the given line
        """

        #0 = True, 1 False
        if len(phrase)>4:
            threshold = const.LOW_THRESHOLD
        else:
            threshold = const.HIGH_THRESHOLD

        list_similarities = difflib.get_close_matches(phrase, candidate_codes, 1, threshold)

        # list_similarities = process.extractOne(phrase, candidate_codes,score_cutoff=const.HIGH_THRESHOLD*100)

        if list_similarities and len(list_similarities) > 0:
            return list_similarities[0], 0
        else:
            return "", 1



