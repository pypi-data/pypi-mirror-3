""" test tools module

Most of the tools in this module are tested indirectly in other modules.
"""
from rtools.tools import *


class Dummy():
    def __init__(self):
        pass

def test_RManual():
    d = RManualToDocString("base", "abbreviate")
    d.get_docstring()

    buildDocString("base","summary")

#@Rnames2attributes   
#def readMIDAS(file):  
#    return CNOR.readMIDAS(file)



#def test_names2attributes():
#    readMIDAS()



def test_convertor():
    c = RConvertor()
    c.convert(None)

    # test list of integers and IntVector
    rlist = c.convert([1,1,1])
    rlist2 = c.convert(rlist)

    # test FloatVector
    rlist = c.convert([1.,1.,1.])

    # test complexVector
    rlist = c.convert([1.j,1.,1.])

    # test strVector
    rlist = c.convert(["a","c","b"])

    # test boolVector
    rlist = c.convert([True, False])

    # test boolVector
    Dummy()
    try:
        c.convert([Dummy()])
        assert False
    except NotImplementedError:
        assert True

    # forcetype 
    rlist = c.convert([1.,1.,1.], forcetype=int)



















