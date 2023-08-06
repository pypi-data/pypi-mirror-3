# -*- coding: utf-8 -*-
#
# Djungle Favicons – Favicon auto-generation for Django
# Copyright © 2012  Hendrik M Halkow
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
from django.conf.urls.defaults import patterns, url
from django.conf import settings


def favicon_patterns():
    urlpatterns = patterns('djungle.favicons.views')

    pattern = r'^apple\-touch\-icon(\-(?P<size>\d+)x\2)?' + \
        r'(?P<precomposed>\-precomposed)\.png$'

    urlpatterns += patterns('djungle.favicons.views',
        url(r'^apple\-touch\-icon(\-(?P<size>\d+)x\2)?' + \
                r'(?P<precomposed>\-precomposed)?\.png$',
            'favicon_touch', name='djungle-favicon-touch'),

        url(r'^favicon\.png$', 'favicon', name='djungle-favicon'),
    )

    return urlpatterns
