#!/usr/local/bin/python
# coding: utf-8


class Error(Exception):
    """
    Base class for exceptions in this module.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class FileError(Error):

    def __init__(self, message, path):
        Error.__init__(self, message)
        self.path = path

    def __str__(self):
        message = "The file '{0}' {1}".format(self.path, self.message)
        return message


class GraphError(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NodeGraphError(GraphError):
    def __init__(self, node, message):
        GraphError.__init__(self, message)
        self.node = node

    def __str__(self):
        message = "The node {0} {1}".format(self.node, self.message)
        return message


class EdgeGraphError(GraphError):
    def __init__(self, source, target, message):
        GraphError.__init__(self, message)
        self.source = source
        self.target = target

    def __str__(self):
        message = "The edge ({0}, {1}) {2}".format(self.source,
                                                   self.target,
                                                   self.message)
        return message


class NodeAttributeGraphError(GraphError):
    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class EdgeAttributeGraphError(GraphError):
    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class ProofGraphError(Error):
    def __init__(self, message):
        Error.__init__(self, message)

    def __str__(self):
        return self.message


class NodeProofGraphError(ProofGraphError):
    def __init__(self, node, message):
        ProofGraphError.__init__(self, message)
        self.node = node

    def __str__(self):
        message = "The node {0} {1}".format(self.node, self.message)
        return message


class EdgeProofGraphError(ProofGraphError):
    def __init__(self, source, target, message):
        ProofGraphError.__init__(self, message)
        self.source = source
        self.target = target

    def __str__(self):
        message = "The edge ({0}, {1}) {2}".format(self.source,
                                                   self.target,
                                                   self.message)
        return message


class NodeAttributeProofGraphError(ProofGraphError):
    def __init__(self, attribute, message):
        ProofGraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class EdgeAttributeProofGraphError(ProofGraphError):
    def __init__(self, attribute, message):
        ProofGraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class WrongSettingGraphError(ProofGraphError):
    def __init__(self, method, message):
        ProofGraphError.__init__(self, message)
        self.method = method

    def __str__(self):
        message = "The setting of method {0}".format(self.method)
        return message
