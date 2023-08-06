"""
fs

Interface for filesystem access

"""
import os
from shutil import copyfile
from cooker import settings
from cooker.util import alert

class FileSystem():
    """
    Handle creation of directory / files

    """

    def __init__(self):
        pass

    @classmethod
    def create_file(cls, name, contents):
        """Create a new file with given name and save it with
        given contents.

        """
        with open(name, 'w') as fptr:
            fptr.write(contents.strip() + '\n')

    @classmethod
    def make_structure(cls, name='test', inp='', out='', path='.'):
        """Setup the directory structure at the given path with:
        @param name folder to be created
        @param inp  contents for input file
        @param out  contents for output file
        @param path

        """

        # Create destination directory
        dest_dir = '%s/%s' % (path, name)
        try:
            os.mkdir(dest_dir, 0755)
        except OSError:
            resp = raw_input('Problem directory exists. Overwrite (y/n) ? ')
            if resp == 'n':
                alert('Exiting on user cancel.')

        # Make files
        files = { 'input': inp, 'output': out}

        for k in files:
            dest = '%s/%s.txt' % (dest_dir, k)
            cls.create_file(dest, files.get(k))

        src = '%s/template.%s' % (settings.TEMPLATES,
                                    settings.LANG)
        dest = '%s/main.%s' % (dest_dir, settings.LANG)
        try:
            copyfile(src, dest)
        except IOError:
            # destination not writable
            alert('Unable to write to copy the template file.')
