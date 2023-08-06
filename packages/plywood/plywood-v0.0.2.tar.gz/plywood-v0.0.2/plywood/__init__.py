from plywood.grammar import *


class Block(object):
    pass


class Command(object):
    pass


class Plywood(object):
    """
    Takes a template and turns it into a tree of Commands
    """
    def __init__(self, template):
        self.parse(template, 0)

    def parse(self, template, offset):
        pass

    def __str__(object):
        pass


##|
##|  EXTENSIONS
##|
