# Copyright (c) 2012 Thales Global Services SAS
# 
# Author : Robin Jarry
# 
# The MIT license. See LICENSE file for details


__version__ = '0.3'

from pylint import lint

from pylint2tusar.reporter import TUSARReporter

#------------------------------------------------------------------------------
lint.REPORTER_OPT_MAP['tusar'] = TUSARReporter
for optname, optvalues in lint.PyLinter.options:
    if optname == 'output-format':
        optvalues['choices'] += ('tusar',)

#------------------------------------------------------------------------------
def register(linter):
    linter.cmdline_parser._long_opt['--output-format'].choices += ('tusar',)
