#! /usr/bin/env python                                                        
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        jCabocha.py
# Purpose:     Run jCabocha from python from u'unicode strings'
#              No Need to configure jCabocha with UTF-8 by ./configure UTF-8...
#              Works as it is with the configuration with EUCJP or ISO-8859-1
# Requirement: Python 2.6.* or above,
#              jCabocha installed with configuration EUCJP
# Files req:   None
# Author:      KATHURIA Pulkit
# License:     N/A
# Date:        November 2011
#-------------------------------------------------------------------------------
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys 
import subprocess
from subprocess import call
import os

"""
JCabocha Module for python where input is a unicode string
No need to configure jCabocha with utf-8

Output Types and Formats:
-------------------------

    1)Unicode <str> to jCabocha xml
        Usages
            >>>st = u'毎日新聞社特別顧問４氏の略歴'    
            >>>jCabocha = JCabocha()
            >>>print jCabocha.xmlstring(st).encode('utf-8')

        FORMATS
        =======
            >>>import xml.etree.cElementTree as etree
            >>>st = u'毎日新聞社特別顧問４氏の略歴'    
            >>>jCabocha = JCabocha()
            
        -) XML FORMAT
           ==========
            >>>xml = jCabocha.xmlstring(st).encode('utf-8')
            >>>tree = etree.fromstring(xml)
            >>>print etree.tostring(tree, 'UTF-8')

        -) LATTICE FORMAT
           ==============
            >>>print jCabocha.lattice(st).encode('utf-8')
            
        -) CORPUS FORMAT
           =============
            >>>print jCabocha.corpus(st).encode('utf-8')
            
"""
class JCabocha:
    def __init__(self):
        pass
    
    def write_sent(self, sent):
        """
        @type(sent) = unicode
        """
        in_sent = open('in_sent','w+')
        in_sent.write(sent.encode('eucjp'))
        in_sent.close()

    def clean(self):
        os.remove('in_sent')
        os.remove('out_sent_xml')

    def call_unix(self, sent, command):
        self.write_sent(sent)
        call(command, shell = True)
        with open('out_sent_xml') as out: out_sent_xml = out.read()
        self.clean()
        return unicode(out_sent_xml,'eucjp')
        
    def xmlstring(self, sent):
        """
        @return type = unicode
        -xml format unicode string is returned 
        """
        command = 'cabocha -f 3 < in_sent > out_sent_xml'
        return self.call_unix(sent, command)
    
    def lattice(self, sent):
        """
        @return type = unicode
        -lattice format is returned
        """
        command = 'cabocha -f 2 < in_sent > out_sent_xml'
        return self.call_unix(sent, command)

    def corpus(self, sent):
        """
        @return type = unicode
        -corpus format is returned
        """
        command = 'cabocha -f 1 < in_sent > out_sent_xml'
        return self.call_unix(sent, command)

def main():
    pass

if __name__ == '__main__':
    input_sentence = u'私は彼を５日前、つまりこの前の金曜日に駅で見かけた'
    cabocha = JCabocha()
    print cabocha.xmlstring(input_sentence).encode('utf-8')
    
    
