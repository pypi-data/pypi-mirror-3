#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    run all unittests
    ~~~~~~~~~~~~~~~~~
    

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2009-03-31 15:00:10 +0200 (Di, 31 Mrz 2009) $
    $Rev: 26 $
    $Author: google.groups@jensdiemer.de $

    :copyleft: 2008-2009 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE.txt for more details.
"""

import unittest

from tests.utils.utils import MarkupTest
from tests.test_cross_compare import CrossCompareTests
from tests.test_creole2html import TestCreole2html, TestCreole2htmlMarkup
from tests.test_html2creole import TestHtml2Creole, TestHtml2CreoleMarkup

if __name__ == '__main__':
    unittest.main()
    