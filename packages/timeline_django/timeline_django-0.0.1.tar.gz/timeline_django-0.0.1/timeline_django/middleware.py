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


TIMELINE_VAR = 'timeline'


_thread_local = threading.local()


def get_timeline():
    """Get the timeline associated with the current request, if any.

    If `TimelineMiddleware` saved a `Timeline` object at the start of
    the request calling this function will return it. If there isn't
    a saved timeline then `None` will be returned.
    """
    return getattr(_thread_local, TIMELINE_VAR, None)


class TimelineMiddleware(object):
    """Save a `Timeline` as a thread local.

    This middleware looks in `request.environ` for a `timeline.timeline`
    key, and if it is present it stores it in a thread local variable,
    so that `get_timeline` will return it when later called in that
    thread.
    """

    TIMELINE_ENVIRON_KEY = 'timeline.timeline'

    def process_request(self, request):
        if self.TIMELINE_ENVIRON_KEY in request.environ:
            setattr(_thread_local, TIMELINE_VAR,
                    request.environ[self.TIMELINE_ENVIRON_KEY])
