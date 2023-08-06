# Copyright (c) 2012 Thales Global Services SAS
# 
# Author : Aravindan Mahendran
# 
# The MIT license. See LICENSE file for details

from sonar_rules_extractor.rule import Rule
from sonar_rules_extractor.extractor import RuleExtractor, ExtractorArgumentError
import glob
import os
import re


class CppcheckExtractor(RuleExtractor):
    '''
    Extractor for cppcheck 1.43
    '''
    
    severities = {'error':'CRITICAL','style':'MINOR','possibleError':'MAJOR', 'possibleStyle':'INFO'}
    tool = 'cppcheck'

    def extract(self, *args):
        if len(args) == 0:
            raise ExtractorArgumentError('Not enough arguments. A folder\'s name containing the source code of "lib" folder must be given as argument')
        
        if not os.path.isdir(args[0]):
            raise ExtractorArgumentError('The given path is not a folder.')
        
        rules = []
        self.read_directory(rules, args[0])
        
        return rules
        
    
    def add_rule(self, rules, line):
        pattern = re.compile('^\\s*(?:reportErr|reportError)\\(\\s*[\\w-]+?\\s*,\\s*(.+?)\\s*,\\s*\\\"(.+?)\\\"\\s*,\\s*.+?\\s*\\).*$')
        search = pattern.search(line)
        if search != None:
            values = search.groups()
            rule = Rule()
            rule.key = values[1]
            if rule.key != 'uninitVar': #rules present twice
                rule.configKey = values[1]
                rule.category = 'Reliability'
                rule.description = values[1]
                rule.name = values[1]
                splittedSeverity = values[0].split('::')
                rule.priority = 'MAJOR'
                if len(splittedSeverity) >= 2:
                    severity = splittedSeverity[1]
                    if ' ' in severity:
                        cleaned_severity = severity.split()
                        severity = cleaned_severity[0]
                    rule.priority = self.severities[severity.strip()]
                rules.append(rule)
            
    def read_file(self, rules, file_name):
        fd = open(file_name,'r')
        for line in fd.readlines():
            self.add_rule(rules, line)
        fd.close()
        
    def read_directory(self, rules, folder_path):
        for file_name in glob.glob(os.path.join(folder_path,"*.*")):
            self.read_file(rules, file_name)