"""Tests mockproc under nose"""
import unittest,subprocess
import mockproc

def setUp( self ):
    self.processes = mockproc.MockProc()
    self.processes.append( 'ls', stdout = '''total 20
drwxr-xr-x  2 mcfletch mcfletch 4096 2010-06-05 09:58 .
drwxr-xr-x 12 mcfletch mcfletch 4096 2010-06-05 09:58 ..
-rw-r--r--  1 mcfletch mcfletch    3 2010-06-05 09:58 supercali.txt''' )
    self.processes.enter()
def tearDown( self ):
    self.processes.exit()

class OverrideTest( unittest.TestCase ):
    def setUp( self ):
        '''Override ls for a particular test'''
        processes.append( 'ls', stdout = 'moo' )
    def tearDown( self ):
        processes.remove( 'ls' )
    def test_with_override( self ):
        stdout,stderr = subprocess.Popen( 'ls', stdout=subprocess.PIPE ).communicate()
        assert stdout == 'moo', stdout

class RegularTest( unittest.TestCase ):
    def test_without_override( self ):
        stdout,stderr = subprocess.Popen( 'ls', stdout=subprocess.PIPE ).communicate()
        assert 'supercali' in stdout, stdout
    def test_delete_nonexistent( self ):
        assert not processes.delete_script( { 'executable': 'blah' } ), """Should have reported failure!"""
    def test_remove_nonexistent( self ):
        assert not processes.remove( 'blah' ), """Should have reported failure"""

class MockProcTest( unittest.TestCase ):
    def test_mkbindir( self ):
        m = mockproc.MockProc( '\000' )
        self.failUnlessRaises( RuntimeError, m.enter )
    def test_exit( self ):
        m = mockproc.MockProc( )
        m.append( 'test', stdout='hello world' )
        m.enter()
        m.exit()
