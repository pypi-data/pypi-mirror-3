#!/usr/bin/env python
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
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseNotFound
from PIL import Image
import StringIO
#import gtk





def render_svg(size):
    filename = settings.DJUNGLE_FAVICON_FILE
    width, height = size, size
    
    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, width, height)
    favicon = Image.fromstring("RGB",(width,height),pb.get_pixels())
    favicon_buffer = StringIO.StringIO()
    favicon.save(favicon_buffer, format='PNG')
    favicon_data = favicon_buffer.getvalue()
    favicon_buffer.close()
    return favicon_data
    


def icon_of_size(size):
    favicon_path = settings.DJUNGLE_FAVICON_FILE
    favicon = Image.open(favicon_path)
    favicon = favicon.resize((size, size), Image.ANTIALIAS)

    favicon_buffer = StringIO.StringIO()
    favicon.save(favicon_buffer, format='PNG')
    favicon_data = favicon_buffer.getvalue()
    favicon_buffer.close()
    return favicon_data

def favicon_touch(request, size, precomposed):
    size_int = int(size or 114)
    precomposed_string = precomposed if precomposed is not None else ''
    
    if not settings.DJUNGLE_FAVICON_PRECOMPOSED \
            and precomposed is not None \
            and size is not None:
        return HttpResponseNotFound()
    
    if size_int > 512:
        return HttpResponsePermanentRedirect(
                '/apple-touch-icon-%dx%d%s.png' % \
                (512, 512, precomposed_string))
    
    if size_int < 16:
        return HttpResponsePermanentRedirect(
                '/apple-touch-icon-%dx%d%s.png' % \
                (16, 16, precomposed_string))
    
    icon = icon_of_size(size_int) 
    return HttpResponse(icon, content_type='image/png')
    
@cache_page(60 * 15)
def favicon(request):
    icon = icon_of_size(settings.DJUNGLE_FAVICON_SIZE)
    #icon = icon_of_size(settings.DJUNGLE_FAVICON_SIZE) 
    return HttpResponse(icon, content_type='image/png')
    
    
    #precomposed = kwargs.get('precomposed', None) is not None

    #size_str = kwargs.get('size')
    #if size_str is None:
    #    size = 114
    #else:
    #    size = int(size_str)
    #if size > 512:
    #    size = 512
    #if size <= 0:
    #    size = 1

    size = 128
    favicon_path = settings.DJUNGLE_FAVICON_FILE
    favicon = Image.open(favicon_path)
    favicon = favicon.resize((size, size), Image.ANTIALIAS)

    favicon_buffer = StringIO.StringIO()
    favicon.save(favicon_buffer, format='PNG')
    favicon_data = favicon_buffer.getvalue()
    favicon_buffer.close()

    return HttpResponse(favicon_data, content_type='image/png')
