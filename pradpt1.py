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
from models import Worker, TrialList
from sqlalchemy.orm.exc import NoResultFound
from elixir import *
from random import choice

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
    all_lists = TrialList.query.all()
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
        required_keys = ['workerId', 'assignmentId', 'hitId']
        key_error_msg = 'Missing parameter: {0}. Required keys: {1}'

        try:
            amz_dict['workerId'] = req.params['workerId']
            amz_dict['assignmentId'] = req.params['assignmentId']
            amz_dict['hitId'] = req.params['hitId']
        except KeyError as e:
            resp = exc.HTTPBadRequest(key_error_msg.format(e, required_keys))

        worker = check_worker_exists(amz_dict['workerId'])
        if worker:
            pass
        # TODO: check to see if we have the worker in the db yet. if so, check
        # if they're previewing part N, but haven't done part N-1
        # at this point we just want to warn. don't assign to any list until
        # they accept the HIT.

        if amz_dict['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            template = env.get_template('preview.html')
            template = template.render()
        else:
            required_keys.extend(('templ', 'part', 'list'))
            try:
                templ = req.params['templ']
                part = req.params['part']
                listid = req.params['list']
            except KeyError as e:
                resp = exc.HTTPBadRequest(key_error_msg.format(e, required_keys))

            # TODO: if worker isn't set, create them and assign to list here
            # if worker is set, retrieve their list and check what part they are
            # on. warn them to finish part N-1 first if they've not done it
            # else, update what part they are on
            if not worker:
                worker = Worker(workerid = amz_dict['workerId'], list = random_lowest_list())

            if templ == 'instr':
                template = env.get_template('instructions.html')
                template = template.render(part=part)
            elif templ == 'expt':
                template = env.get_template('flash_experiment.html')
                template = template.render(part = part, list = listid, amz_dict = amz_dict)

        if template:
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
