#
# Test the conversion to FD
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

import re
import glob

import pyutilib.th as unittest
import coopr.pyomo.scripting.pyomo as main
from coopr.pyomo import *
import pyutilib.misc
import coopr.openopt

try:
    import FuncDesigner
    FD_available=True
except:
    FD_available=False

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


@unittest.category('nightly')
class NightlyTests(Tests):

    def __init__(self, *args, **kwds):
        Tests.__init__(self, *args, **kwds)


@unittest.category('smoke', 'nightly')
class SmokeTests(Tests):

    def __init__(self, *args, **kwds):
        Tests.__init__(self, *args, **kwds)


skip_files = set(['aircrfta', 'artif', 'booth','chemrctb', 'core1','corkscrw', 'eg1','eg2','eg3', 'drcav3lq', 'dtoc1l', 'expfit', 'tfi2','synthes1', 'sosqp1', 's368', 'robot', 'oet1', 'makela3', 'polak1', 'tame', 'mifflin2', 'mifflin1', 'makela4', 'makela2', 'makela1', 'extrasim', 'demymalo', 'chaconn2', 'chaconn1', 'bt1'])
smoke_files = set( ['bqp1var', 'explin', 'extrasim', 'tame', 'sim2bqp', 'denschna', 'rosenbr', 'bt10', 'sisser', 'denschnb', 'eg1', 'mifflin1', 'makela1', 'bt1', 'denschnc', 'demymalo', 'zy2', 'mifflin2', 'polak1', 'bt9', 'byrdsphr', 'makela2', 'bt2', 'camel6', 'aljazzaf', 'chaconn1', 'chaconn2', 'csfi2', 'bt13', 'cantilvr', 'bt3', 'cb2', 'cb3', 'makela4', 'matrix2'])


@unittest.nottest
def fd_test(self, name):
    #print name
    if name in skip_files:
        unittest.skip('Ignoring test '+name)
        return
    model = pyutilib.misc.import_file(currdir+name+'_cute.py')
    if os.path.exists(currdir+name+'.dat'):
        instance = model.model.create(currdir+name+'.dat')
    else:
        instance = model.model.create()
    #
    pvals = {}
    for oname, obj in instance.active_components(Objective).iteritems():
        for key in obj.keys():
            pvals[oname, key] = obj[key]()
            fname = (oname, key)
            break
    #for cname, con in instance.active_components(Constraint).iteritems():
        #for key in con.keys():
            #pvals[cname, key] = con[key]()
    #
    S = coopr.openopt.Pyomo2FuncDesigner(instance)
    oval = S.f(S.initial_point)
    self.assertAlmostEqual(pvals[fname], oval, places=7)



if FD_available:
    for f in glob.glob(currdir+'*_cute.py'):
        name = re.split('[._]',os.path.basename(f))[0]
        if name in smoke_files:
            SmokeTests.add_fn_test(fn=fd_test, name=name)
        else:
            NightlyTests.add_fn_test(fn=fd_test, name=name)


if __name__ == "__main__":
    unittest.main()
