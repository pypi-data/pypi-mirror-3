# Copyright (c) 2012 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import pkg_resources
import pkginfo
import shutil
import subprocess
import sys
import tempfile


def main(argv=sys.argv):
    # We use the autosummary extension to build API docs from source code.
    # However, this extension doesn't update the generated docs if the source
    # files change. Therefore, we'd need to remove the generated stuff between
    # runs. In order to avoid the risk of accidentally deleting too much stuff
    # from the user's working copy, we work on a temporary (partial) copy of
    # the project and throw it away if the sphinx run succeeds.

    cwd = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    tmpdoc = os.path.join(tmpdir, 'doc')
    shutil.copytree('doc', tmpdoc, symlinks=True)

    for name in os.listdir(cwd):
        if name.endswith(('.txt', '.py')):
            shutil.copy2(name, os.path.join(tmpdir, name))

    # We need access to the source code tree in order to include text found
    # there in the documentation.
    dist = pkginfo.Develop(cwd)
    namespace = dist.name.split('.')[0]
    src = os.path.join(cwd, namespace)
    os.symlink(src, os.path.join(tmpdir, namespace))

    # Finally, we need to create egg info for the temporary copy since our
    # config code tries to infer some values from package info. Make sure the
    # subprocess can import setuptools by exporting our module search path.
    os.chdir(tmpdir)
    env = os.environ.copy()
    env['PYTHONPATH'] = pkg_resources.get_distribution('distribute').location
    try:
        subprocess.Popen(
            [sys.executable,
             os.path.join(tmpdir, 'setup.py'),
             '-q',
             'egg_info'],
            env=env,
            ).wait()
    finally:
        os.chdir(cwd)

    sphinx_build = pkg_resources.load_entry_point(
        'Sphinx', 'console_scripts', 'sphinx-build')
    argv = ['sphinx-build'] + argv[1:]
    argv += [
        '-q',
        '-E',
        '-d', os.path.join(cwd, 'build', 'doctrees'),
        tmpdoc,
        os.path.join(cwd, 'build', 'doc'),
        ]

    try:
        sphinx_build(argv)
    except Exception:
        print '\nFailed building docs in %s:\n\n' % tmpdoc
    else:
        shutil.rmtree(tmpdir)
