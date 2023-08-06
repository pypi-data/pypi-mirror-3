# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2010 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


""".. todo:: Document module."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import glob
import os
import fnmatch
import subprocess
import webbrowser
import re
import codecs
import sys

#---  Third-party imports
import paver.easy as paver
try:
    from paver import virtual
    from sphinxcontrib import paverutils
except ImportError:
    # Assume we running under minilib.
    pass

#---  Project imports


#---Globals--------------------------------------------------------------------

_SETUP = dict(
  name='m4us',
  version='0.2.1',
  description=('A pythonic coroutine-based concurrent programming framework '
    'inspired by Kamaelia.'),
  author='Krys Lawrence',
  author_email='m4us@krys.ca',
  url='http://pypi.python.org/pypi/m4us',
  download_url='http://pypi.python.org/pypi/m4us',
  zip_safe=True,
  ##namespace_packages=[],
  ##test_loader='',
  test_suite='unittest2.collector',
  install_requires=[
    'zope.interface>=3.6.1,<3.6.99',
    'decorator>=3.3.2,<3.3.99',
    # Test dependencies.  The tests can be run anywhere.
    'unittest2>=0.5.1,<0.5.99',
    'mock>=0.7b4,<0.7.99',
    # Sub-dependencies
  ],
  ##extras_require={},
  ##setup_requires=[],
  ##tests_require=[],
  ##dependency_links=[],
  ##eager_resources=[],
  ##entry_points={},
  ##platform=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
  ],
  long_description=codecs.open('README', 'r', 'utf-8').read(),
)

_OPTIONS = dict(
  sphinx=paver.Bunch(builddir='', sourcedir='source'),
  purge=paver.Bunch(exclude_patterns=['*.wpu']),
  pep8=paver.Bunch(paths=['m4us', 'pavement.py']),
  lint=paver.Bunch(paths=['m4us', 'pavement.py']),
  tests_lint=paver.Bunch(paths=['m4us.core.tests', 'm4us.tests']),
  clones=paver.Bunch(packages=['m4us']),
  flakes=paver.Bunch(
    paths=['m4us', 'pavement.py'],
    other_regexes=[r'[/\\\.]api\.py:', "'init' imported but unused"],
  ),
  virtualenv=paver.Bunch(
    no_site_packages=True,
    paver_command_line='develop',
    use_distribute=True,
    packages_to_install=[
      # Sub-dependencies
      'logilab_common>=0.53,<0.53.99',
      'logilab_astng>=0.21,<0.21.99',
      'docutils>=0.7,<0.7.99',
      'Jinja2>=2.5.5,<2.5.99',
      'Pygments>=1.3.1,<1.3.99',
      # Development dependencies
      'virtualenv>=1.5.1,<1.5.99',
      'ipython>=0.10.1,<0.10.99',
      'Sphinx>=1.0.5,<1.0.99',
      'sphinxcontrib-paverutils>=1.3,<1.3.99',
      # Patched version of repoze.sphinx.autointerface included directly.
      ##'repoze.sphinx.autointerface>=0.4,<0.4.99',
      # Useful developer tools
      'coverage>=3.4,<3.4.99.',
      'pep8>=0.6.1,<0.6.99',
      'pylint>=0.22,<0.22.99',
      'pyflakes>=0.4,<0.4.99',
      'CloneDigger>=1.1.0,<1.1.99',
    ],
  ),
  clean=paver.Bunch(
    dir_paths=[
      'docs/html',
      'docs/coverage',
      'docs/latex',
      'docs/doctrees',
      'docs/text',
      'docs/doctest',
    ],
    file_paths=[
      'docs/*.pdf',
      'paver-minilib.zip',
      'setup.py',
      'output.html',
      'pip-log.txt',
      'docs/clones.html',
    ],
    file_patterns=['*.pyc', '*.pyo', '*.bak', '*~', '*.~*'],
    exclude_patterns=['bin', 'lib', 'lib64', 'includes', 'Scripts', 'Lib'],
  ),
)

_DEFAULT_MODDOC_TEMPLATE = u"""\
.. This file is part of Message For You Sir (m4us).
.. Copyright © 2010 Krys Lawrence
..
.. Message For You Sir is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Affero General Public License as published by
.. the Free Software Foundation, either version 3 of the License, or (at your
.. option) any later version.
..
.. Message For You Sir is distributed in the hope that it will be useful, but
.. WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
.. or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
.. License for more details.
..
.. You should have received a copy of the GNU Affero General Public License
.. along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.

