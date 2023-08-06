__version__ = '0.2.2'

#------------------------------------------------------------------------------
try:
    from numpy.testing import nosetester
    test = nosetester.NoseTester().test
    del nosetester
except:
    pass
#------------------------------------------------------------------------------
