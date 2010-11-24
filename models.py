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

from elixir import *
from datetime import datetime

metadata.bind = "sqlite:///pradpt1.sqlite"

class Worker(Entity):
    workerid = Field(Unicode(15), unique=True)
    triallist = ManyToOne('TrialList', inverse = 'workers')
    #XXX: should I add 'session'?

    def __repr__(self):
        return '<Worker: "%s"' % (self.workerid)

class TrialList(Entity):
    number = Field(Integer)
    count = Field(Integer) # TODO: delete this in favor of counting length of  list of associated workers
    workers = OneToMany('Worker', inverse = 'triallist')

    def __repr__(self):
        return '<TrialList: "%d">' % (self.number)

class Session(Entity):
    number = Field(Integer)
    timestamp = Field(DateTtime, default=datetime.now)
    worker =  sadf

    def __repr__(self):
        return '<Session: %s, %d>' % (self.worker.workerid, self.number)
