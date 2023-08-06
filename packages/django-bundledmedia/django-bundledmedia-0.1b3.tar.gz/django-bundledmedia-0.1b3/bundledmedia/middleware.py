# Copyright (c) 2012 by Yaco Sistemas
#
# This file is part of django-bundledmedia.
#
# django-bundledmedia is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-bundledmedia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-bundledmedia.  If not, see <http://www.gnu.org/licenses/>.

from bundledmedia.datastructures import MediaDictionary


class BundledMediaMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and initializes the media bundle object in the current
    thread context.
    """

    def process_request(self, request):
        """ Initialize media contents for bundledmedia and addmedia tags """
        request.media_holder = MediaDictionary()

    def process_response(self, request, response):
        """ Uninitialize media contents for bundledmedia and addmedia tags """
        if hasattr(request, 'media_holder'):
            del request.media_holder
        return response
