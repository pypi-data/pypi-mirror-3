import urllib
from cooker.parser import HTMLTagsParser

"""
    Handle communication with different sites
"""

class Site():
    def problem_data(self, problem, contest=''):
        """Abstract method for getting problem title and test cases
        """
        pass

    def fetch_data(self, url):
        """Fetch contents of the given url

        @return String
        """
        # Get a file-like object for the url
        f = urllib.urlopen(url)

        # Read from the object, storing the page's contents in 's'.
        s = f.read()
        f.close()

        return s

class CodeChef(Site):

    def problem_data(self, problem, contest=''):
        """Get data from codechef
        """
        # Fetch data
        url = self.create_url(problem, contest)
        response = self.fetch_data(url)

        # Parse response
        parser = HTMLTagsParser(['title', 'pre'])
        parser.feed(response)
        data = parser.get_data()

        # Find title and sample test cases
        title = data['title'][0].split(' |')[0]
        inp, out = self.get_cases(data['pre'])

        return (title, inp, out)

    def get_cases(self, response):
        """Extract the input / output test cases

        Needs testing since CodeChef has no fixed format for cases
        """
        inp = ''
        out = ''
        # Hack for one format
        if len(response) == 2:
            inp = response[0]
            out = response[1]
        return (inp, out)

    def create_url(self, problem, contest=''):
        """Constructs the url for given problem and contest
        """
        if contest:
            contest += '/'

        url = "http://www.codechef.com/%sproblems/%s" % (base, contest.upper(), problem.upper())

        return url

class CodeChefLocal(CodeChef):

    def create_url(self, problem, contest=''):
        """Constructs the url for given problem and contest
        """
        url = "http://localhost/work/sim.html"

        return url
