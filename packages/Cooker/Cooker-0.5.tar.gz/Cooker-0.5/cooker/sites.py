"""
sites

Interface for accessing problems from different sites

"""
import urllib
import exceptions
from cooker.parser import HTMLTagsParser

class Site():
    """
    Base class for all sites

    """

    def __init__(self, *args, **kwargs):
        pass

    def get_data(self, *args, **kwargs):
        """Entry point for fetching data from a site

        """
        url = kwargs.get('url', '')

        if not url:
            url = self.create_url(*args, **kwargs)

        html = self.fetch_content(url)

        parser = HTMLTagsParser(kwargs.get('tags', []))
        parser.feed(html)
        parsed_content = parser.get_data()

        title, inp, out = self.get_cases(parsed_content)

        return { 'name': title,
                 'path': kwargs.get('path', '.'),
                 'inp': inp,
                 'out': out }


    @classmethod
    def create_url(cls, *args, **kwargs):
        """Constructs the url for given problem and contest"""
        if args or kwargs:
            raise exceptions.NotImplementedError
        raise exceptions.ValueError


    @classmethod
    def get_cases(cls, parsed_content):
        """Abstract method for getting problem title and test cases

        """
        if parsed_content:
            raise exceptions.NotImplementedError
        raise exceptions.ValueError


    @classmethod
    def fetch_content(cls, url):
        """Fetch contents of the given url

        @return String

        """
        # Get a file-like object for the url
        if not url:
            raise exceptions.ValueError

        resp = urllib.urlopen(url)
        html = resp.read()
        resp.close()

        return html


class CodeChef(Site):
    """
    Handles communication with www.codechef.com

    """

    def get_data(self, *args, **kwargs):
        """Extend the base class method. Set a few defaults
        for the particular site.

        """
        kwargs['tags'] = ['title', 'pre']
        return Site.get_data(self, *args, **kwargs)


    def get_cases(self, parsed_content):
        """Extract the input / output test cases

        Needs testing since CodeChef has no fixed format for cases

        """
        title = parsed_content['title'][0].split(' |')[0]
        title = title.replace(' ', '-').lower()
        pre = parsed_content['pre']
        inp, out = '', ''
        # Hack for one format
        if len(pre) == 2:
            inp = pre[0]
            out = pre[1]
        elif len(pre) == 4:
            inp = pre[1]
            out = pre[3]
        return (title, inp, out)


    def create_url(self, *args, **kwargs):
        """Constructs the url for given problem and contest

        """
        contest = kwargs.get('contest', '').upper()
        problem = kwargs.get('problem', '').upper()
        if contest:
            contest += '/'

        base = "http://www.codechef.com"

        return "%s/%sproblems/%s" % (base, contest, problem)
