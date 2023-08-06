from __future__ import absolute_import
from ..buml.mappingSpec import *


def test_mappingSpec():
    "mappingSpec: mappingSpec and Item"
    def emHandler(): pass
    def strongHandler(): pass
    m = MappingSpec()
    assert m == []
    m.append(MappingSpecItem('*', '*', emHandler))
    assert m._startTagPattern == None
    assert m._mappingDict == None
    assert m.mappingDict().keys() == ['*']
    m.append(MappingSpecItem('**', '**', strongHandler))
    assert m._startTagPattern == None
    assert m._mappingDict == None
    assert m.mappingDict().keys() == ['*', '**']
    assert m.startTagPattern is not None
