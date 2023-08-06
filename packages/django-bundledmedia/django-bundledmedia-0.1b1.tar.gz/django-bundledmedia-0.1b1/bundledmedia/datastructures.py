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


from BeautifulSoup import BeautifulSoup


def is_included(node, media_list):
    if node.name == 'script':
        attrs_to_compare = ('src', 'id', )
    else:  # css
        attrs_to_compare = ('href', 'id', )
    for media in media_list:
        if node.name != media.name:
            continue
        for attr in attrs_to_compare:
            if node.get(attr) != media.get(attr):
                break
            # all attributes are equal
            return True
    return False


class MediaList(list):

    def __init__(self, namespace):
        self._namespace = namespace
        super(MediaList, self).__init__()

    def append(self, obj):
        if obj not in self:
            super(MediaList, self).append(obj)

    def render(self):
        soup = BeautifulSoup('\n'.join(self))
        media_assets = []
        for node in soup.findAll():  # remove duplicated media assets
            if not is_included(node, media_assets):
                media_assets.append(node)
        return '\n'.join([unicode(node) for node in media_assets])


class MediaDictionary(dict):
    """
    A media dictionary which auto fills itself instead of raising key errors.
    """

    def __init__(self):
        super(MediaDictionary, self).__init__()

    def __getitem__(self, item):
        if item not in self:
            self[item] = MediaList(item)
        return super(MediaDictionary, self).__getitem__(item)
