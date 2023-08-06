def warning(msgStr):
    print "Warning: %s" % msgStr

def findPatternPos(inStr, pattern):
    "for re what find is for string: returns pos of first separator or -1"
    match = pattern.search(inStr)
    if match:
        return match.span()[0]
    else:
        return -1

def reQuote(pattStr):
    "quote special characters in re patter component"
    QUOTE_CHR = '\\'
    l = list(pattStr)
    l = [QUOTE_CHR + c for c in l]
    return ''.join(l)


def addrNameFromString(inStr):
    """parses name and address from string

       formats:
          'name <address>'
          'addrSameAsName'
    """
    l = inStr.split('<')
    if len(l) == 1:
        name = addr = inStr
    elif len(l) == 2:
        name = l[0]
        addr = l[1]
    else:
        raise Exception('unexpected format of addrStr: %s' % inStr)
    name = name.strip()
    if addr[-1] == '>':  
        addr = addr[:-1]
    addr = addr.strip()
    return (addr, name)


#class MappingSpec(list):
#    "how to map syntactic tokens to elements"
#
#    def __init__(self):
#        list.__init__(self)
#        self._startTagPattern = None
#        self._mappingDict = None
#
#    def mappingDict(self):
#        "mappingSpecItems indexed by startTag for easy use"
#        if not self._mappingDict:
#            self._mappingDict = dict([[i.startTag, i] for i in self])
#        return self._mappingDict
#
#    def startTagPattern(self):
#        if not self._startTagPattern:
#            self._startTagPattern = tagsPattern(self.mappingDict.keys())
#        return self._startTagPattern
#
#    def append(self, item):
#        list.append(self, item)
#        self._mappingDict = None
#        self._startTagPattern = None
#
#class MappingSpecItem(object):
#    def __init__(self, startTag, endTag, mappingFunc, singleWord=False):
#        """start and endTag are strings, 
#           mappingFunc maps a txt to a list of nodes
#        """
#        self.startTag = startTag
#        self.endTag = endTag
#        self.func = mappingFunc
#        self.singleWord = singleWord
#        self.endTagPattern = endTagPattern(self.endTag, self.singleWord)
#
#
# 
#
#
#    
