# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from BeautifulSoup import BeautifulStoneSoup
from optparse import OptionParser
import sys


class XMLSoup(BeautifulStoneSoup):

    def _smartPop(self, name):
        """We don't want to 'clean' the DOM.
        """
        pass


def xmlindent():
    """Indent an XML file.

    Can be used in emacs on your buffer with C-x h C-u M-S | path to
    the script Enter.
    """
    parser = OptionParser()
    (options, files) = parser.parse_args()

    if not files:
        input = ''
        data = sys.stdin.read()
        while data:
            input += data
            data = sys.stdin.read()
        print XMLSoup(input).prettify()
        return

    for filename in files:
        with open(filename, 'r') as input:
            print XMLSoup(input.read()).prettify()
