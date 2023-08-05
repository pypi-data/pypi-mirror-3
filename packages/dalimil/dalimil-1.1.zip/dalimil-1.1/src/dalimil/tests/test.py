'''
Created on 9.11.2010

@author: javl
'''
import unittest
import os
import shutil
import datetime
import time
from dalimil import dalimil

class Test(unittest.TestCase):
    datasrc = "datasrc"
    default_archive = "archive"

    def kill_tree(self, top):
        # Delete everything reachable from the directory named in "top",
        # assuming there are no symbolic links.
        # CAUTION:  This is dangerous!  For example, if top == '/', it
        # could delete all your disk files.
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))            
                pass
            os.rmdir(root)            
        return

    def setUp(self):
        #and make sure the dir exists
        if not os.path.exists(self.datasrc):
            os.makedirs(self.datasrc)
        #populate with some data
        dates = [
                 "2010-11-01T12:22:10",
                 "2010-11-01T13:22:10",
                 "2010-11-01T14:22:10",
                 "2010-11-02T12:22:10",
                 "2010-11-02T20:22:10",
                 "2010-11-02T21:22:10",
                 datetime.datetime.now().isoformat()[:19],
                 datetime.datetime.now().isoformat()[:19]
                ]
        i = 0
        for dt in dates:
            i = i+1
            dt_struct = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
            dt_timestamp = time.mktime(dt_struct.timetuple())
            dt_yearago = dt_struct
            dt_yearago.replace(year = dt_yearago.year - 1) 
            dt_yearago = time.mktime(dt_yearago.timetuple())
            fname = self.datasrc + "/" + dt[:10] + "_" + str(i)+ "_123.xml"
            try:
                with open(fname, "w") as f:
                    f.write(fname)
                os.utime(fname, (dt_yearago, dt_yearago))
            except:
                print "Problem in SetUp"
                pass
        return


#    def tearDown(self):
#        #remove source test fiels, if they exists
#        self.kill_tree(self.datasrc)
#        self.kill_tree(self.default_archive)
#        print "Tear down"
#        return
        
    def testList(self):
        #list actions
        argline = "-action list" + " " + self.datasrc + "/*"   
        dalimil.main(argline.split())
        #todo: check somehow, that something is printed out
        return
    
    def testCopy2Zip(self):
        #list actions
        argline = "-action copy2zip" + " " + self.datasrc + "/*"    
        dalimil.main(argline.split())
        #todo: check, that source files are still there
        #todo: check, that expected archives are created
        return
    
    def testMove2Zip(self):
        #list actions
        argline = "-action move2zip" + " " + self.datasrc + "/*"    
        dalimil.main(argline.split())
        #todo: check, that source files from completed periods are removed
        #todo: check, that source files from current time period are still present
        #todo: check, that expected archives are created
        return
    

    def testEasyScenario(self):
        #minimal set of parameters
        print "testing"
        pass

    def testPatternTimeDetection(self):
        #minimal set of parameters
        print "testing"
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testEasyScenario']
    unittest.main()
