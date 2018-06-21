#!/usr/local/bin/python
# coding: utf-8

class Error(Exception):
    """Base class for exceptions in this module."""

class ProofGraphError(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class NodeAttributeError(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class EdgeAttributeError(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
