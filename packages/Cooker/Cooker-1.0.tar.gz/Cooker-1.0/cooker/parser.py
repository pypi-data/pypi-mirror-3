"""
parser

Generic parsers

"""
import argparse
from HTMLParser import HTMLParser
from cooker import settings

class DefaultArgParser():
    """
    Command line arguements parser

    """

    def __init__(self):
        pass


    @classmethod
    def create_parser(cls):
        """Create a default command line parser"""
        parser = argparse.ArgumentParser(
                    prog='cook',
                    description="""Utility for various
                            programming problem sites""")
        parser.add_argument(
                    '--version', action='version',
                    version='%(prog)s 1.0')
        parser.add_argument('command', default='.',
                           help='command : setup, check')
        parser.add_argument('-d', '--directory', default='.',
                           help='path where the folder is to be created')
        parser.add_argument('-l', '--language', default='',
                           help='language to use (c, cpp, java, py)')
        parser.add_argument('-q', '--question', default='',
                           help='question code for given site')
        parser.add_argument('-u', '--url', default='',
                           help='direct url for the problem')
        parser.add_argument('-c', '--contest', default='',
                           help='contest id for given site')
        parser.add_argument('-s', '--site', default='',
                           help='problem site (default: CodeChef)')

        return parser


    @classmethod
    def parse(cls):
        """Parse command line arguements and returns the values

        """
        parser = cls.create_parser()
        args = parser.parse_args()

        if args.language:
            settings.LANG = args.language

        return { 'command': args.command,
                 'problem': args.question,
                 'path': args.directory or settings.DIRECTORY,
                 'contest': args.contest or settings.CONTEST,
                 'url': args.url,
                 'site': args.site or settings.SITE
                }


class HTMLTagsParser(HTMLParser):
    """
    Generic HTML Parser which returns the contents of the tags specified.

    """

    def __init__(self, tags):
        HTMLParser.__init__(self)
        self.tags = tags
        self.save = False
        self.data = {}
        self.current = ''


    def get_data(self):
        """Return the dict containing the data for each tracked tag"""
        return self.data


    def handle_data(self, data):
        """Handler for text nodes in the parsed HTML tree

        It saves all the data contained within tags being tracked

        """
        if not self.save:
            return
        try:
            self.data[self.current].append(data)
        except KeyError:
            self.data[self.current] = [data]


    def handle_starttag(self, tag, attrs):
        """Handler for a start tag

        Starts to save data if current tag is in list of tags
        to be tracked.

        """
        if tag in self.tags:
            self.current = tag
            self.save = True


    def handle_endtag(self, tag):
        """Handler for an end tag

        Determines when to stop saving the data

        """
        if tag in self.tags:
            self.current = ''
            self.save = False
