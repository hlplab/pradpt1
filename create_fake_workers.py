#!/usr/bin/env python

#Author: Andrew Watts
#
#    Copyright 2009-2010 Andrew Watts and the University of Rochester
#    Brain and Cognitive Sciences Department
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License version 2.1 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.
#    If not, see <http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>.

'''
For testing purposes, create 100 fake workers randomly assigned to each of
the 8 lists we created in db_init
'''

from models import *
from random import randint, choice
from pradpt1 import random_lowest_list

setup_all()

for i in range(100):
    tmp = ['A']
    tmp.extend([choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for x in range(13)])
    Worker(workerid = ''.join(tmp), trialgroup = random_lowest_list())
session.commit()
