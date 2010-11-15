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
from models import *

class ExperimentServer(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)

        env = Environment(loader=FileSystemLoader('.'))
        templ = None
        part = None
        worker = None
        try:
            templ = req.params['templ']
            part = req.params['part']
            worker = req.params['workerid']
        except KeyError as e:
            resp = exc.HTTPBadRequest('Missing parameter: %s' % e)

        template = None
        if templ == 'instr':
            template = env.get_template('instructions.html')
            template = template.render(part=part)
        elif templ == 'expt':
            template = env.get_template('flash_experiment.html')
            #TODO: get 'scriptname' (aka list file name)
            template = template.render(part=part)
        else:
            template = u"Template instantiation error!"

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
