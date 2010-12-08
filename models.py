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
    trialgroup = ManyToOne('TrialGroup', inverse = 'workers')
    sessionstate = OneToOne('SessionState', inverse='worker')

    def __repr__(self):
        return '<Worker: "%s">' % (self.workerid)

class TrialGroup(Entity):
    number = Field(Integer)
    sess1list = Field(Integer)
    sess2list = Field(Enum(u'NPNP', u'NPPP'))
    sess3list = Field(Integer)
    now = Field(Boolean)
    workers = OneToMany('Worker', inverse = 'trialgroup')

    def __repr__(self):
        return '<TrialGroup: "%d">' % (self.number)

    def worker_count(self):
        return len(self.workers)

class SessionState(Entity):
    sess1complete = Field(Boolean, default = False)
    sess2complete = Field(Boolean, default = False)
    sess3complete = Field(Boolean, default = False)
    sess1timestamp = Field(DateTime, default=datetime.min)
    sess2timestamp = Field(DateTime, default=datetime.min)
    sess3timestamp = Field(DateTime, default=datetime.min)
    worker =  ManyToOne('Worker', inverse='sessionstate')

    def __repr__(self):
        return '<SessionState: {0}, {1}, {2}, {3}>'.format(self.worker.workerid, self.sess1complete, self.sess2complete, self.sess3complete)
