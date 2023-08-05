__version__ = '0.2.0'

#------------------------------------------------------------------------------
try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except:
    pass
#------------------------------------------------------------------------------
