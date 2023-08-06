#!/usr/bin/env python

"""
python package templates for makeitso

Several components are included.
[TODO] You may use these subtemplates in any combination.

* README.txt : a README in restructured text
* examples : examples for your package
* setup.py : setup utility for the full package
* ./main.py : CLI handler for your webapp
* ./model.py : model of a persisted object
* ./template.py : a MakeItSo template for project creation
* ./tests : doctest suite for the package
* ./web.py : a webob web handler
"""

import os
import sys
from cli import MakeItSoCLI
from makeitso import ContentTemplate
from optparse import OptionParser
from template import MakeItSoTemplate
from template import Variable

class PythonModuleTemplate(MakeItSoTemplate):
  """single module python package"""
  templates = ['python_module']

class PythonPackageTemplate(MakeItSoTemplate):
  """
  python package template
  """
  name = 'python-package'
  templates = ['python_package']
  vars = [Variable('description'),
          Variable('author', 'author of the package'),
          Variable('email', "author's email"),
          Variable('url'),
          Variable('repo', 'project repository'),
          ]
  look = False

  # things that go in setup.py
  dependencies = {'web.py': ['webob'],
                  'template.py': ['MakeItSo']}
  console_scripts = {'main.py': '{{project}} = {{project}}.main:main',
                     'template.py': '{{project}}-template = {{project}}.template:main'
                     }
  
  def __init__(self, **kw):
    MakeItSoTemplate.__init__(self, **kw)

    # TODO: get the templates you actually care about [maybe from the CLI?]

  def pre(self, variables, output):
    """
    sanitize some variables
    """

    # get project from output directory
    variables['project'] = os.path.basename(output)

    # get package name from project
    # XXX could have looser restrictions with transforms
    assert variables['project'].isalnum(), 'Project name must be just letters, you gave %s' % variables['project']
    variables['package'] = variables['project'].lower()

    # dependencies
    dependencies = set([])
    for template, dependency in self.dependencies.items():
      dependencies.update(dependency)
    dependencies = list(dependencies)
    variables['dependencies'] = dependencies
      
    # console_scripts
    console_scripts = []
    for template, console_script in self.console_scripts.items():
      console_scripts.append(console_script)
    if console_scripts:
      s = 'setup(' # placeholder string
      script_strings = ['[console_scripts]']
      for console_script in console_scripts:
        template = ContentTemplate(console_script)
        output = template.substitute(project=variables['project'])
        script_strings.append(output)
      variables['console_scripts'] = '\n'.join([' ' * len(s) + i
                                                for i in script_strings])
    else:
      variables['console_scripts'] = ''


class PythonPackageCLI(MakeItSoCLI):
  """
  CLI front end for the python package template
  """
  usage = '%prog [options] project'

def main(args=sys.argv[1:]):
  cli = PythonPackageCLI(PythonPackageTemplate)
  cli(*args)

if __name__ == '__main__':
  main()  
