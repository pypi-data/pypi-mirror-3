import os,tempfile,shutil,logging
log = logging.getLogger( __name__ )

__all__ = ('MockProc',)

class MockProc( object ):
    """Provides basic path-overriding process mocks for nose (or similar) test frameworks

    You would normally use a MockProc where you have code which uses subprocess
    to call an external program which would have negative effects were it to
    actually be called within your test framework.
    
    You can (optionally) provide a "bindir" argument to the MockProc to specify where 
    the executable scripts should be written (e.g. to avoid having the scripts written 
    into a noexec partition).
    
    Note: cleanup for the MockProc unconditionally removes bindir (even if you created it)
    when .exit() is called.
    """
    def __init__( self, bindir=None ):
        self.scripts = {}
        self.bindir = bindir
    def __enter__( self ):
        """Write scripts to bindir (possibly creating it) and set PATH to use it"""
        if not self.bindir:
            self.bindir = tempfile.mkdtemp()
        bindir = self.bindir
        try:
            if not os.path.isdir( bindir ):
                os.makedirs( bindir )
        except (IOError,OSError,TypeError), err:
            log.warn( 'Could not create bin directory for mocks: %s', bindir )
            raise RuntimeError( """Unable to create test binary directory: %s"""%( bindir, ))
        os.environ['PATH'] = self.bindir + os.pathsep + os.environ.get( 'PATH', '' )
        for scripts in self.scripts.values():
            if scripts:
                self.write_script( scripts[-1] )
    enter = __enter__
    def __exit__( self, exit=None, value=None, exception=None ):
        """Delete bindir and remove from PATH"""
        if self.bindir:
            os.environ['PATH'] = os.environ.get( 'PATH', '' ).replace( os.pathsep + self.bindir, '' )
            for scripts in self.scripts.values():
                if scripts:
                    self.delete_script( scripts[-1] )
            shutil.rmtree( self.bindir, ignore_errors=True )
    exit = __exit__
    def write_script( self, description ):
        if not description.get('script'):
            description['script'] = self.script_template % description
        description['filename'] = filename = os.path.join( self.bindir, description['executable'] )
        fh = open( filename, 'w' )
        fh.write( description['script'] )
        fh.close()
        os.chmod( filename,0755 )
        return filename
    def delete_script( self, description ):
        try:
            filename = os.path.join( self.bindir, description['executable'] )
            os.remove( filename )
        except (OSError,IOError,TypeError), err:
            return False
        else:
            return True

    def append(
        self,
        executable,
        returncode = 0,
        stdout = None,
        stderr = None,
        script = None,
    ):
        """Add a new script to the bin-dir, 'pushes' the script into the stack...
        
        executable -- the name of the executable, note that this must be a 
        PATH-lookup executable name, *not* a full path to an executable
                      
        returncode -- the return code to return from the executable (script)
        
        stdout -- the standard output for the process, if None, nothing will be output
        
        stderr -- the standard error for the process, if None, nothing will be output 
        
        script -- allows you to specify the script to be written, e.g. to allow you 
        to simulate a process which takes a very long time, or produces extremely 
        large amounts of output/errors.

        returns the internal description of the script (basically the parameters as a 
        dictionary)
        """
        if not executable:
            raise ValueError( """Null executable not allowed""" )
        if os.path.basename( executable ) != executable:
            raise ValueError( """Only base-name executables can be overridden""" )
        description = {
            'executable': executable,
            'returncode': returncode,
            'stdout': stdout,
            'stderr': stderr,
            'script': script,
        }
        self.scripts.setdefault(executable,[] ).append( description )
        if self.bindir:
            self.write_script( description )
        return description
    def remove( self, executable ):
        """Pop the current executable from our set of scripts
        
        If the MockProc is currently live, will also delete the script
        when the last executable of this name is removed, or write the 
        next version of the executable into the scripts directory.
        """
        try:
            scripts = self.scripts[executable]
            script = scripts.pop()
        except (KeyError,IndexError), err:
            return None
        else:
            if not scripts:
                if self.bindir:
                    self.delete_script( executable )
                del self.scripts[executable]
            else:
                if self.bindir:
                    self.write_script( scripts[-1] )
            return script

    script_template = """#! /usr/bin/env python

# mocked implementation of %(executable)s

import os,sys
stdout = %(stdout)r
stderr = %(stderr)r
if stdout:
    sys.stdout.write( stdout )
if stderr:
    sys.stderr.write( stderr )
sys.exit( %(returncode)s )
"""
