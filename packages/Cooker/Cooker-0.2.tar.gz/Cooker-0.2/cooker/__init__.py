"""
    Programming Problem Sites Utilities
"""

__author__ = "Nayan Shah (nayan@nayanshah.com)"
__copyright__ = "Copyright 2012, Nayan Shah"
__license__ = "MIT License"

import os

from shutil import copyfile
from cooker.sites import CodeChef
from cooker.sites import CodeChefLocal

TEMPLATE='/etc/cooker/template.cpp'

"""
    Main Class for the package
"""

class Cooker():

    def cook(self, problem, contest='', path='.'):
        """Cook a problem and serve it
        """

        print 'Gathering ingredients to cook %s' % problem
        title = make_structure(problem, contest, path)
        print '%s is ready to be served!' % title


    def create_file(self, name, contents):
        """Create a new file with given name and save it with
        given contents.
        """

        f = open(name, 'w')
        f.write(contents)
        f.close()

    def make_structure(self, problem, contest='', path='.'):
        """Setup the directory structure at the given path with:
         ./main.cpp     (Template file)
         ./input.txt        (Sample input)
         ./output.txt       (Program's output)
         ./test.txt         (Sample output)

         @return Title of the problem
        """
        # Get the problem test cases
        cc = CodeChef()
        title, inp, out = cc.problem_data(problem, contest)

        # Create destination directory
        base = '.'
        dest = '%s/%s/' % (base, problem.lower())
        os.mkdir(dest, 0755)

        # Make files
        files = { 'input.txt': inp, 'output.txt': out, 'test.txt': out }
        for k in files:
            self.create_file(dest + k, files.get(k))
        copyfile(TEMPLATE, dest + 'main.cpp')

        return title
