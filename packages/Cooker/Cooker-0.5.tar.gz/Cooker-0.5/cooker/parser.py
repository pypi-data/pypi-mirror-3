"""
parser

Generic parsers

"""
import argparse
from HTMLParser import HTMLParser

class DefaultArgParser():
    """
    Command line arguements parser

    """

    def __init__(self):
        pass


    @classmethod
    def create_parser(cls):
        """Create a parser

        """
        parser = argparse.ArgumentParser(
                    prog='cook',
                    description="""Utility for various
                            programming problem sites""")
        parser.add_argument(
                    '--version', action='version',
                    version='%(prog)s 1.0')
        parser.add_argument('path', type=str,
                           help='path where the folder is to be created')
        parser.add_argument('-l', '--language', default='cpp',
                           help='language to use (c, cpp, java)')
        parser.add_argument('-p', '--problem', default='',
                           help='problem code for given site')
        parser.add_argument('-u', '--url', default='',
                           help='direct url for the problem')
        parser.add_argument('-c', '--contest', default='',
                           help='contest id for given site')
        parser.add_argument('-s', '--site', default='',
                           help='problem site (default: CodeChef)')

        return parser


    @classmethod
    def parse(cls):
        """Parse command line arguements and returns the parser
        with entered values

        """
        parser = cls.create_parser()
        return parser.parse_args()


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
