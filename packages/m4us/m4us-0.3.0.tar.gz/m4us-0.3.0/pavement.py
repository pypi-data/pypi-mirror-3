# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2009-2012 Krys Lawrence
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


"""Build and development tools for m4us."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip  ## NOQA
## pylint: enable=W0622, W0611

import glob
import os
import fnmatch
import subprocess
import webbrowser
import platform

#---  Third-party imports
import paver.easy as paver

#---  Project imports


#---Globals--------------------------------------------------------------------

_IS_WIN = platform.system() == 'Windows'
_OPTIONS = dict(
  sphinx=paver.Bunch(builddir='', sourcedir='source'),
  purge=paver.Bunch(exclude_patterns=['etc/*.wpu']),
  lint=paver.Bunch(paths=['m4us', 'pavement.py']),
  tests_lint=paver.Bunch(paths=['m4us.core.tests', 'm4us.tests']),
  flakes=paver.Bunch(paths=['m4us', 'pavement.py']),
  clones=paver.Bunch(packages=['m4us']),
  clean=paver.Bunch(
    dir_paths=[
      'docs/html',
      'docs/coverage',
      'docs/latex',
      'docs/doctrees',
      'docs/doctest',
    ],
    file_paths=[
      'docs/clones.html',
    ],
    file_patterns=['*.pyc', '*.pyo', '*.bak', '*~', '*.~*'],
    exclude_patterns=['bin', 'lib', 'lib64', 'includes', 'Scripts', 'Lib'],
  ),
)
_DEFAULT_MODDOC_TEMPLATE = u"""\
.. This file is part of Message For You Sir (m4us).
.. Copyright © 2009-2012 Krys Lawrence
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

def _show_file(file_path, pager=None):
    """Show a text file in the console.

    Use a pager program if given or set by the PAGER environment variable.

    If pager=False, then no pager used.

    """
    if pager is None and 'PAGER' in os.environ:
        pager = os.environ['PAGER']
    if pager:
        paver.sh('%s %s' % (pager, file_path))
    else:
        print(file_path.text())


#---  Tasks

@paver.task
@paver.needs('html')
@paver.cmdopts([
  ('release', 'r', 'Create a release distribution'),
  ('upload', 'u', 'Upload the release and docs to PyPI.'),
])
def sdist(options):
    """Generate the source distribution."""
    options.order('sdist')
    release = options.get('release', False)
    upload = options.get('upload', False)
    options.order()
    assert release or not upload, ('ERROR: --release required with --upload.  '
      'One should not upload development releases to PyPI.')
    command = ['python setup.py']
    if release:
        command.append('release')
    command.append('sdist')
    if upload:
        command.append('register upload upload_docs')
    paver.sh(' '.join(command))


@paver.task
@paver.cmdopts([
  ('fresh', 'f', 'Rebuild from a fresh environment'),
  ('all', 'a', 'Rebuild all files, but keep exising environment'),
  ('show', 's', 'Show the result in a web browser'),
])
def html(options):
    """Generate HTML documentation."""
    options.order('html')
    fresh = options.get('fresh', False)
    all_ = options.get('all', False)
    show = options.get('show', False)
    build_path = paver.path(options.get('build_path', 'docs'))
    todo_path = paver.path(options.get('todo_path', 'docs/source/todo.rst'))
    options.order()
    todo_path.touch()
    command = ['python setup.py build_sphinx']
    if fresh:
        command.append('-E')
    elif all_:
        command.append('-a')
    paver.sh(' '.join(command))
    if show:
        index_path = build_path / 'html' / 'index.html'
        url = 'file://' + index_path.abspath()
        paver.dry('open "{0}" in browser'.format(url), webbrowser.open, url)


@paver.task
@paver.cmdopts([
  ('show', 's', 'Show the results.'),
  ('pager=', 'p', 'Page the outpur using the given pager'),
  ('no-pager', 'n', 'Do not page the output.'),
])
def docscoverage(options):
    """Generate and show documentation coverage report."""
    options.order('docscoverage')
    build_dir = paver.path(options.get('build_dir', 'docs'))
    show = options.get('show', False)
    no_pager = options.get('no_pager', False)
    pager = (options.get('pager', None) if not no_pager else False)
    options.order()
    paver.sh('python setup.py build_sphinx -b coverage')
    if not show:
        return
    report_file = build_dir / 'coverage' / 'python.txt'
    _show_file(report_file, pager)


@paver.task
@paver.cmdopts([
  ('show', 's', 'Show the results.'),
  ('pager=', 'p', 'Page the outpur using the given pager'),
  ('no-pager', 'n', 'Do not page the output.'),
])
def testdocs(options):
    """Run Sphinx doctest on the documentation."""
    options.order('testdocs')
    build_dir = paver.path(options.get('build_dir', 'docs'))
    show = options.get('show', False)
    no_pager = options.get('no_pager', False)
    pager = (options.get('pager', None) if not no_pager else False)
    options.order()
    paver.sh('python setup.py build_sphinx -b doctest', capture=True)
    if not show:
        return
    report_file = build_dir / 'doctest' / 'output.txt'
    _show_file(report_file, pager)


