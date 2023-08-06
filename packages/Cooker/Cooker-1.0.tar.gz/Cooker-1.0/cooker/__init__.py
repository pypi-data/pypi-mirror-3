"""
cooker

A tool for cooking programming problems from different sites
quickly.
"""
import sys
from subprocess import Popen
from subprocess import STDOUT
from subprocess import PIPE
from cooker import settings
from cooker.util import alert
from cooker.util import message
from cooker.util import compiler
from cooker.util import binary
from cooker.util import guess_language
from cooker.fs import FileSystem
from cooker.sites import CodeChef
from cooker.parser import DefaultArgParser

__author__ = "Nayan Shah (nayan@nayanshah.com)"
__copyright__ = "Copyright 2012, Nayan Shah"
__license__ = "MIT"
__all__ = ('sites', 'Cooker')


class Cooker():
    """
        Main Class for the package

    """

    def __init__(self, *args, **kwargs):
        pass


    @classmethod
    def cook(cls, arg_parser=DefaultArgParser, site=CodeChef):
        """Cook a problem and serve it

        @param argParser Return arguements to be used
        @param someSite A sub class of Site
        """

        # Parse command line arguements using the default parser
        parser = arg_parser()
        recipe = parser.parse()

        sites = { 'chef': CodeChef }
        settings.SITE = sites.get(recipe.get('site'), site)()

        cls.handle_command(recipe)


    @classmethod
    def handle_command(cls, recipe):
        """Command handler. Calls the required function."""

        commands = { 'setup': cls.setup,
                     'check': cls.check,
                     'add': cls.add,
                     'submit': cls.submit
                    }
        handler = commands.get(recipe.get('command'), cls.default)
        handler(recipe)


    @classmethod
    def setup(cls, recipe):
        """Setup the ingredients for a problem"""

        message('Gathering ingredients for %s' % recipe.get('problem'))

        ingredients = settings.SITE.get_data(**recipe)
        FileSystem.make_structure(**ingredients)

        message('%s is ready to be cooked!' % ingredients.get('name'))


    @classmethod
    def check(cls, recipe):
        """Compiles the code, executes it and verifies it
        against the given test cases.

        """

        guess_language()
        message('Compiling main\n')
        comp = Popen(compiler(), stderr=STDOUT)
        comp.communicate()
        if comp.returncode:
            alert('\nError during compilation.')

        message('Running code')
        inp = Popen(["cat", "input.txt"], stdout=PIPE)
        out = Popen(binary(), stdin=inp.stdout, stdout=PIPE)

        message('Comparing results with output.txt\n')
        test = Popen(["diff", "output.txt", "-"], stdin=out.stdout)
        result = test.communicate()

        if not test.returncode:
            message('Correct solution!')
        else:
            message("Program's output doesn't match output.txt")


    @classmethod
    def add(cls, recipe):
        """Add's a gived test case to existing ones."""
        message('Adding test cases to %s' % recipe.get('problem'))
        raise NotImplementedError


    @classmethod
    def submit(cls, recipe):
        """Serve the problem and wait for result"""

        message('Submitting code for %s' % recipe.get('problem'))
        settings.SITE.submit(**recipe)

        message('Problem has been served!')


    @classmethod
    def default(cls, recipe):
        """Default command handler"""
        message('Invalid command : %s' % recipe.get('command'))
        alert('Choose from : setup, check, add, submit')
