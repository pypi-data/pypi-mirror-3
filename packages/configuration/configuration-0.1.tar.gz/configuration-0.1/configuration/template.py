#!/usr/bin/env python

"""
configuration template for makeitso
"""

import sys
from cli import MakeItSoCLI
from optparse import OptionParser
from template import MakeItSoTemplate

class configurationTemplate(MakeItSoTemplate):
  """
  configuration template
  """
  name = 'configuration'
  templates = ['template']
  look = True

class TemplateCLI(MakeItSoCLI):
  """
  CLI driver for the configuration template
  """

def main(args=sys.argv[:]):
  cli = TemplateCLI()
  cli(*args)
  
if __name__ == '__main__':
  main()  


