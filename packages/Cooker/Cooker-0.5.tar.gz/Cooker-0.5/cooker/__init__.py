"""
cooker

A tool for cooking programming problems from different sites
quickly.
"""
from cooker import settings
from cooker.fs import FileSystem
from cooker.sites import CodeChef
from cooker.parser import DefaultArgParser

__author__ = "Nayan Shah (nayan@nayanshah.com)"
__copyright__ = "Copyright 2012, Nayan Shah"
__license__ = "MIT"


class Cooker():
    """
        Main Class for the package

    """

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def cook(cls):
        """Cook a problem and serve it"""

        recipe = cls.parse()
        print 'Gathering ingredients for %s' % recipe.get('problem')

        chef = CodeChef()
        ingredients = chef.get_data(**recipe)
        FileSystem.make_structure(**ingredients)

        print '%s is ready to be served!' % ingredients.get('name')


    @classmethod
    def parse(cls):
        """Parse command line arguements using the default parser

        """

        parser = DefaultArgParser()
        args = parser.parse()

        settings.LANG = args.language

        return { 'problem': args.problem,
                 'path': args.path,
                 'contest': args.contest,
                 'url': args.url,
                 'site': args.site }
