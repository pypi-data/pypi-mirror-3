# Copyright (c) 2008-2012 Thomas Lotze
# See also LICENSE.txt

from paste.script.templates import var
import ConfigParser
import datetime
import os
import os.path
import paste.script.templates
import paste.util.template
import pkg_resources
import shutil
import subprocess


tl_pkg = pkg_resources.get_distribution('tl.pkg')

config = ConfigParser.ConfigParser()
try:
    config.read(os.path.join(os.path.expanduser('~'), '.tl-pkg.cfg'))
    section_name = config.sections()[0]
except Exception:
    config_value = lambda option: None
else:
    config_value = lambda option: (config.get(section_name, option) or
                                   '<%s>' % option.upper())


class TLPkg(paste.script.templates.Template):

    _template_dir = 'tl_pkg_template'

    summary = 'Namespaced Python package with buildout and Sphinx docs.'

    vars = [
        var("description", "One-line description of the package"),
        var("keywords", "Space-separated keywords/tags"),
        var('author', 'Author name', default=config_value('author')),
        var('author_email', 'Author e-mail',
            default=config_value('author-email')),
        var('bitbucket_name', 'Bitbucket user name',
            default=config_value('bitbucket-name')),
        ]

    template_renderer = staticmethod(
        paste.util.template.paste_script_template_renderer)

    def underline_double(self, text):
        return '=' * len(text)

    def pre(self, command, output_dir, vars):
        namespace, package = vars['egg'].split('.')
        vars.update(
            double_brace_left='{{',
            double_brace_right='}}',
            namespace=namespace,
            package=package,
            year=datetime.date.today().year,
            underline_double=self.underline_double,
            tl_pkg_version=tl_pkg.version,
            )

    def post(self, command, output_dir, vars):
        os.rename(os.path.join(output_dir, 'hgignore'),
                  os.path.join(output_dir, '.hgignore'))
        subprocess.call(['hg', 'init', output_dir])
        shutil.move(os.path.join(output_dir, 'hgrc'),
                    os.path.join(output_dir, '.hg'))
