# Copyright (C) 2011 Oren Zomer <oren.zomer@gmail.com>

#                          *** MIT License ***
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import doctest
import inspect

class FullDocTestRunner(doctest.DocTestRunner):
    def report_success(self, out, test, example, got):
        if self._verbose and example.want:
            out('Got:\n')
            out('    %s' % (got,))
        doctest.DocTestRunner.report_success(self, out, test, example, got)

def testmod(m, name=None, globs=None, verbose=None,
            report=True, optionflags=0, extraglobs=None, exclude_empty=False):
    """
    fixed testmod function
    """
    # Check that we were actually given a module.
    if not doctest.inspect.ismodule(m):
        raise TypeError("testmod: module required; %r" % (m,))

    # If no name was given, then use the module's name.
    if name is None:
        name = m.__name__

    # Find, parse, and run all tests in the given module.
    finder = doctest.DocTestFinder(exclude_empty=exclude_empty)

    runner = FullDocTestRunner(verbose=verbose, optionflags=optionflags)

    for test in finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    if report:
        runner.summarize()

    if doctest.master is None:
        doctest.master = runner
    else:
        doctest.master.merge(runner)

    return doctest.TestResults(runner.failures, runner.tries)

def run_docstring_examples(f, globs, verbose=False, name="NoName",
                           compileflags=None, optionflags=0):
    # Find, parse, and run all tests in the given module.
    finder = doctest.DocTestFinder(verbose=verbose, recurse=False)
    runner = FullDocTestRunner(verbose=verbose, optionflags=optionflags)
    for test in finder.find(f, name, globs=globs):
        runner.run(test, compileflags=compileflags)


if __name__ == '__main__':
    import sys
    import os
    import os.path
    __dir__ = os.path.dirname(__file__)

    sys.path.insert(0, os.path.dirname(__dir__))

    __init__ = __import__(os.path.basename(__dir__))

    optionflags = doctest.ELLIPSIS
    
    args = sys.argv[1:]
    if len(args) == 0:
        print "Doctest Runner"
        print "Usage: "
        print "    python -m psifas all"
        print "    python -m psifas [filenames]"
        print "    python -m psifas [classnames]"
        sys.exit(0)
        
    if len(args) == 1 and args[0] == 'all':
        args = []
        os.path.walk(__dir__,
                     lambda _, dirname, names: args.extend(os.path.relpath(os.path.join(dirname, name), __dir__) for name in names
                                                           if name.lower().endswith('.py') and not name.startswith('__')),
                     None)
    for arg in args:
        module_name, ext = os.path.splitext(arg)
        if ext.lower() == '.py':
            module = __init__
            for package_name in module_name.split(os.path.sep):
                module = getattr(module, package_name, None)
            if not inspect.ismodule(module):
                print "*** Module %s could not be imported ***" % (arg,)
                continue
            testmod(module, globs = __init__.__dict__, verbose = True, optionflags = optionflags, exclude_empty = True)
        else:
            run_docstring_examples(getattr(__init__, arg), __init__.__dict__, verbose = True, name = arg, optionflags = optionflags)

