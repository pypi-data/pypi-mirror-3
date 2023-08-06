# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

import threading

from testtools import TestCase
from timeline import Timeline

from .. import middleware


class Request(object):

    def __init__(self, environ):
        self.environ = environ


class TimelineMiddlewareTests(TestCase):

    def setUp(self):
        super(TimelineMiddlewareTests, self).setUp()
        self.patch(middleware, '_thread_local', threading.local())

    def test_get_timeline_is_None(self):
        self.assertEqual(None, middleware.get_timeline())

    def test_middleware_doesnt_set_timeline_if_not_in_environ(self):
        mw = middleware.TimelineMiddleware()
        request = Request({})
        mw.process_request(request)
        self.assertEqual(None, middleware.get_timeline())

    def test_middleware_sets_timeline(self):
        mw = middleware.TimelineMiddleware()
        timeline = Timeline()
        request = Request({'timeline.timeline': timeline})
        mw.process_request(request)
        self.assertEqual(timeline, middleware.get_timeline())
