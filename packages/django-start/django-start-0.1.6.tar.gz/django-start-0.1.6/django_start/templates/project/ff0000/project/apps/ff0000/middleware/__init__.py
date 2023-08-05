# Copyright (c) 2009, Sunlight Foundation
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of Sunlight Foundation, Sunlight Labs
#       nor the names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.utils.decorators import decorator_from_middleware
	
CONTENT_TYPES = ('text/html','application/xhtml+xml','application/xml')
HEADER_VALUE = getattr(settings, 'X_UA_COMPATIBLE', 'IE=edge,chrome=1')

class XUACompatibleMiddleware(object):
    
    def __init__(self, value=None):
        
        self.value = value
        if value is None:
            self.value = HEADER_VALUE
        if not self.value:
            raise MiddlewareNotUsed
        
    def process_response(self, request, response):
        response_ct = response.get('Content-Type','').split(';', 1)[0].lower()
        if response_ct in CONTENT_TYPES:
            if not 'X-UA-Compatible' in response:
                response['X-UA-Compatible'] = self.value
        return response

xuacompatible = decorator_from_middleware(XUACompatibleMiddleware)

# Strip Google Analytics cookies for caching middleware purposes
# From http://djangosnippets.org/snippets/1772/
# Author: nf / nf@wh3rd.net

import re

class StripCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except: pass