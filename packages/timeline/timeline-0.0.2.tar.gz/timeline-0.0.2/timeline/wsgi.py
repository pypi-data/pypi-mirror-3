# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Affero General Public License version 3 (see the file LICENSE).

"""WSGI integration."""

__all__ = ['make_app']

from timeline import Timeline

def make_app(app):
    """Create a WSGI app wrapping app.

    The wrapper app injects an environ variable 'timeline.timeline' which is a
    Timeline object.
    """
    def wrapper(environ, start_response):
        environ['timeline.timeline'] = Timeline()
        return app(environ, start_response)
    return wrapper
