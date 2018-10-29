#!/usr/local/bin/python
# coding: utf-8


class FlowColor:

    def __init__(self, formulas_index):
        self.dictionary = {}
        self.formulas = formulas_index

    def get(self, color):
        if color in self.dictionary:
            return self.dictionary[color]
        else:
            return None

    def set(self, color, bit_vector, path):
        if not bit_vector and not path:
            self.dictionary[color] = None
        else:
            self.dictionary[color] = (bit_vector, path)

    def reset(self):
        for color in self.dictionary.keys():
            self.dictionary[color] = None


class FlowEdge:

    def __init__(self):
        self.dictionary = {}

    def get_edges_by_color(self, color):
        edges = []
        for edge, color_dict in self.dictionary.items():
            if color in color_dict:
                if color_dict[color]:
                    edges.append(edge)
        return edges

    def get(self, source, target, color):
        value = None
        if (source, target) in self.dictionary:
            if color in self.dictionary[(source, target)]:
                value = self.dictionary[(source, target)][color]
        return value

    def set(self, source, target, color, value):
        self.dictionary[(source, target)] = {color: value}
