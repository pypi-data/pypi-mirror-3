# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Handler to queue actions on the 30loops platform."""

import json
import urlparse

from .state import env
from .base import HttpBaseHandler
from .exceptions import HttpReturnError


class ActionHandler(HttpBaseHandler):
    def __init__(self, action, options={}):
        self.action = action
        self.options = options

    def uri(self):
        uri = "%s/%s/%s/%s/%s/" % (
                env.base_uri.strip('/'),
                env.api_version.strip('/'),
                env.account.strip('/'),
                env.label.strip('/'),
                env.resource.strip('/')
                )
        return uri

    def queue(self):
        cmd = {
                'action': self.action,
                'options': self.options
                }

        self.post(data=json.dumps(cmd))

        if self.response.status_code == 202:
            # we succesfully queued the action, so it seems
            location = urlparse.urlsplit(self.response.headers['Location'])
            self.uuid = location.path.strip('/').split('/')[-1]
        else:
            # Every other return code is considered an error
            raise HttpReturnError(self.response.status_code,
                    self.response.content)
