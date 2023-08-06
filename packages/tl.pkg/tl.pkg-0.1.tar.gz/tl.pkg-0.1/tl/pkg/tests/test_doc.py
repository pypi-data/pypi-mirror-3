# Copyright (c) 2012 Thomas Lotze
# See also LICENSE.txt

import gocept.testing.assertion
import os.path
import shutil
import subprocess
import sys
import tempfile
import tl.pkg.doc
import unittest2 as unittest


class DocBuildBase(unittest.TestCase, gocept.testing.assertion.Ellipsis):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmpdir)
        self.mkdir('tl')
        self.mkdir('tl/%s' % self.package_name)
        self.write('setup.py', """\
from setuptools import setup

setup(
    name='tl.%s',
    version='1.0',
    author='Author',
)
""" % self.package_name)
        subprocess.call([sys.executable, 'setup.py', '-q', 'egg_info'])
        self.mkdir('doc')
        self.write('doc/api.txt', """\
dummy
-----
""")
        self.write('doc/index.txt', """\
foo and bar and qux

.. toctree::

    api
""")

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def mkdir(self, path):
        os.mkdir(os.path.join(self.tmpdir, *path.split('/')))

    def write(self, path, contents):
        with open(os.path.join(self.tmpdir, *path.split('/')), 'w') as f:
            f.write(contents)


class DocBuildEndToEnd(DocBuildBase):

    package_name = 'example'

    def test_should_generate_documentation(self):
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf
tl.pkg.sphinxconf.set_defaults()
""")
        tl.pkg.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        self.assertTrue(os.path.isfile(index_html))
        contents = open(index_html).read()
        self.assertEllipsis('...foo and bar and qux...', contents)

    def test_variables_from_confpy_are_available_in_sphinxconf_module(self):
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf

_year_started = 2000
tl.pkg.sphinxconf.set_defaults()
        """)
        tl.pkg.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...Copyright 2000-2...', contents)

    def test_defaults_from_sphinxconf_should_not_override_confpy(self):
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf

release = '2.0beta'
tl.pkg.sphinxconf.set_defaults()
        """)
        tl.pkg.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...tl.example v2.0beta...', contents)

    def test_overridden_source_suffix_gets_applied(self):
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf

source_suffix = '.rst'
tl.pkg.sphinxconf.set_defaults()
        """)
        os.rename(os.path.join('doc', 'api.txt'),
                  os.path.join('doc', 'api.rst'))
        os.rename(os.path.join('doc', 'index.txt'),
                  os.path.join('doc', 'index.rst'))
        tl.pkg.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        self.assertTrue(os.path.isfile(index_html))

    def test_command_line_arguments_are_passed_to_sphinx_build(self):
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf

release = '2.0beta'
tl.pkg.sphinxconf.set_defaults()
        """)
        tl.pkg.doc.main(['doc', '-D', 'release=3.1.4'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...tl.example v3.1.4...', contents)

    def test_setuptools_is_importable_to_create_egg_info_for_docs(self):
        # While tl.pkg's test runner is configured by buildout to use a Python
        # that has distribute installed and can therefore use that to call
        # setup.py egg_info (as done in this test-case class' setUp), we
        # cannot be sure about the doc builder. The latter therefore needs to
        # export the path to setuptools before having egg info created.
        python_path = os.path.join(self.tmpdir, 'python-path')
        setup_py = open('setup.py', 'a')
        setup_py.write(r"""

import os.path
import os
f = open('%s', 'w')
f.write('\n'.join(os.environ['PYTHONPATH'].split(':')))
f.close()
""" % python_path)
        setup_py.close()
        tl.pkg.doc.main(['doc'])
        contents = open(python_path).read()
        self.assertEllipsis('.../distribute-...', contents)


class DocBuildWithUnderscoreInPackageName(DocBuildBase):

    package_name = 'example_pkg'

    def test_package_name_with_underscore_can_be_fixed_in_conf_py(self):
        # XXX This really needs a better solution.
        self.write('doc/conf.py', """\
import tl.pkg.sphinxconf
project = 'tl.%s'
tl.pkg.sphinxconf.set_defaults()
""" % self.package_name)
        tl.pkg.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        self.assertTrue(os.path.isfile(index_html))
        contents = open(index_html).read()
        self.assertEllipsis('...tl.example_pkg...', contents)
        self.assertNotIn('tl.example-pkg', contents)
