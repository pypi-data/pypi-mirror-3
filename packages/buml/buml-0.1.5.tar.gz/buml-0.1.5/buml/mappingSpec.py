from inlineParser import endTagPattern, tagsPattern


class MappingSpec(list):
    "how to map syntactic tokens to elements"

    def __init__(self):
        list.__init__(self)
        self._startTagPattern = None
        self._mappingDict = None

    def mappingDict(self):
        "mappingSpecItems indexed by startTag for easy use"
        if not self._mappingDict:
            self._mappingDict = dict([[i.startTag, i] for i in self])
        return self._mappingDict

    def startTagPattern(self):
        if not self._startTagPattern:
            self._startTagPattern = tagsPattern(self.mappingDict().keys())
        return self._startTagPattern

    def append(self, item):
        list.append(self, item)
        self._mappingDict = None
        self._startTagPattern = None

class MappingSpecItem(object):
    def __init__(self, startTag, endTag, handler, singleWord=False):
        """start and endTag are strings, 
           mappingFunc maps a txt to a list of nodes
        """
        self.startTag = startTag
        self.endTag = endTag
        self.handler = handler
        self.singleWord = singleWord
        self.endTagPattern = endTagPattern(self.endTag, self.singleWord)


