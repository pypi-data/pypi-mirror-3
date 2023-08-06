# coding: utf-8

# Copyright © 2012 Julian Mehnle <julian@mehnle.net>,
# Copyright © 2012 Scott Kitterman <scott@kitterman.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
authres extension module for RFC 6008 DKIM signature identification (header.b).
"""

#MODULE = 'authres'

__author__  = 'Scott Kitterman, Julian Mehnle'
__email__   = 'scott@kitterman.com'
__version__ = '0.399'

import authres.core
from authres.core import make_result_class_properties

class DKIMAuthenticationResult(authres.core.AuthenticationResult):
    "DKIM result clause of an ``Authentication-Results`` header"

    METHOD = 'dkim'

    def __init__(self, version = None,
        result               = None,  result_comment               = None,
        reason               = None,  reason_comment               = None,
        properties = None,
        header_d             = None,  header_d_comment             = None,
        header_i             = None,  header_i_comment             = None,
        header_b             = None,  header_b_comment             = None
    ):
        authres.core.AuthenticationResult.__init__(self, self.METHOD, version,
            result, result_comment, reason, reason_comment, properties)
        if header_d:                     self.header_d                     = header_d
        if header_d_comment:             self.header_d_comment             = header_d_comment
        if header_i:                     self.header_i                     = header_i
        if header_i_comment:             self.header_i_comment             = header_i_comment
        if header_b:                     self.header_b                     = header_b
        if header_b_comment:             self.header_b_comment             = header_b_comment

    header_d,             header_d_comment             = make_result_class_properties('header', 'd')
    header_i,             header_i_comment             = make_result_class_properties('header', 'i')
    header_b,             header_b_comment             = make_result_class_properties('header', 'b')

RESULT_CLASSES = [
    DKIMAuthenticationResult
]

# vim:sw=4 sts=4
