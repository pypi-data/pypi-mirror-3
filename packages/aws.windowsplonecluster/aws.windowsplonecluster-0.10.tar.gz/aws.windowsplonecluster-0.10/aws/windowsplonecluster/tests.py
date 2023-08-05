# -*- coding: utf-8 -*-
# Copyright (C) 2011 Alterway Solutions 

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import aws.windowsplonecluster
import unittest
import doctest
import time


flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)
    
suite = unittest.TestSuite()
suite.addTest(doctest.DocFileSuite("README.txt",
                                   optionflags=flags))
unittest.TextTestRunner().run(suite)



class TestSequenceFunctions(unittest.TestCase):

    
    
    def test_thread(self):
        
        def sleep( value):
            time.sleep(value)
        aws.windowsplonecluster.queue_tasks(((sleep,  0.01),
                                           (sleep, 0.02)))
        
        
        
    
