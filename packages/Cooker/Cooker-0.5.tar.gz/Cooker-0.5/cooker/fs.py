"""
fs

Interface for filesystem access

"""
import os
from shutil import copyfile
from cooker import settings

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
        fptr = open(name, 'w')
        fptr.write(contents)
        fptr.close()

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
        os.mkdir(dest_dir, 0755)

        # Make files
        files = { 'input': inp, 'output': out, 'test': '' }

        for k in files:
            dest = '%s/%s.txt' % (dest_dir, k)
            cls.create_file(dest, files.get(k))

        src = '%s/template.%s' % (settings.TEMPLATES_DIR,
                                    settings.LANG)
        dest = '%s/main.%s' % (dest_dir, settings.LANG)
        copyfile(src, dest)
