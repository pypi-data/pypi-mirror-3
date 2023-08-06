=======
Cooker
=======

Cooker provides easy access to various programming sites such as
`CodeChef <http://www.codechef.com>`_.

It eases up repetitive tasks like setting up directory for solving
a new problem.
Typical usage::

    #!/usr/bin/env python

    from cooker import Cooker

    problem = 'SIMGRAPH'
    contest = 'APRIL12'
    path = '.'

    c = Cooker()
    c.cook(problem, contest, path)
    print "Dinner is served!"


A Sub-Section
-------------

The above code will setup the structure for the following problem :
`CodeChef <http://www.codechef.com/APRIL12/problems/SIMGRAPH>`_.
