from HTMLParser import HTMLParser

"""
    Generic HTML Parser which returns the contents
    of the tags specified.
"""

class HTMLTagsParser(HTMLParser):

    def __init__(self, tags):
        """Constructor for HTMLTagsParser

        @param tags A list of tags whose contents are to be saved

        """
        HTMLParser.__init__(self)
        self.tags = tags
        self.save = False
        self.data = {}

    def get_data(self):
        """Return the dict containing the data for each tracked tag
        """
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