:mod:`{name}`
======{underline}=

.. automodule:: {name}
   :members:
   :show-inheritance:
   :synopsis:

   .. todo:: Add module synopsis.

   Inheritance Diagram
   -------------------

   .. inheritance-diagram:: {name}

   Members
   -------
"""


#---Functions------------------------------------------------------------------

#---  Support functions

def _touch_todo(options, *option_sets):
    """Touch the todo.rst file so that Sphinx will regenerate the todo list."""
    if 'sphinx' not in option_sets:
        option_sets += ('sphinx',)
    options.order(*option_sets)
    ## pylint: disable=W0212
    paths = paverutils._get_paths(options)
    ## pylint: enable=W0212
    todo_file = paths.srcdir / options.get('todo_file', 'todo.rst')
    todo_file.touch()
    options.order()


def _gen_docs(options, *option_sets):
    """Touch the todo file and run sphinx to (re-)generate the docs."""
    _touch_todo(options, *option_sets)
    paverutils.run_sphinx(options, *option_sets)


def _in_setup_py():
    """Return True when running as setup.py and not as "paver <some_task>"."""
    return sys.modules['__main__'].__file__ == 'setup.py'


#---  Tasks

@paver.task
@paver.needs('minilib', 'generate_setup', 'html', 'setuptools.command.sdist')
def sdist():
    """Generate the source distribution."""


@paver.task
def release(options):
    """Generate a release version source distribution."""
    egg_info_options = options.setdefault('egg_info', paver.Bunch())
    egg_info_options['tag-build'] = ''
    egg_info_options['tag-date'] = False
    paver.call_task('setuptools.command.egg_info')


@paver.task
def html(options):
    """Generate HTML documentation."""
    _gen_docs(options, 'html', 'sphinx')


@paver.task
def pdf(options):
    """Generate PDF documentation."""
    options.setdotted('pdf.builder', 'latex')
    _gen_docs(options, 'pdf', 'sphinx')
    options.order('pdf', 'sphinx')
    ## pylint: disable=W0212
    paths = paverutils._get_paths(options)
    ## pylint: enable=W0212
    with paver.pushd(paths.outdir):
        paver.sh('make')
        # There can be multiple .pdf files, but only one .tex file, I think.
        # So the .pdf file who's name matches the .tex, is most likely the
        # correct file.
        first_pdf = glob.glob('*.tex')[0][:-4] + '.pdf'
        pdf_file = paver.path(options.get('pdf_file', first_pdf))
        pdf_path = pdf_file.abspath()
    old_pdf = paths.builddir / pdf_file
    if old_pdf.exists():
        old_pdf.remove()
    pdf_path.move(paths.builddir)
    if options.get('remove_outdir', True):
        paths.outdir.rmtree()
    options.order()


@paver.task
def text(options):
    """Generate text documentation."""
    options.setdotted('text.builder', 'text')
    _gen_docs(options, 'text', 'sphinx')


@paver.task
def docscoverage(options):
    """Generate and show documentation coverage report."""
    options.setdotted('coverage.builder', 'coverage')
    _gen_docs(options, 'coverage', 'sphinx')
    options.order('coverage', 'sphinx')
    ## pylint: disable=W0212
    paths = paverutils._get_paths(options)
    ## pylint: enable=W0212
    report_file = paths.outdir / 'python.txt'
    if options.get('show', True):
        pager = options.get('pager')
        if not pager and 'PAGER' in os.environ:
            pager = os.environ['PAGER']
        if pager:
            paver.sh('%s %s' % (pager, report_file))
        else:
            print(report_file.text())
    options.order()


@paver.task
def testdocs(options):
    """Run Sphinx doctest on the documentation."""
    options.setdotted('testdocs.builder', 'doctest')
    _gen_docs(options, 'testdocs', 'sphinx')


@paver.task
@paver.consume_args
def moddoc(options, args):
    """Generate autodoc stub documents for each given module."""
    order = ['moddoc', 'sphinx']
    if 'moddoc' in options and 'section' in options.moddoc:
        order.insert(1, options.moddoc.section)
    ## pylint: disable=W0142
    options.order(*order)
    ## pylint: enable=W0142
    ## pylint: disable=W0212
    paths = paverutils._get_paths(options)
    ## pylint: enable=W0212
    apidir = paths.srcdir / options.get('apidir', 'api')
    template = options.get('template', _DEFAULT_MODDOC_TEMPLATE)
    underline = options.get('underline', '=')
    extension = options.get('extension', '.rst')
    for module_name in args:
        file_path = apidir / module_name + extension
        output = template.format(name=module_name, underline=underline * len(
          module_name))
        paver.dry('writing %s' % file_path, file_path.write_text, output,
          'utf-8', linesep=None)
    options.order()


@paver.task
def clean(options):
    """Delete all unnecessary files."""
    options.order('clean')
    for dir_pattern in options.get('dir_paths', []):
        for dir_path in glob.glob(dir_pattern):
            paver.path(dir_path).rmtree()
    for file_pattern in options.get('file_paths', []):
        for file_path in glob.glob(file_pattern):
            paver.path(file_path).remove()
    for base_path, dir_names, file_names in os.walk('.'):
        for exclude_pattern in options.get('exclude_patterns', []):
            for dir_name in fnmatch.filter(dir_names, exclude_pattern):
                dir_names.remove(dir_name)
            for file_name in fnmatch.filter(file_names, exclude_pattern):
                file_names.remove(file_name)
        for file_pattern in options.get('file_patterns', []):
            for file_name in fnmatch.filter(file_names, file_pattern):
                file_path = paver.path(base_path) / file_name
                file_path.remove()
    options.order()


@paver.task
def purge(options, dry_run):
    """Delete all files not under version control."""
    options.order('purge')
    command = ['hg purge --all']
    if dry_run:
        command.append('-p')
    for exclude_pattern in options.get('exclude_patterns', []):
        command.append('-X %s' % exclude_pattern)
    subprocess.call(' '.join(command), shell=True)
    options.order()


@paver.task
@paver.cmdopts([
  ('source', 's', 'Show source code for each error'),
  ('pep', 'p', 'Show text of PEP 8 for each error'),
])
def pep8(options):
    """Check python modules for PEP8 compliance."""
    options.order('pep8')
    paths = options.paths
    repeat = options.get('repeat', True)
    ignore = options.get('ignore', [])
    source = options.get('source', False)
    pep = options.get('pep', False)
    options.order()
    cmd = ['pep8']
    if repeat:
        cmd.append('--repeat')
    if ignore:
        cmd.append('--ignore=' + ','.join(ignore))
    if source:
        cmd.append('--show-source')
    if pep:
        cmd.append('--show-pep8')
    cmd += paths
    paver.sh(' '.join(cmd))


@paver.task
@paver.needs('setuptools.command.develop')
def develop():
    """Install package in 'development mode'"""
    for distribute_archive in paver.path('.').files('distribute-*.tar.gz'):
        distribute_archive.remove()


@paver.task
@paver.cmdopts([
  ('branch', 'b', 'Branch coverage instead of line coverage'),
  ('show_html', 's', 'Open the HTML coverage report in a Web browser'),
])
def coverage(options):
    """Run all tests with coverage report."""
    options.order('coverage')
    branch = ('--branch' if options.get('branch', False) else '')
    show_html = options.get('show_html', False)
    index_path = paver.path(options.get('index_path',
      'docs/coverage/index.html'))
    options.order()
    paver.sh('coverage erase')
    paver.sh('coverage run {0} bin/unit2 discover 2>&1'.format(branch),
      ignore_error=True)
    paver.sh('coverage html')
    paver.sh('coverage report -m')
    if show_html:
        url = 'file://' + index_path.abspath()
        paver.dry('open "{0}" in browser'.format(url), webbrowser.open, url)


@paver.task
@paver.needs('html')
def docs(options):
    """Open the m4us HTML documentation in a web browser."""
    options.order('docs')
    index_path = paver.path(options.get('index_path', 'docs/html/index.html'))
    options.order()
    url = 'file://' + index_path.abspath()
    paver.dry('open "{0}" in browser'.format(url), webbrowser.open, url)


@paver.task
def bootstrap(options):
    """Creates a virtualenv bootstrap script."""
    # This task overrides the default in order to support using distribute
    # instead of setuptools.
    options.order('virtualenv')
    dest_dir = options.get('dest_dir', '.')
    overridden_adjust_options = [
      '\n\ndef adjust_options(options, args):',
      "    args[:] = ['{0}']".format(dest_dir),
    ]
    if options.get('no_site_packages', False):
        overridden_adjust_options.append('    options.no_site_packages = True')
    if options.get('unzip_setuptools', False):
        overridden_adjust_options.append('    options.unzip_setuptools = True')
    if options.get('use_distribute', False):
        overridden_adjust_options.append('    options.use_distribute = True')
    ## pylint: disable=W0212
    virtual._create_bootstrap(
      options.get('script_name', 'bootstrap.py'),
      options.get('packages_to_install', []),
      options.get('paver_command_line', None),
      dest_dir=dest_dir,
      more_text='\n'.join(overridden_adjust_options),
    )
    ## pylint: enable=W0212
    options.order()


@paver.task
@paver.cmdopts([
  ('unfiltered', 'u', 'Don not filter the output, same as running pyflakes '
    'directly.'),
])
def flakes(options):
    """Run pyflakes and filter out certain expected results."""
    options.order('flakes')
    paths = options.paths
    ignore_unused_imports_for = options.get('ignore_unused_imports_for',
      ('map', 'zip', 'hex', 'ascii', 'oct', 'filter'))
    other_regexes = options.get('other_regexes', ())
    unfiltered = options.get('unfiltered', False)
    options.order()
    results = paver.sh('pyflakes ' + ' '.join(paths), capture=True,
      ignore_error=True)
    if unfiltered:
        print(results)
        return
    unsued_import_message = "'{0}' imported but unused"
    ignore_strings = [unsued_import_message.format(object_name) for object_name
      in ignore_unused_imports_for]
    filters = [re.compile('|'.join(ignore_strings)).search] + [
      re.compile(regex).search for regex in other_regexes]
    for line in results.splitlines():
        if any(filter_(line) for filter_ in filters):
            continue
        print(line)


@paver.task
@paver.cmdopts([
  ('no_colour', 'c', 'Do not use colours in the output.'),
  ('no_reports', 'r', 'Do not show the reports.'),
  ('filter_disables', 'd', 'Filter out "Locally disabling..." messages'),
  ('filter_empty', 'e', 'Filter out module headers with no messages.'),
])
def lint(options):
    """Run pylint on the code."""
    options.order('lint')
    paths = options.paths
    rcfile = options.get('rcfile', None)
    no_colour = options.get('no_colour', False)
    no_reports = options.get('no_reports', False)
    filter_disables = options.get('filter_disables', False)
    filter_empty = options.get('filter_empty', False)
    options.order()
    command = ['pylint']
    if rcfile is not None:
        command.append('--rcfile=' + rcfile)
    if no_colour:
        command.append('-f text')
    if no_reports:
        command.append('-r n')
    command += paths
    # We capture the results and then print them so that output is in the
    # correct order when tasks are chained and the output is piped.
    # The consequence, however, is that paver.sh can hang if the output is too
    # much.  This is a bug in Paver.
    results = paver.sh(' '.join(command), capture=True, ignore_error=True)
    if filter_disables:
        results = results.splitlines()
        results = [line for line in results if 'Locally disabling' not in line]
        results = '\n'.join(results)
    if filter_empty:
        filtered_results = []
        header_line = None
        for line in results.splitlines():
            if '*' * 13 in line:
                header_line = line
                continue
            if line == '':
                header_line = None
            if header_line:
                filtered_results.append(header_line)
                header_line = None
            filtered_results.append(line)
        results = '\n'.join(filtered_results)
    print(results)


@paver.task
## pylint: disable=E1101
@paver.cmdopts(lint.user_options)
## pylint: enable=E1101
def tests_lint(options):
    """Run pylint on the tests."""
    options.order('tests_lint')
    paths = options.paths
    rcfile = options.get('rcfile', 'tests_pylintrc')
    no_colour = options.get('no_colour', False)
    no_reports = options.get('no_reports', False)
    filter_disables = options.get('filter_disables', False)
    filter_empty = options.get('filter_empty', False)
    options.order()
    options.setdotted('lint.paths', paths)
    options.setdotted('lint.rcfile', rcfile)
    options.setdotted('lint.no_colour', no_colour)
    options.setdotted('lint.no_reports', no_reports)
    options.setdotted('lint.filter_disables', filter_disables)
    options.setdotted('lint.filter_empty', filter_empty)
    ## pylint: disable=E1120
    lint()
    ## pylint: enable=E1120


@paver.task
@paver.cmdopts([
  ('full', 'f', 'Generate a full report.'),
  ('no_colour', 'c', 'Do not use colours in the output.'),
])
def check(options):
    """Run pep8, pyflakes and pylintto find code smell."""
    options.order('check')
    full = options.get('full', False)
    no_colour = options.get('no_colour', False)
    options.order()
    if full:
        options.setdotted('pep8.source', True)
        options.setdotted('pep8.pep', True)
    else:
        options.setdotted('lint.no_reports', True)
        options.setdotted('lint.filter_disables', True)
        options.setdotted('tests_lint.no_reports', True)
        options.setdotted('tests_lint.filter_disables', True)
        options.setdotted('lint.filter_empty', True)
        options.setdotted('tests_lint.filter_empty', True)
    if no_colour:
        options.setdotted('lint.no_colour', True)
        options.setdotted('tests_lint.no_colour', True)
    ## pylint: disable=E1120
    pep8()
    flakes()
    lint()
    tests_lint()
    ## pylint: enable=E1120


@paver.task
@paver.cmdopts([
  ('tests', 't', 'Include the tests.'),
  ('browser', 'b', 'Show results in browser.'),
])
def clones(options):
    """Check for duplicate code by runing CloneDigger."""
    options.order('clones')
    tests = options.get('tests', False)
    browser = options.get('browser', False)
    output_file = options.get('output_file', 'docs/clones.html')
    packages = options.get('packages', [])
    assert packages, 'At least one package or module is required.'
    ignores = options.get('ignores', [])
    test_ignores = options.get('test_ignores', ['test', 'tests'])
    options.order()
    command = ['clonedigger -o']
    command.append(output_file)
    if not tests:
        ignores += test_ignores
    for ignore in ignores:
        command.append('--ignore-dir={0}'.format(ignore))
    command += packages
    paver.dry('run CloneDinner', paver.sh, ' '.join(command))
    if browser:
        paver.dry('open "{0}" in browser'.format(output_file),
          webbrowser.open, output_file)


@paver.task
@paver.cmdopts([
  ('browser', 'b', 'Show results in browser.'),
  ('not-strict', 'n', 'Relax error checking.'),
])
def readme(options):
    """Convert README to HTML using rst2html to test it for PyPI."""
    options.order('readme')
    browser = options.get('browser', False)
    strict = not options.get('not_strict', False)
    input_file = options.get('input_file', 'README')
    output_file = options.get('output_file', 'README.html')
    options.order()
    command = ['rst2html.py']
    if strict:
        command.append('--strict')
    command += [input_file, '>', output_file]
    paver.dry('Generate {0}'.format(output_file), paver.sh, ' '.join(command))
    if browser:
        paver.dry('open "{0}" in browser'.format(output_file),
          webbrowser.open, output_file)


if not _in_setup_py():
    @paver.task
    @paver.consume_args
    def test(args):
        """Replacement for distutils command that works in paver.

        This task is not needed or available when running commands and tasks
        from setup.py.  The default disutils command is used instead.  (e.g.
        "python setup.py test".

        When run from paver (e.g. "paver test"), however, unittest2's test
        collector gets confused.  This task works around that.

        """
        paver.sh(' '.join(['unit2', 'discover'] + args))


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

paver.options.update(_OPTIONS)

try:
    import setuptools
    assert hasattr(setuptools, '_distribute')
    del setuptools
except (ImportError, AssertionError):
    import distribute_setup
    distribute_setup.use_setuptools()


#---Late Imports---------------------------------------------------------------

from paver import setuputils


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

## pylint: disable=W0142
setuputils.setup(
  packages=setuputils.find_packages(),
  package_data=setuputils.find_package_data('m4us', package='m4us'),
  **_SETUP)
## pylint: enable=W0142
