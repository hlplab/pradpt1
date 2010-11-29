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

from models import *

# boilerplate Elixer code to create DB objects
setup_all(create_tables=True)

# create our 8 lists with a starting count of 0
# see groups.txt for why the groups are this way
for i in range(1,9):
    tg = TrialGroup(number=i)

    if i in (1,2,5,6):
        tg.sess1list = 1
        tg.sess3list = 2
    else:
        tg.sess1list = 2
        tg.sess3list = 1

    if i in (1,3,5,7):
        tg.sess2list = u'NPNP'
    else:
        tg.sess2list = u'NPPP'

    if i <= 4:
        tg.now = True
    else:
        tg.now = False

session.commit()
