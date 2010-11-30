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

from webob import Request, Response, exc
from jinja2 import Environment, FileSystemLoader
from models import Worker, TrialGroup, SessionState
from sqlalchemy.orm.exc import NoResultFound
from elixir import *
from random import choice
from datetime import datetime

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

    def __init__(self, app):
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
            resp = exc.HTTPBadRequest(key_error_msg.format(e, required_keys))

        if amz_dict['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            template = env.get_template('preview.html')
            template = template.render(part = part)
        else:
            required_keys.extend('template')
            try:
                templ = req.params['template']
            except KeyError as e:
                resp = exc.HTTPBadRequest(key_error_msg.format(e, required_keys))

            worker = check_worker_exists(amz_dict['workerId'])
            if worker:
                if part > 1:
                    try:
                        sess = SessionState.query.filter_by(worker=worker).one()
                        sess.number = part
                        sess.timestamp = datetime.now() #TODO: check timestamp on part 3
                        session.commit() # important! w/o this it won't save them
                    except NoResultFound:
                        resp = exc.HTTPBadRequest('Attempting to do part {0} without having done part 1!'.format(part))
            else:
                print "No worker defined"
                if part == 1:
                    worker = Worker(workerid = amz_dict['workerId'], trialgroup = random_lowest_list())
                    SessionState(number = 1, worker = worker)
                    session.commit() # important! w/o this it won't save them
                else:
                    print "This is bad"
                    # If part is anything but 1 and there's no worker defined,
                    # then something is horribly wrong
                    resp = exc.HTTPBadRequest('Attempting to do part {0} without having done part 1!'.format(part))

            if not resp:
                if templ == 'instr':
                    template = env.get_template('instructions.html')
                    template = template.render(part=part, now=worker.trialgroup.now)
                elif templ == 'expt':
                    sesslist = {1 : worker.trialgroup.sess1list,
                                2 : worker.trialgroup.sess2list,
                                3 : worker.trialgroup.sess3list}[part]
                    if part in (1,3):
                        template = env.get_template('flash_experiment.html')
                    else:
                        template = env.get_template('spr_experiment.html')
                    template = template.render(part = part, list = sesslist, amz_dict = amz_dict)

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
