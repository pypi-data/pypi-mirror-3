#
# Test the Pyomo command-line interface
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
datadir = os.path.normpath(currdir+'../../../../coopr.pyomo/examples/pyomo/p-median/')+os.sep
print datadir

from coopr.pyomo import *
import pyutilib.th as unittest
import coopr.pyomo.scripting.convert as convert
import re
import glob


@unittest.category('performance')
class Test(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(currdir)

    def tearDown(self):
        os.chdir(self.cwd)


@unittest.category('performance')
class Test1(Test):

    def test1(self):
        res = convert.pyomo2nl(['--save-model',currdir+'test1.nl',datadir+'pmedian.py',datadir+'pmedian.dat'])
        if not os.path.exists(currdir+'test1.nl'):
            raise ValueError, "Missing file test1.nl generated in test1"
        os.remove(currdir+'test1.nl')
        if not res.options.max_memory is None:
            self.recordTestData('maximum memory used', res.options.max_memory)

    def test2(self):
        res = convert.pyomo2lp(['--save-model',currdir+'test2.lp',datadir+'pmedian.py',datadir+'pmedian.dat'])
        if not os.path.exists(currdir+'test2.lp'):
            raise ValueError, "Missing file test2.lp generated in test2"
        os.remove(currdir+'test2.lp')
        if not res.options.max_memory is None:
            self.recordTestData('maximum memory used', res.options.max_memory)

@unittest.category('performance')
class Test2(Test):
    pass


@unittest.category('performance')
class Test3(Test):
    pass


@unittest.nottest
def nl_test(self, name):
    fname = currdir+name+'.nl'
    root = name.split('_')[1]
    #print >>sys.stderr, fname
    res = convert.pyomo2nl(['--save-model',fname]+self.get_options(name)+[datadir+root+'.dat'])
    if not os.path.exists(fname):
        raise ValueError, "Missing file %s generated in test2" % fname
    os.remove(fname)
    if not res.options.max_memory is None:
        self.recordTestData('maximum memory used', res.options.max_memory)

@unittest.nottest
def lp_test(self, name):
    fname = currdir+name+'.lp'
    root = name.split('_')[1]
    #print >>sys.stderr, fname
    res = convert.pyomo2lp(['--save-model',fname]+self.get_options(name)+[datadir+root+'.dat'])
    if not os.path.exists(fname):
        raise ValueError, "Missing file %s generated in test2" % fname
    os.remove(fname)
    if not res.options.max_memory is None:
        self.recordTestData('maximum memory used', res.options.max_memory)


for i in range(8):
    name = 'test'+str(i+1)
    #
    Test2.add_fn_test(fn=nl_test, name='nl_pmedian.'+name, options=[datadir+'pmedian.py'])
    Test2.add_fn_test(fn=nl_test, name='nl-O_pmedian.'+name, options=['--disable-gc', datadir+'pmedian.py'] )
    if i < 4:
        Test3.add_fn_test(fn=nl_test, name='nl-memcov_pmedian.'+name, options=['--profile-memory','1',datadir+'pmedian.py'] )
    #
    Test2.add_fn_test(fn=lp_test, name='lp_pmedian.'+name, options=[datadir+'pmedian.py'])
    Test2.add_fn_test(fn=lp_test, name='lp-O_pmedian.'+name, options=['--disable-gc', datadir+'pmedian.py'] )
    if i < 4:
        Test3.add_fn_test(fn=lp_test, name='lp-memcov_pmedian.'+name, options=['--profile-memory','1',datadir+'pmedian.py'] )


if __name__ == "__main__":
    unittest.main()
