=========
Cooker
=========

Cooker provides easy access to various programming sites such as
`CodeChef <http://www.codechef.com>`.

It eases up repetitive tasks like setting up directory for solving
a new problem.

Typical usage::

    cook setup -u http://link.to/problem.html
    cook check

See help for more options

Examples::

    cook setup -q simgraph -c april12 -l java

The last line will create a new directoy named the title of the
`problem <http://www.codechef.com/APRIL12/problems/SIMGRAPH>`,
copy your template, create input and output files containing
sample test cases.
