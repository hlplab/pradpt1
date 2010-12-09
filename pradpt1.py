#!/usr/bin/env python

#Author: Andrew Watts
#
#    Copyright 2009-2010 Andrew Watts and the University of Rochester BCS Department
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
#

from webob import Request, Response
from webob.exc import HTTPForbidden, HTTPBadRequest
from jinja2 import Environment, FileSystemLoader
from models import Worker, TrialGroup, SessionState
from sqlalchemy.orm.exc import NoResultFound
from elixir import *
from random import choice
from datetime import datetime, timedelta

# elixir code to connect to db and connect models to db objects
metadata.bind = "sqlite:///pradpt1.sqlite"
setup_all()

def check_worker_exists(workerid):
    try:
        worker = Worker.query.filter_by(workerid=workerid).one()
        return worker
    except NoResultFound:
        return None

def random_lowest_list():
    all_lists = TrialGroup.query.all()
    # sort the lists from least assigned workers to most
    all_lists.sort(key = lambda x: len(x.workers))

    # if the lists are all the same length return a random one
    if len(all_lists[0].workers) == len(all_lists[-1].workers):
        return choice(all_lists)
    else:
        wk = [len(i.workers) for i in all_lists]
        # find out how many lists are the same length as the smallest
        # and return a random one from that subset
        return choice(all_lists[0:wk.count(wk[0])])

class ExperimentServer(object):

    def __init__(self, app=None): # this way if running standalone, gets app, else doesn't need it
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)

        env = Environment(loader=FileSystemLoader('.'))
        amz_dict = {'workerId' : '', 'assignmentId' : '', 'hitId' : ''}
        templ, part, listid, template, resp = [None for x in range(5)]
        required_keys = ['workerId', 'assignmentId', 'hitId', 'part']
        key_error_msg = 'Missing parameter: {0}. Required keys: {1}'

        try:
            amz_dict['workerId'] = req.params['workerId']
            amz_dict['assignmentId'] = req.params['assignmentId']
            amz_dict['hitId'] = req.params['hitId']
            part = int(req.params['part'])
        except KeyError as e:
            resp = HTTPBadRequest(key_error_msg.format(e, required_keys))
            return resp(environ, start_response)

        if amz_dict['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            template = env.get_template('preview.html')
            template = template.render(part = part)
        else:
            worker = check_worker_exists(amz_dict['workerId'])
            if worker:
                forbidden_msg = '<p style="font-weight: bold; font-size: x-large;">{0}</p>'
                if part in (2,3):
                    try:
                        sess = SessionState.query.filter_by(worker=worker).one()
                        if part == 2:
                            if not sess.sess1complete:
                                resp = HTTPForbidden(forbidden_msg.format('You must do part 1 before part 2!'))
                            else:
                                sess.sess2complete = True
                                sess.sess2timestamp = datetime.now()
                                session.commit() # important! w/o this it won't save them

                        if part == 3:
                            if not sess.sess2complete:
                                resp = HTTPForbidden(body_template=forbidden_msg.format('You must do part 2 before part 3!'))
                            if not worker.trialgroup.now:
                                start_time = sess.sess2timestamp + timedelta(days=2)
                                if datetime.now() < start_time:
                                    resp = HTTPForbidden(forbidden_msg('You must wait at least 2 days before doing part 3!'))
                            if not resp:
                                sess.sess3complete = True
                                sess.sess4timestamp = datetime.now()
                                session.commit() # important! w/o this it won't save them
                    except NoResultFound:
                        resp = HTTPForbidden(forbidden_msg.format('Attempting to do part {0} without having done part 1!'.format(part)))
            else:
                if part == 1:
                    worker = Worker(workerid = amz_dict['workerId'], trialgroup = random_lowest_list())
                    SessionState(sess1complete = True, worker = worker)
                    session.commit() # important! w/o this it won't save them
                else:
                    # If part is anything but 1 and there's no worker defined,
                    # then something is horribly wrong
                    resp = HTTPForbidden(forbidden_msg.format('Attempting to do part {0} without having done part 1!'.format(part)))

            if not resp:
                sesslist = {1 : worker.trialgroup.sess1list,
                            2 : worker.trialgroup.sess2list,
                            3 : worker.trialgroup.sess3list}[part]
                if part in (1,3):
                    template = env.get_template('flash_experiment.html')
                else:
                    template = env.get_template('spr_experiment.html')
                template = template.render(part = part, list = sesslist, now=worker.trialgroup.now, amz_dict = amz_dict)

        if template and not resp:
            resp = Response()
            resp.content_type='application/xhtml+xml'
            resp.unicode_body = template
        return resp(environ, start_response)

if __name__ == '__main__':
    from paste import httpserver
    from paste.urlparser import StaticURLParser

    app = StaticURLParser('/')
    app = ExperimentServer(app)
    httpserver.serve(app, host='127.0.0.1', port=8080)
