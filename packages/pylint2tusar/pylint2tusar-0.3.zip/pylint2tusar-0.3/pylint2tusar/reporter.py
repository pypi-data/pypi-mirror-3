# Copyright (c) 2012 Thales Global Services SAS
# 
# Author : Robin Jarry
# 
# The MIT license. See LICENSE file for details

import os
import sys
from pylint.reporters.text import ParseableTextReporter
from xml.dom.minidom import Document

#------------------------------------------------------------------------------
TUSAR_NS = 'http://www.thalesgroup.com/tusar/v8'
VIOLATIONS_NS = 'http://www.thalesgroup.com/tusar/violations/v4'
MEASURES_NS = 'http://www.thalesgroup.com/tusar/measures/v6'
SIZE_NS = 'http://www.thalesgroup.com/tusar/size/v1'
DUPLICATIONS_NS = 'http://www.thalesgroup.com/tusar/duplications/v1'

#------------------------------------------------------------------------------
class TUSARReporter(ParseableTextReporter):
    
    linter = None
    
    def __init__(self, output=sys.stdout, relative=True):
        ParseableTextReporter.__init__(self, output, relative)
        
        self.doc = Document()
        
        self.tusar = self.doc.createElementNS(TUSAR_NS, 'tusar:tusar')
        self.violations = self.doc.createElementNS(VIOLATIONS_NS, 'tusar:violations')
        self.measures = self.doc.createElementNS(MEASURES_NS, 'tusar:measures')
        self.size = self.doc.createElementNS(SIZE_NS, 'measures:size')
        self.duplications = self.doc.createElementNS(DUPLICATIONS_NS, 'measures:duplications')
        
        for e in (self.violations, self.measures, self.size, self.duplications):
            e.setAttribute('tool', 'pylint')
        
        self.tusar.setAttributeNS('', 'xmlns:tusar', TUSAR_NS)
        self.tusar.setAttributeNS('', 'xmlns:violations', VIOLATIONS_NS)
        self.tusar.setAttributeNS('', 'xmlns:measures', MEASURES_NS)
        self.tusar.setAttributeNS('', 'xmlns:size', SIZE_NS)
        self.tusar.setAttributeNS('', 'xmlns:duplications', DUPLICATIONS_NS)
        
        self.doc.appendChild(self.tusar)
        self.tusar.appendChild(self.violations)
        self.tusar.appendChild(self.measures)
        self.measures.appendChild(self.duplications)
        self.measures.appendChild(self.size)
        
        self.files = {}
    
    def add_message(self, msg_id, location, msg):
        """manage message of different type and in the context of path"""
        
        try:
            path, _, obj, line, _ = location
        except ValueError:
            # fallback for pylint < 0.25
            path, _, obj, line = location
            
        if self._prefix:
            path = path.replace(self._prefix, '')

        if msg_id == 'R0801': # duplication
            self.handle_duplication(msg)
        else: # violation
            self.handle_violation(msg_id, path, obj, line, msg)

    def handle_duplication(self, msg):
        _, buff = msg.split('\n', 1)
        buff = buff.strip()
        
        duplication = self.doc.createElementNS(DUPLICATIONS_NS, 'duplications:set') 
        self.duplications.appendChild(duplication)
        
        while buff.startswith('=='):
            temp, buff = buff[2:].split('\n', 1)
            module, line = temp.split(':')
            
            modulepath = module.replace('.', os.path.sep)
            
            if os.path.exists(modulepath + '.py'):
                modulepath = modulepath + '.py'
            else:
                modulepath = modulepath + os.path.sep + '__init__.py'
            
            resource = self.doc.createElementNS(DUPLICATIONS_NS, 'duplications:resource')
            resource.setAttribute('path', modulepath)
            resource.setAttribute('line', line)
            
            duplication.appendChild(resource)
        
        codefragment = self.doc.createElementNS(DUPLICATIONS_NS, 'duplications:codefragment')
        codefragment.appendChild(self.doc.createCDATASection(buff))
        
        duplication.appendChild(codefragment)
        duplication.setAttribute('lines', str(buff.count('\n') + 1))
    
    def handle_violation(self, msg_id, path, obj, line, msg):
        if '\n' in msg:
            # we only keep the first line 
            msg, _ = msg.split('\n', 1)
        
        violation = self.doc.createElementNS(VIOLATIONS_NS, 'violations:violation')
        violation.setAttribute('key', msg_id)
        violation.setAttribute('line', str(line))
        violation.setAttribute('message', msg.strip())
        
        try:
            self.files[path].append(violation)
        except KeyError:
            self.files[path] = [ violation ]
        
    EXPORTED_METRICS = (
        ('statements', 'statement'),
        ('lines', 'total_lines'),
        ('ncloc', 'code_lines'),
        ('files', 'module'),
        ('comment_lines', 'comment_lines'),
        ('duplicated_lines', 'nb_duplicated_lines'),
        ('classes', 'class'),
        ('functions', ('method', 'function')),
    )
    def _display(self, layout):
        for path, violations in self.files.items():
            fileelt = self.doc.createElementNS(VIOLATIONS_NS, 'violations:file')
            fileelt.setAttribute('path', path)
            for v in violations:
                fileelt.appendChild(v)
            self.violations.appendChild(fileelt)
        
        project = self.doc.createElementNS(SIZE_NS, 'size:resource')
        project.setAttribute('type', 'PROJECT')
        project.setAttribute('value', '')
        self.size.appendChild(project)
        
        for sonar_attr, pylint_attr in TUSARReporter.EXPORTED_METRICS:
            value = 0
            if type(pylint_attr) == type(()):
                for attr in pylint_attr:
                    value += self.linter.stats[attr]
            else:
                value += self.linter.stats[pylint_attr]
            
            measure = self.doc.createElementNS(SIZE_NS, 'size:measure')
            measure.setAttribute('key', sonar_attr)
            measure.setAttribute('value', str(value))
            
            project.appendChild(measure)
        
        self.doc.writexml(self.out, encoding='utf-8', addindent='  ', newl='\n')
        print >>self.out, '\n'

