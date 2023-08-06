# Copyright (c) 2012 Thomas Lotze
# See also LICENSE.txt

import datetime
import os
import os.path
import paste.script.command
import pkg_resources
import shutil
import subprocess
import sys
import tempfile
import time
import tl.pkg
import tl.pkg.doc
import unittest2 as unittest


class TemplateSetUp(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def expand_template(self):
        try:
            paste.script.command.run(
                'create -q -t tl-pkg tl.example'.split() + [
                    'description=An example package. ',
                    'keywords=example package',
                    'author=Max Mustermann',
                    'author_email=max@example.org',
                    'bitbucket_name=max',
                    ])
        except SystemExit:
            pass

    def content(self, rel_path):
        file_path = os.path.join(
            self.tmpdir, 'tl.example', *rel_path.split('/'))
        self.assertTrue(os.path.isfile(file_path))
        return open(file_path).read()


class Template(TemplateSetUp):

    def test_expanding_template_creates_files(self):
        self.expand_template()
        self.assertEqual(
            '', self.content('tl/example/tests/__init__.py'))
        self.assertIn(
            str(datetime.date.today().year), self.content('COPYRIGHT.txt'))

    def test_package_has_tl_pkg_version_pinned_to_active(self):
        self.expand_template()
        tl_pkg = pkg_resources.get_distribution('tl.pkg')
        self.assertIn('tl.pkg = %s\n' % tl_pkg.version,
                      self.content('versions/versions.cfg'))

    def test_hg_init_has_been_run(self):
        self.expand_template()
        self.assertTrue(os.path.isdir(os.path.join('tl.example', '.hg')))

    def test_setup_py_is_functional(self):
        # paster detects setup.py and creates egg-info from it
        self.expand_template()
        self.assertIn('Name: tl.example\n',
                      self.content('tl.example.egg-info/PKG-INFO'))

    def test_sphinx_docs_can_be_built(self):
        self.expand_template()
        os.chdir('tl.example')
        tl.pkg.doc.main(['doc'])
        self.assertIn('<html', self.content('build/doc/index.html'))

    def test_project_links_are_fully_expanded_in_sphinx_sidebar(self):
        self.expand_template()
        os.chdir('tl.example')
        tl.pkg.doc.main(['doc'])
        self.assertIn('"https://bitbucket.org/max/tl.example/"',
                      self.content('build/doc/index.html'))
        self.assertIn('"http://pypi.python.org/pypi/tl.example/"',
                      self.content('build/doc/index.html'))

    def test_flattr_button_is_omitted_if_no_flattr_url_is_given(self):
        self.expand_template()
        os.chdir('tl.example')
        tl.pkg.doc.main(['doc'])
        self.assertNotIn('flattr', self.content('build/doc/index.html'))

    def test_flattr_button_is_shown_if_flattr_url_is_given(self):
        self.expand_template()
        os.chdir('tl.example')
        conf_py = open(os.path.join('doc', 'conf.py'), 'w')
        conf_py.write("""\
import tl.pkg.sphinxconf
_flattr_url = 'http://flattr.com/thing/...'
tl.pkg.sphinxconf.set_defaults()
""")
        conf_py.close()
        tl.pkg.doc.main(['doc'])
        self.assertIn('href="http://flattr.com/thing/',
                      self.content('build/doc/index.html'))


class Buildout(TemplateSetUp):

    level = 2

    def setUp(self):
        super(Buildout, self).setUp()
        self.expand_template()
        os.chdir('tl.example')

    @property
    def tl_pkg_dev(self):
        path = tl.pkg.__file__
        for _ in xrange(3):
            path = os.path.dirname(path)
        return path

    def buildout(self):
        subprocess.call([sys.executable, 'bootstrap.py'])
        return subprocess.call([
                os.path.join('bin', 'buildout'),
                '-q',
                'buildout:develop+=%s' % self.tl_pkg_dev])

    def test_bootstrap_succeeds_using_distribute_by_default(self):
        subprocess.call([sys.executable, 'bootstrap.py'])
        bin_buildout = self.content('bin/buildout')
        self.assertIn(sys.executable, bin_buildout)
        self.assertIn('distribute-', bin_buildout)
        self.assertNotIn('setuptools-', bin_buildout)

    def test_buildout_succeeds(self):
        status = self.buildout()
        self.assertEqual(0, status)
        self.assertEqual(
            ['buildout', 'doc', 'py', 'test'], sorted(os.listdir('bin')))

    def test_tests_succeed(self):
        self.buildout()
        bin_test = os.path.join('bin', 'test')
        self.assertTrue(os.path.isfile(bin_test))
        status = subprocess.call([bin_test])
        self.assertEqual(0, status)

    def test_sphinx_docs_can_be_built(self):
        self.buildout()
        bin_doc = os.path.join('bin', 'doc')
        self.assertTrue(os.path.isfile(bin_doc))
        subprocess.call([bin_doc])
        self.assertIn('<html', self.content('build/doc/index.html'))

    def test_sphinx_api_docs_are_updated_with_every_run(self):
        self.buildout()
        bin_doc = os.path.join('bin', 'doc')
        api_txt = open(os.path.join('doc', 'api.txt'), 'w')
        api_txt.write("""\
.. autosummary::
    :toctree: ./

    tl.example.foo
""")
        api_txt.close()
        foo_py = open(os.path.join('tl', 'example', 'foo.py'), 'w')
        foo_py.write('"A module doc string."')
        foo_py.close()
        subprocess.call([bin_doc])
        self.assertIn('A module doc string.',
                      self.content('build/doc/tl.example.foo.html'))
        # Make sure the mtime of both the Python source and the Sphinx input
        # files generated by autosummary is greater at a precision of 1 second
        # during the following run than the Sphinx output produced in the
        # previous run.
        time.sleep(1)
        foo_py = open(os.path.join('tl', 'example', 'foo.py'), 'w')
        foo_py.write('def some_function(): pass')
        foo_py.close()
        subprocess.call([bin_doc])
        self.assertIn('some_function',
                      self.content('build/doc/tl.example.foo.html'))
