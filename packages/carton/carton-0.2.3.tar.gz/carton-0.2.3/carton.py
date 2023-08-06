#!/usr/bin/env python

"""
make a self-extracting virtualenv from directories or URLs of packages

To package up all files in a virtualenvs source directory (e.g.)::

  python path/to/carton.py myproject project/src/*

This will create a self-extracting file, `myproject.py`, that will unfold
a virtualenv with the specified packages setup for development

The sources may be directories, local or HTTP-accessible tarballs, or ordinary
files. The `setup.py`s found in the `src` directory after extraction will be
run (via `python setup.py develop`) in the order they are provided. This makes
it possible to have completely local dependencies (without touching the net)
by correctly specifying the source order.  If a `setup.py` is overwritten from
a later source, it will not be rerun (known limitation).

The extracted virtualenv will be created in the current directory and will have
the same name as provided initially (e.g. `myproject`) unless `--env` is
specified.

Normally, the entire contents of source directories are compressed and
packaged as-is.  When running with the `--package` flag, a source tarball is
produced via `python setup.py sdist` if the directory contains a top-level
`setup.py`.

Since directories are compressed as-is, portable file-based VCS repositories,
such a mercurial and git, may be cartoned this way (though note that newer
repositories may not be backwards-compatible with older clients).
"""

# imports
import optparse
import os
import sys
import subprocess
import tarfile
import tempfile
import urllib2
from StringIO import StringIO

# global variables
usage = "%prog [options] environment_name directory|url [...]"
virtualenv_url = 'http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.6.1.tar.gz'
template = """#!/usr/bin/env python

"create a virtualenv at %(ENV)s"

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from optparse import OptionParser
from StringIO import StringIO

try:
    call = subprocess.check_call
except AttributeError:
    # old python; boo :(
    call = subprocess.call

# virtualenv name
ENV='''%(ENV)s'''

# packed files
VIRTUAL_ENV='''%(VIRTUAL_ENV)s'''.decode('base64').decode('zlib')
PACKAGE_SOURCES=%(PACKAGE_SOURCES)s
CARTON=%(CARTON)s

# post-install scripts
PYTHON_SCRIPTS=%(PYTHON_SCRIPTS)s

# parse options
usage = os.path.basename(sys.argv[0]) + ' [options]'
parser = OptionParser(usage=usage, description=__doc__)
parser.add_option('--env', dest='env', help="environment name [DEFAULT: " + ENV + "]")
options, args = parser.parse_args()
if options.env:
    ENV = options.env

# unpack virtualenv
tempdir = tempfile.mkdtemp()
buffer = StringIO()
buffer.write(VIRTUAL_ENV)
buffer.seek(0)
tf = tarfile.open(mode='r', fileobj=buffer)
tf.extractall(tempdir)

# find the virtualenv
for root, dirs, files in os.walk(tempdir):
    if 'virtualenv.py' in files:
        virtualenv = os.path.join(root, 'virtualenv.py')
        break
else:
    raise Exception("virtualenv.py not found in " + tempdir)

# create the virtualenv
os.environ.pop('PYTHONHOME', None)
call([sys.executable, virtualenv, ENV])

# find the bin/scripts directory
for i in ('bin', 'Scripts'):
    scripts_dir = os.path.abspath(os.path.join(ENV, i))
    if os.path.exists(scripts_dir):
        break
else:
    raise Exception("Scripts directory not found in " + ENV)

# find the virtualenv's python
for i in ('python', 'python.exe'):
    python = os.path.join(scripts_dir, i)
    if os.path.exists(python):
        break
else:
    raise Exception("python not found in " + scripts_dir)

# unpack the sources and setup for development
srcdir = os.path.join(ENV, 'src')
os.mkdir(srcdir)
setup_pys = set()
for source in PACKAGE_SOURCES:
    source = source.decode('base64').decode('zlib')
    buffer = StringIO()
    buffer.write(source)
    buffer.seek(0)
    tf = tarfile.open(mode='r', fileobj=buffer)
    tf.extractall(srcdir)

    # setup sources for development if there are any new setup.py files
    # TODO: ideally this would figure out dependency order for you
    for i in os.listdir(srcdir):
        if i in setup_pys:
            continue
        subdir = os.path.join(srcdir, i)
        if os.path.exists(os.path.join(srcdir, i, 'setup.py')):
            try:
                call([python, 'setup.py', 'develop'], cwd=subdir)
            except:
                call([python, 'setup.py', 'install'], cwd=subdir)
            setup_pys.add(i)

# add virtualenv to the virtualenv (!)
virtualenv_dir = os.path.dirname(virtualenv)
if os.path.exists(os.path.join(virtualenv_dir, 'setup.py')):
    call([python, 'setup.py', 'install'], cwd=virtualenv_dir, stdout=subprocess.PIPE)

# add carton to the virtualenv (!)
if CARTON:
    CARTON = CARTON.decode('base64').decode('zlib')
    carton_filename = os.path.join(scripts_dir, 'carton.py')
    f = file(carton_filename, 'w')
    f.write(CARTON)
    f.close()
    try:
        os.chmod(carton_filename, 0755)
    except:
        # you probably don't have os.chmod
        pass

# cleanup virtualenv tempdir
shutil.rmtree(tempdir)

# run post-install scripts
for script in PYTHON_SCRIPTS:
    if not os.path.isabs(script):
        script = os.path.join(os.path.abspath(ENV), script)
    call([python, script])
"""

