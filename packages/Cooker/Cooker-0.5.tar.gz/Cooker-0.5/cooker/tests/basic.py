"""
basic

Basic Unit tests for cooker

"""
import cooker

class CodeChefLocal(cooker.sites.CodeChef):
    """Dummy site for testing code

    """

    def create_url(self):
        """override default url for CodeChef"""

        # url = "http://localhost/work/par.html";
        url = "http://localhost/work/sim.html"

        return url
