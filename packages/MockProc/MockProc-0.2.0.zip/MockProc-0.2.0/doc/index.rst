.. highlight:: python
   :linenothreshold: 5

MockProc for Python, Subprocess Stubs for Tests
===============================================

MockProc is a mechanism that allows you to stub out subprocesses during testing 
to test handling of subprocess behaviours including timeout handling, output 
processing, input processing and the like.

Standard usage is to use a MockProc as a context manager so that it will clean up 
when the block of code has exited.  This can also be accomplished by using e.g. 
tearDown to call :py:meth:`mockproc.mockprocess.MockProc.exit` to clean up.  Generally you 
will not call :py:meth:`mockproc.mockprocess.MockProc.enter` in the setUp unless you want 
every test to have the same mocked-out processes::

    from mockproc import mockprocess
    class Test( unittest.TestCase ):
        def setUp( self ):
            self.scripts = mockprocess.MockProc()
        
        def test_subprocess_fail( self ):
            self.scripts.append( 'process-name', returncode=1 )
            
            with self.scripts:
                run_and_handle_result()
        
        def test_subprocess_output( self ):
            self.scripts.append( 'process-name', returncode=0, stdout="output to process" )
            
            with self.scripts:
                run_and_handle_result()
        
        def test_timeout_with_custom_script( self ):
            self.scripts.append('process-name',returncode = 0,script='''#! /usr/bin/env python
    import time 
    time.sleep( 2.0 )
    ''')
            with self.scripts:
                run_and_handle_result()

        def test_large_output_with_custom_script( self ):
            self.scripts.append('process-name',returncode = 0,script='''#! /usr/bin/env python
    for i in range( 100000 ):
        print 'a'*10000
    ''')
            with self.scripts:
                run_and_handle_result()


How it Works
------------

:py:class:`mockproc.mockprocess.MockProc` instances create a temporary directory into which 
they write executable scripts.  This temporary directory is then added to the current process'
``PATH`` when the instance is `entered` (either by calling :py:meth:`mockproc.mockprocess.MockProc.enter`
or by using the "with" statement in later versions of Python).

The default script which is written simply consumes standard in, writes to stdout and stderr (if provided)
and then exits with the indicated return code.  You can provide your own script using the "script" 
argument to :py:meth:`mockproc.mockprocess.MockProc.append`.

Installation
------------

Standard Python library installation from `PyPI`_:

.. code-block:: bash

    $> source my-virtual-env/bin/activate
    $> pip install mockproc
    
To help contribute/develop MockProc, install `bzr`_ and then use the following command:

.. code-block:: bash

    $> pip install -e bzr+http://bazaar.launchpad.net/~mcfletch/mockproc/trunk#egg=MockProc

Which will install MockProc into your VirtualEnv's src directory in an editable format.
The `LaunchPad Project`_ can be used to report bugs, or you can contact the `author`_ directly.

.. _PyPI: http://pypi.python.org/pypi/MockProc/
.. _bzr: http://bazaar.canonical.com/
.. _`LaunchPad Project`: https://launchpad.net/mockproc
.. _author: http://www.vrplumber.com
                
Limitations
-----------

There are a number of major limitations to MockProc due to the current implementation:

    * cannot stub out executables which are referenced by their full path ``/usr/bin/executable``
        * parameterize these executables and use a library such as globalsub to replace the 
          parameter for the duration of the test
    * likely only works on Unix-like operating systems due to the template script used
        * on Microsoft Windows the script should run, but would likely require a few other 
          environment variables and potentially a rename of the files (to have .py extensions)
          to make them executable
    * will not give you any notice if the mocking/faking fails
    * it is not thread safe; modifies os.environ to include its path, so the whole process will 
      be mocked, not just the current thread
                
Contents:

.. toctree::
   :maxdepth: 2

   mockproc
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

