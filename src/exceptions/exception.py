#!/usr/local/bin/python
# coding: utf-8

"""
'exception' module has all exceptions raised.
"""


class Error(Exception):
    """
    Base class for exceptions in this module.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class FileError(Error):
    """
    Exception raised if an error occurs while reading the file 'dot'.
    """

    def __init__(self, message, path):
        Error.__init__(self, message)
        self.path = path

    def __str__(self):
        message = "The file '{0}' {1}".format(self.path, self.message)
        return message


class GraphError(Error):
    """
    Base class for exceptions raised in GraphAdapter object.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NodeGraphError(GraphError):
    """
    Exception raised if an error occurs in node of GraphAdapter object.
    """

    def __init__(self, node, message):
        GraphError.__init__(self, message)
        self.node = node

    def __str__(self):
        message = "The node {0} {1}".format(self.node, self.message)
        return message


class EdgeGraphError(GraphError):
    """
    Exception raised if an error occurs in edge of GraphAdapter object.
    """

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
    """
    Exception raised if an error occurs in node attribute of
    GraphAdapter object.
    """

    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class EdgeAttributeGraphError(GraphError):
    """
    Exception raised if an error occurs in edge attribute of
    GraphAdapter object.
    """

    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class ProofGraphError(Error):
    """
    Base class for exceptions raised in ProofGraph object.
    """

    def __init__(self, message):
        Error.__init__(self, message)

    def __str__(self):
        return self.message


class NodeProofGraphError(ProofGraphError):
    """
    Exception raised if an error occurs in node of ProofGraph object.
    """

    def __init__(self, node, message):
        ProofGraphError.__init__(self, message)
        self.node = node

    def __str__(self):
        message = "The node {0} {1}".format(self.node, self.message)
        return message


class EdgeProofGraphError(ProofGraphError):
    """
    Exception raised if an error occurs in edge of ProofGraph object.
    """

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
    """
    Exception raised if an error occurs in node attribute of
    ProofGraph object.
    """

    def __init__(self, attribute, message):
        ProofGraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class EdgeAttributeProofGraphError(ProofGraphError):
    """
    Exception raised if an error occurs in edge attribute of
    GraphAdapter object.
    """

    def __init__(self, attribute, message):
        ProofGraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class WrongSettingGraphError(ProofGraphError):
    """
    Exception raised if a method in ProofGraph is called with a wrong
    setting.
    """

    def __init__(self, method, message):
        ProofGraphError.__init__(self, message)
        self.method = method

    def __str__(self):
        message = "The setting of method {0}".format(self.method)
        return message
