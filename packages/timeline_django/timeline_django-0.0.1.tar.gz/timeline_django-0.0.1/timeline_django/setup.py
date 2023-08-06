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

from . import hooks, middleware, timeline_cursor


def setup_for_requests(timeline_factory=None, prefix=None):
    """Setup the hooks for timeline_django for request-based tracing.

    This will install all the Django hooks needed to populate the
    `Timeline` during requests. If you are running in an environment
    that is not request-based (manage.py commands, celery tasks) then
    you will need to set up the cursors and hooks in a different fashion.

    If `timeline_factory` is `None` then `timeline_django.middleware.get_timeline`
    will be used. This assumes that `timeline_django.middleware.TimelineMiddleware`
    is in the middleware for the Django project, and that the `timeline` wsgi setup
    is done so the middleware can work.

    If you aren't using the middleware, or aren't in a wsgi context, then you can
    provide your own timeline factory.
    """
    if timeline_factory is None:
        timeline_factory = middleware.get_timeline
    timeline_cursor.setup_timeline_cursor_hooks(timeline_factory, prefix=prefix)
    receiver = hooks.TimelineReceiver(timeline_factory)
    receiver.connect_to_signals()
