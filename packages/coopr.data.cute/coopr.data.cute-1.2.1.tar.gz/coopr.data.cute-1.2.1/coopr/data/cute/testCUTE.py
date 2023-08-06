#
# Test the NL writer on a subset of the CUTE test cases
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

#import time
import re
import glob

import pyutilib.th as unittest
import pyutilib.th as unittest
import coopr.pyomo.scripting.pyomo as main
from coopr.pyomo import *


class Tests(unittest.TestCase):

    def pyomo(self, cmd):
        #args=re.split('[ ]+',cmd)
        os.chdir(currdir)
#       t0= time.clock()
        #output = main.run(cmd+['--debug'])
        output = main.run(['-q', '-c']+cmd)
#       t1 = time.clock() - t0 # t is CPU seconds elapsed (floating point)
#       print "Seconds: " + str(t1)
        return output


#@unittest.category('nightly')
class NightlyTests(Tests):

    def __init__(self, *args, **kwds):
        Tests.__init__(self, *args, **kwds)
NightlyTests = unittest.category('nightly')(NightlyTests)


#@unittest.category('smoke', 'nightly')
class SmokeTests(Tests):

    def __init__(self, *args, **kwds):
        Tests.__init__(self, *args, **kwds)
SmokeTests = unittest.category('smoke', 'nightly')(SmokeTests)


skip_files = set(['aircrfta', 'artif', 'brownden', 'cvxqp3', 'corkscrw', 'drcav3lq','dtoc1l','gigomez1','hager3','fletcher','fletchbv','makela2', 'makela4', 'mifflin1', 'ncvxbqp1','polak1', 'rosenbr','srosenbr','tridia', 'zy2', 'core1', 'hager4'])
smoke_files = set( ['bqp1var', 'extrasim', 'booth', 'tame', 'sim2bqp', 'denschna', 'rosenbr', 'bt10', 'sisser', 'denschnb', 'eg1', 'mifflin1', 'makela1', 'bt1', 'denschnc', 'demymalo', 'zy2', 'mifflin2', 'polak1', 'bt9', 'byrdsphr', 'makela2', 'bt2', 'camel6', 'aljazzaf', 'chaconn1', 'chaconn2', 'csfi2', 'bt13', 'cantilvr', 'bt3', 'cb2', 'cb3', 'makela4', 'matrix2'])

@unittest.nottest
def pyomo_test(self, name):
    if name in skip_files:
        unittest.skip('Ignoring test '+name)
        return
    if os.path.exists(currdir+name+'.dat'):
        self.pyomo(['--save-model='+currdir+name+'.test.nl',
                    currdir+name+'_cute.py',
                    currdir+name+'.dat'])
        self.assertFileEqualsBaseline(currdir+name+'.test.nl', currdir+name+'.pyomo.nl', tolerance=1e-7)
    else:
        self.pyomo(['--save-model='+currdir+name+'.test.nl',
                    currdir+name+'_cute.py'])
        self.assertFileEqualsBaseline(currdir+name+'.test.nl', currdir+name+'.pyomo.nl', tolerance=1e-7)
    io.ampl.ampl_var_id = {}
    io.ampl.var_ampl_repn_dict = {}
    with open('cute.log', 'w') as f:
        print >>f, dir()
        print >>f, name
        print >>f, self
        print >>f, dir(self)


for f in glob.glob(currdir+'*_cute.py'):
    name = re.split('[._]',os.path.basename(f))[0]
    if name in smoke_files:
        SmokeTests.add_fn_test(fn=pyomo_test, name=name)
    else:
        NightlyTests.add_fn_test(fn=pyomo_test, name=name)

if __name__ == "__main__":
    unittest.main()