@paver.task
@paver.consume_args
def moddoc(options, args):
    """Generate autodoc stub documents for each given module."""
    options.order('moddoc')
    api_path = paver.path(options.get('api_path', 'docs/source/api'))
    template = options.get('template', _DEFAULT_MODDOC_TEMPLATE)
    underline = options.get('underline', '=')
    extension = options.get('extension', '.rst')
    options.order()
    for module_name in args:
        file_path = api_path / module_name + extension
        output = template.format(name=module_name, underline=underline * len(
          module_name))
        paver.dry('writing %s' % file_path, file_path.write_text, output,
          'utf-8', linesep=None)


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
def develop():
    """Install package in 'development mode'"""
    bin_dir = ('bin/' if not _IS_WIN else 'Scripts\\')
    paver.dry('Installing development package', paver.sh,
      '{0}python setup.py develop'.format(bin_dir))
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
    rcfile = '--rcfile=' + options.get('rcfile', 'etc/coveragerc')
    options.order()
    bin_dir = ('Scripts\\' if _IS_WIN else 'bin/')
    paver.sh('coverage erase ' + rcfile)
    paver.sh('coverage run {0} {1} {2}unit2 discover 2>&1'.format(rcfile,
      branch, bin_dir), ignore_error=True)
    paver.sh('coverage html ' + rcfile)
    paver.sh('coverage report -m ' + rcfile)
    if show_html:
        url = 'file://' + index_path.abspath()
        paver.dry('open "{0}" in browser'.format(url), webbrowser.open, url)


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
    rcfile = options.get('rcfile', 'etc/pylintrc')
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
    rcfile = options.get('rcfile', 'etc/tests_pylintrc')
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
  ('max-complexity=', 'c', 'McCabe complexity treshold.'),
  ('no-repeat', 'r', 'Do not show all occurrences of the same error.'),
  ('exclude=', 'e', 'Exclude files or directories which match these comma '
    'separated patterns .(default: .svn,CVS,.bzr,.hg,.git)'),
  ('filename=', 'f', 'When parsing directories, only check filenames matching '
    'these comma separated patterns. (default: *.py)'),
  ('ignore=', 'i', 'Skip errors and warnings. (e.g. E4,W)'),
  ('show-source', 's', 'Show source code for each error.'),
  ('show-pep8', 'p', 'Show text of PEP 8 for each error.'),
])
def flakes(options):
    """Run flake8 on all code."""
    options.order('flakes')
    max_complexity = options.get('max_complexity', '10')
    no_repeat = options.get('no_repeat', False)
    exclude = options.get('exclude', [])
    filename = options.get('filename', [])
    ignore = options.get('ignore', [])
    show_source = options.get('show_source', False)
    show_pep8 = options.get('show_pep8', False)
    paths = options.paths
    options.order()
    command = ['python Scripts\\flake8' if _IS_WIN else 'flake8']
    if max_complexity:
        command.append('--max-complexity=' + max_complexity)
    if no_repeat:
        command.append('-r')
    for name, values in [('exclude', exclude), ('filename', filename),
      ('ignore', ignore)]:
        if values:
            if isinstance(values, basestring):
                values = values.strip().split(',')
            command.append('--{0}={1}'.format(name, ','.join(values)))
    if show_source:
        command.append('--show-source')
    if show_pep8:
        command.append('--show-pep8')
    command += paths
    paver.dry('Running flake8', paver.sh, ' '.join(command), ignore_error=True)


@paver.task
@paver.cmdopts([
  ('full', 'f', 'Generate a full report.'),
  ('no_colour', 'c', 'Do not use colours in the output.'),
])
def check(options):
    """Run flake and lint and tests_lint to find code smell."""
    options.order('check')
    full = options.get('full', False)
    no_colour = options.get('no_colour', False)
    options.order()
    if full:
        options.setdotted('flake.show_source', True)
        options.setdotted('flake.show_pep8', True)
    else:
        paver.environment.quiet = True
        options.setdotted('lint.no_reports', True)
        options.setdotted('lint.filter_disables', True)
        options.setdotted('lint.filter_empty', True)
        options.setdotted('tests_lint.no_reports', True)
        options.setdotted('tests_lint.filter_disables', True)
        options.setdotted('tests_lint.filter_empty', True)
    if no_colour:
        options.setdotted('lint.no_colour', True)
        options.setdotted('tests_lint.no_colour', True)
    paver.call_task('flakes')
    lint_task = paver.environment.get_task('lint')
    lint_task()
    lint_task.called = False
    paver.call_task('tests_lint')


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
    output_file = paver.path(options.get('output_file', 'docs/clones.html'))
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
        url = 'file://' + output_file.abspath()
        paver.dry('open "{0}" in browser'.format(output_file),
          webbrowser.open, url)


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
    command = ['python Scripts\\rst2html.py' if _IS_WIN else 'rst2html.py']
    if strict:
        command.append('--strict')
    command += [input_file, '>', output_file]
    paver.dry('Generate {0}'.format(output_file), paver.sh, ' '.join(command))
    if browser:
        paver.dry('open "{0}" in browser'.format(output_file),
          webbrowser.open, output_file)


@paver.task
@paver.consume_args
def test(args):
    """Run all tests"""
    paver.sh(' '.join(['unit2', 'discover'] + args))


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

paver.options.update(_OPTIONS)


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