def isURL(path):
    return path.startswith('http://') or path.startswith('https://')

try:
    call = subprocess.check_call
except AttributeError:
    # old python; boo :(
    call = subprocess.call

def main(args=sys.argv[1:]):

    # parse CLI arguments
    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        """description formatter for console script entry point"""
        def format_description(self, description):
            if description:
                return description.strip() + '\n'
            else:
                return ''
    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    parser.add_option('-o', dest='outfile',
                      help="specify outfile; otherwise it will come from environment_name")
    parser.add_option('-p', '--package', dest='package',
                      action='store_true', default=False,
                      help="create python packages from sources; do not take entire subdirectory")
    parser.add_option('--python-script', dest='python_scripts', default=[],
                      action='append',
                      help="post-uncartoning python scripts to run in the virtualenv; these should be relative to $VIRTUAL_ENV")
    parser.add_option('--virtualenv', dest='virtualenv',
                      help="use this virtualenv URL or file tarball")
    options, args = parser.parse_args(args)
    if len(args) < 2:
        parser.print_usage()
        parser.exit()
    environment = args[0]
    if environment.endswith('.py'):
        # stop on .py; will add it in later
        environment = environment[:-3]
    sources = args[1:]

    # tar up the sources
    source_array = []
    for source in sources:
        buffer = None

        if isURL(source):
            # remote tarball or resource
            buffer = urllib2.urlopen(source).read()
        else:
            # local directory or tarball
            assert os.path.exists(source), "%s does not exist" % source

            # package up the source if applicable
            if options.package and os.path.exists(os.path.join(source, 'setup.py')):

                # create a .tar.gz package
                call([sys.executable, 'setup.py', 'sdist'], cwd=source, stdout=subprocess.PIPE)
                dist_dir = os.path.join(source, 'dist')
                assert os.path.isdir(dist_dir), "dist directory not created in %s" % source
                tarfiles = [i for i in os.listdir(dist_dir)
                            if i.endswith('.tar.gz')]
                assert tarfiles, "no .tar.gz files found in %s" % dist_dir

                # use the last modified tarball
                def last_modified(filename):
                    return os.path.getmtime(os.path.join(dist_dir, filename))
                tarfiles.sort(key=last_modified)
                source = os.path.join(dist_dir, tarfiles[-1])

            if (not os.path.isdir(source)) and tarfile.is_tarfile(source):
                # check for a tarball
                buffer = file(source).read()
            else:
                # add other sources (files and directories) to the archive
                source_buffer = StringIO()
                source_tar = tarfile.open(mode="w:gz", fileobj=source_buffer)
                source_tar.add(source, arcname=os.path.basename(source.rstrip(os.path.sep)))
                source_tar.close()
                buffer = source_buffer.getvalue()

        # could use git, hg, etc repos. but probably shouldn't
        source_array.append(buffer.encode('zlib').encode('base64'))

    # tar up virtualenv if not available
    if options.virtualenv:
        if isURL(options.virtualenv):
            globals()['VIRTUAL_ENV'] = urllib2.urlopen(options.virtualenv).read()
        else:
            assert os.path.exists(options.virtualenv)
            if os.path.isdir(options.virtualenv):
                raise NotImplementedError("Hypothetically you should be able to use a local directory or tarball, but I haven't done this yet")
            else:
                # assert a tarfile
                assert tarfile.is_tarfile(options.virtualenv), "%s must be a tar file" % options.virtualenv
                globals()['VIRTUAL_ENV'] = file(options.virtualenv).read()
    else:
        globals()['VIRTUAL_ENV'] = urllib2.urlopen(virtualenv_url).read()
        # TODO: used the below hashed value of VIRTUAL_ENV if set
        # (set that with another file)

    # get the contents of this file
    carton = None
    try:
        if __file__:
            filename = __file__.rstrip('c') # avoid pyfiles
            if os.path.exists(filename):
                carton = file(filename).read().encode('zlib').encode('base64')
    except NameError:
        pass

    # interpolate "template" -> output
    # TODO: add the ability to include a post-deployment script
    outfile = options.outfile
    if outfile is None:
        outfile = environment + '.py'
    variables = {'VIRTUAL_ENV': VIRTUAL_ENV.encode('zlib').encode('base64'),
                 'ENV': environment,
                 'CARTON': repr(carton),
                 'PYTHON_SCRIPTS': repr(options.python_scripts),
                 'PACKAGE_SOURCES': repr(source_array)}
    f = file(outfile, 'w')
    f.write(template % variables)
    f.close()
    try:
        os.chmod(outfile, 0755)
    except:
        # you probably don't have os.chmod
        pass

VIRTUAL_ENV = """"""

if __name__ == '__main__':
    main()
