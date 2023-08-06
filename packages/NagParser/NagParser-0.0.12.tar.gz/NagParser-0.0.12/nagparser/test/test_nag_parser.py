# Some basic Nose tests....
from nose.tools import *
import nagparser
import os


class test_nagparser():
    def setup(self):
        testdir, filename = os.path.split(os.path.abspath(__file__))
        basedir = testdir + '/data/'
        importantservicegroups = None
        files = [basedir + 'test_objects.cache', basedir + 'test_status.dat']
        
        self.config = nagparser.NagConfig(files = files)
        self.config.IMPORTANTSERVICEGROUPS = importantservicegroups
        self.lastupdated = '2011-10-31 12:08:22'
        
    def test_nag_objcreation(self):
        '''Just create the nag object, fail on any exception'''
        nag = nagparser.parse(self.config)
        
    
    def test_lastupdated_matches_testdata(self):
        '''Test to ensure the timestamp matches expected given test data'''
        nag = nagparser.parse(self.config)
        assert (str(nag.lastupdated) == str(self.lastupdated))
