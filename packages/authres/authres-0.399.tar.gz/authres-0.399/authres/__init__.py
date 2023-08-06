# coding: utf-8

# Copyright © 2011-2012 Julian Mehnle <julian@mehnle.net>,
# Copyright © 2011-2012 Scott Kitterman <scott@kitterman.com>
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
Package for parsing ``Authentication-Results`` headers as defined in RFC 5451.
Optional support for authentication methods defined in RFCs 5617, 6008, and 6212.

Examples:
RFC 5451 B.2
>>> str(AuthenticationResultsHeader('test.example.org'))
'Authentication-Results: test.example.org; none'

>>> str(AuthenticationResultsHeader('test.example.org', version=1))
'Authentication-Results: test.example.org 1; none'

None RFC example of no authentication with comment:
>>> str(AuthenticationResultsHeader(authserv_id = 'test.example.org',
... results = [NoneAuthenticationResult(comment = 'SPF not checked for localhost')]))
'Authentication-Results: test.example.org; none (SPF not checked for localhost)'

RFC 5451 B.3
>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [SPFAuthenticationResult(result = 'pass',
... smtp_mailfrom = 'example.net')]))
'Authentication-Results: example.com; spf=pass smtp.mailfrom=example.net'

>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; spf=pass smtp.mailfrom=example.net')
>>> str(arobj.authserv_id)
'example.com'
>>> str(arobj.results[0])
'spf=pass smtp.mailfrom=example.net'
>>> str(arobj.results[0].method)
'spf'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].smtp_mailfrom)
'example.net'
>>> str(arobj.results[0].smtp_helo)
'None'
>>> str(arobj.results[0].reason)
'None'
>>> str(arobj.results[0].properties[0].type)
'smtp'
>>> str(arobj.results[0].properties[0].name)
'mailfrom'
>>> str(arobj.results[0].properties[0].value)
'example.net'

RFC 5451 B.4(1)
>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [SMTPAUTHAuthenticationResult(result = 'pass', result_comment = 'cram-md5',
... smtp_auth = 'sender@example.net'), SPFAuthenticationResult(result = 'pass',
... smtp_mailfrom = 'example.net')]))
'Authentication-Results: example.com; auth=pass (cram-md5) smtp.auth=sender@example.net; spf=pass smtp.mailfrom=example.net'

# Missing parsing header comment.
#FIXME
>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; auth=pass (cram-md5) smtp.auth=sender@example.net; spf=pass smtp.mailfrom=example.net')
>>> str(arobj.authserv_id)
'example.com'
>>> str(arobj.results[0])
'auth=pass smtp.auth=sender@example.net'
>>> str(arobj.results[0].method)
'auth'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].smtp_auth)
'sender@example.net'
>>> str(arobj.results[0].properties[0].type)
'smtp'
>>> str(arobj.results[0].properties[0].name)
'auth'
>>> str(arobj.results[0].properties[0].value)
'sender@example.net'
>>> str(arobj.results[1])
'spf=pass smtp.mailfrom=example.net'
>>> str(arobj.results[1].method)
'spf'
>>> str(arobj.results[1].result)
'pass'
>>> str(arobj.results[1].smtp_mailfrom)
'example.net'
>>> str(arobj.results[1].properties[0].type)
'smtp'
>>> str(arobj.results[1].properties[0].name)
'mailfrom'
>>> str(arobj.results[1].properties[0].value)
'example.net'

RFC 5451 B.4(2)
>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [SenderIDAuthenticationResult(result = 'pass',
... header_from = 'example.com')]))
'Authentication-Results: example.com; sender-id=pass header.from=example.com'

>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; sender-id=pass header.from=example.com')
>>> str(arobj.authserv_id)
'example.com'
>>> str(arobj.results[0])
'sender-id=pass header.from=example.com'
>>> str(arobj.results[0].method)
'sender-id'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].header_from)
'example.com'
>>> try:
...     str(arobj.results[0].smtp_mailfrom)
... except AttributeError as x:
...     print(x)
'SenderIDAuthenticationResult' object has no attribute 'smtp_mailfrom'
>>> str(arobj.results[0].properties[0].type)
'header'
>>> str(arobj.results[0].properties[0].name)
'from'
>>> str(arobj.results[0].properties[0].value)
'example.com'

RFC 5451 B.5(1) # Note: RFC 5451 uses 'hardfail' instead of 'fail' for
SPF failures. This erratum is in the process of being corrected.
Examples here use the correct 'fail'. The authres module does not
validate result codes, so either will be processed.

>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [SenderIDAuthenticationResult(result = 'fail',
... header_from = 'example.com'), DKIMAuthenticationResult(result = 'pass',
... header_i = 'sender@example.com', result_comment = 'good signature')]))
'Authentication-Results: example.com; sender-id=fail header.from=example.com; dkim=pass (good signature) header.i=sender@example.com'

# Missing parsing header comment.
#FIXME
>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; sender-id=fail header.from=example.com; dkim=pass (good signature) header.i=sender@example.com')
>>> str(arobj.authserv_id)
'example.com'
>>> str(arobj.results[0])
'sender-id=fail header.from=example.com'
>>> str(arobj.results[0].method)
'sender-id'
>>> str(arobj.results[0].result)
'fail'
>>> str(arobj.results[0].header_from)
'example.com'
>>> str(arobj.results[0].properties[0].type)
'header'
>>> str(arobj.results[0].properties[0].name)
'from'
>>> str(arobj.results[0].properties[0].value)
'example.com'
>>> str(arobj.results[1])
'dkim=pass header.i=sender@example.com'
>>> str(arobj.results[1].method)
'dkim'
>>> str(arobj.results[1].result)
'pass'
>>> str(arobj.results[1].header_i)
'sender@example.com'
>>> str(arobj.results[1].properties[0].type)
'header'
>>> str(arobj.results[1].properties[0].name)
'i'
>>> str(arobj.results[1].properties[0].value)
'sender@example.com'

RFC 5451 B.5(2)
>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [SMTPAUTHAuthenticationResult(result = 'pass', result_comment = 'cram-md5',
... smtp_auth = 'sender@example.com'), SPFAuthenticationResult(result = 'fail',
... smtp_mailfrom = 'example.com')]))
'Authentication-Results: example.com; auth=pass (cram-md5) smtp.auth=sender@example.com; spf=fail smtp.mailfrom=example.com'

# Missing parsing header comment.
#FIXME
>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; auth=pass (cram-md5) smtp.auth=sender@example.com; spf=fail smtp.mailfrom=example.com')
>>> str(arobj.results[0])
'auth=pass smtp.auth=sender@example.com'
>>> str(arobj.results[0].method)
'auth'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].smtp_auth)
'sender@example.com'
>>> str(arobj.results[0].properties[0].type)
'smtp'
>>> str(arobj.results[0].properties[0].name)
'auth'
>>> str(arobj.results[0].properties[0].value)
'sender@example.com'
>>> str(arobj.results[1])
'spf=fail smtp.mailfrom=example.com'
>>> str(arobj.results[1].method)
'spf'
>>> str(arobj.results[1].result)
'fail'
>>> str(arobj.results[1].smtp_mailfrom)
'example.com'
>>> str(arobj.results[1].properties[0].type)
'smtp'
>>> str(arobj.results[1].properties[0].name)
'mailfrom'
>>> str(arobj.results[1].properties[0].value)
'example.com'

RFC 5451 B.6(1)
>>> str(AuthenticationResultsHeader(authserv_id = 'example.com',
... results = [DKIMAuthenticationResult(result = 'pass', result_comment = 'good signature',
... header_i = '@mail-router.example.net'), DKIMAuthenticationResult(result = 'fail',
... header_i = '@newyork.example.com', result_comment = 'bad signature')]))
'Authentication-Results: example.com; dkim=pass (good signature) header.i=@mail-router.example.net; dkim=fail (bad signature) header.i=@newyork.example.com'

# Missing parsing header comment.
#FIXME
>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.com; dkim=pass (good signature) header.i=@mail-router.example.net; dkim=fail (bad signature) header.i=@newyork.example.com')
>>> str(arobj.results[0])
'dkim=pass header.i=@mail-router.example.net'
>>> str(arobj.results[0].method)
'dkim'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].header_i)
'@mail-router.example.net'
>>> str(arobj.results[0].properties[0].type)
'header'
>>> str(arobj.results[0].properties[0].name)
'i'
>>> str(arobj.results[0].properties[0].value)
'@mail-router.example.net'
>>> str(arobj.results[1])
'dkim=fail header.i=@newyork.example.com'
>>> str(arobj.results[1].method)
'dkim'
>>> str(arobj.results[1].result)
'fail'
>>> str(arobj.results[1].header_i)
'@newyork.example.com'
>>> str(arobj.results[1].properties[0].type)
'header'
>>> str(arobj.results[1].properties[0].name)
'i'
>>> str(arobj.results[1].properties[0].value)
'@newyork.example.com'

RFC 5451 B.6(2)
>>> str(AuthenticationResultsHeader(authserv_id = 'example.net',
... results = [DKIMAuthenticationResult(result = 'pass', result_comment = 'good signature',
... header_i = '@newyork.example.com')]))
'Authentication-Results: example.net; dkim=pass (good signature) header.i=@newyork.example.com'

# Missing parsing header comment.
#FIXME
>>> arobj = AuthenticationResultsHeader.parse('Authentication-Results: example.net; dkim=pass (good signature) header.i=@newyork.example.com')
>>> str(arobj.results[0])
'dkim=pass header.i=@newyork.example.com'
>>> str(arobj.results[0].method)
'dkim'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].header_i)
'@newyork.example.com'
>>> str(arobj.results[0].properties[0].type)
'header'
>>> str(arobj.results[0].properties[0].name)
'i'
>>> str(arobj.results[0].properties[0].value)
'@newyork.example.com'

RFC 6008 A.1
>>> import authres.dkim_b
>>> authres_context = FeatureContext(authres.dkim_b)
>>> str(authres_context.header(authserv_id = 'mail-router.example.net',
... results = [authres.dkim_b.DKIMAuthenticationResult(result = 'pass', result_comment = 'good signature',
... header_d = 'newyork.example.com', header_b = 'oINEO8hg'), authres.dkim_b.DKIMAuthenticationResult(result = 'fail',
... header_d = 'newyork.example.com', result_comment = 'bad signature', header_b = 'EToRSuvU')]))
'Authentication-Results: mail-router.example.net; dkim=pass (good signature) header.d=newyork.example.com header.b=oINEO8hg; dkim=fail (bad signature) header.d=newyork.example.com header.b=EToRSuvU'

# Missing parsing header comment.
#FIXME
>>> arobj = authres_context.parse('Authentication-Results: mail-router.example.net; dkim=pass (good signature) header.d=newyork.example.com header.b=oINEO8hg; dkim=fail (bad signature) header.d=newyork.example.com header.b=EToRSuvU')
>>> str(arobj.results[0])
'dkim=pass header.d=newyork.example.com header.b=oINEO8hg'
>>> str(arobj.results[0].method)
'dkim'
>>> str(arobj.results[0].result)
'pass'
>>> str(arobj.results[0].header_d)
'newyork.example.com'
>>> str(arobj.results[0].properties[0].type)
'header'
>>> str(arobj.results[0].properties[0].name)
'd'
>>> str(arobj.results[0].properties[0].value)
'newyork.example.com'
>>> str(arobj.results[0].header_b)
'oINEO8hg'
>>> str(arobj.results[0].properties[1].type)
'header'
>>> str(arobj.results[0].properties[1].name)
'b'
>>> str(arobj.results[0].properties[1].value)
'oINEO8hg'
>>> str(arobj.results[1].method)
'dkim'
>>> str(arobj.results[1].result)
'fail'
>>> str(arobj.results[1].header_d)
'newyork.example.com'
>>> str(arobj.results[1].properties[0].type)
'header'
>>> str(arobj.results[1].properties[0].name)
'd'
>>> str(arobj.results[1].properties[0].value)
'newyork.example.com'
>>> str(arobj.results[1].header_b)
'EToRSuvU'
>>> str(arobj.results[1].properties[1].type)
'header'
>>> str(arobj.results[1].properties[1].name)
'b'
>>> str(arobj.results[1].properties[1].value)
'EToRSuvU'

# RFC 5617 (based on RFC text, no examples provided)
>>> import authres.dkim_adsp
>>> authres_context = FeatureContext(authres.dkim_adsp)
>>> str(authres_context.header(authserv_id = 'example.com',
... results = [DKIMAuthenticationResult(result = 'fail', result_comment = 'bad signature',
... header_d = 'bank.example.net'), authres.dkim_adsp.DKIMADSPAuthenticationResult(result = 'discard',
... header_from = 'phish@bank.example.com', result_comment = 'From domain and d= domain match')]))
'Authentication-Results: example.com; dkim=fail (bad signature) header.d=bank.example.net; dkim-adsp=discard (From domain and d= domain match) header.from=phish@bank.example.com'

# Missing parsing header comment.
#FIXME
>>> arobj = authres_context.parse('Authentication-Results: example.com; dkim=fail (bad signature) header.d=bank.example.net; dkim-adsp=discard (From domain and d= domain match) header.from=phish@bank.example.com')
>>> str(arobj.results[1])
'dkim-adsp=discard header.from=phish@bank.example.com'
>>> str(arobj.results[1].method)
'dkim-adsp'
>>> str(arobj.results[1].result)
'discard'
>>> str(arobj.results[1].header_from)
'phish@bank.example.com'
>>> str(arobj.results[1].properties[0].type)
'header'
>>> str(arobj.results[1].properties[0].name)
'from'
>>> str(arobj.results[1].properties[0].value)
'phish@bank.example.com'

RFC 6212 A.1
>>> import authres.dkim_b, authres.vbr
>>> authres_context = FeatureContext(authres.dkim_b, authres.vbr)
>>> str(authres_context.header(authserv_id = 'mail-router.example.net',
... results = [authres.dkim_b.DKIMAuthenticationResult(result = 'pass', result_comment = 'good signature',
... header_d = 'newyork.example.com', header_b = 'oINEO8hg'), authres.vbr.VBRAuthenticationResult(result = 'pass',
... header_md = 'newyork.example.com', result_comment = 'voucher.example.net',
... header_mv = 'voucher.example.org')]))
'Authentication-Results: mail-router.example.net; dkim=pass (good signature) header.d=newyork.example.com header.b=oINEO8hg; vbr=pass (voucher.example.net) header.md=newyork.example.com header.mv=voucher.example.org'

# Missing parsing header comment.
#FIXME
>>> arobj = authres_context.parse('Authentication-Results: mail-router.example.net; dkim=pass (good signature) header.d=newyork.example.com header.b=oINEO8hg; vbr=pass (voucher.example.net) header.md=newyork.example.com header.mv=voucher.example.org')
>>> str(arobj.results[1])
'vbr=pass header.md=newyork.example.com header.mv=voucher.example.org'
>>> str(arobj.results[1].method)
'vbr'
>>> str(arobj.results[1].result)
'pass'
>>> str(arobj.results[1].header_md)
'newyork.example.com'
>>> str(arobj.results[1].properties[0].type)
'header'
>>> str(arobj.results[1].properties[0].name)
'md'
>>> str(arobj.results[1].properties[0].value)
'newyork.example.com'
>>> str(arobj.results[1].header_mv)
'voucher.example.org'
>>> str(arobj.results[1].properties[1].type)
'header'
>>> str(arobj.results[1].properties[1].name)
'mv'
>>> str(arobj.results[1].properties[1].value)
'voucher.example.org'
"""

MODULE = 'authres'

__author__  = 'Julian Mehnle, Scott Kitterman'
__email__   = 'julian@mehnle.net'
__version__ = '0.399'

import authres.core

# Backward compatibility: For the benefit of user modules referring to authres.…:
from authres.core import *

# FeatureContext class & convenience methods
###############################################################################

class FeatureContext(object):
    """
    Class representing a "feature context" for the ``authres`` package.
    A feature context is a collection of extension modules that may override
    the core AuthenticationResultsHeader class or result classes, or provide
    additional result classes for new authentication methods.

    To instantiate a feature context, import the desired ``authres.…`` extension
    modules and pass them to ``FeatureContext()``.

    A ``FeatureContext`` object provides ``parse``, ``parse_value``, ``header``,
    and ``result`` methods specific to the context's feature set.
    """

    def __init__(self, *modules):
        self.header_class                = authres.core.AuthenticationResultsHeader
        self.result_class_by_auth_method = {}

        modules = [authres.core] + list(modules)
        for module in modules:
            try:
                self.header_class = module.AuthenticationResultsHeader
            except AttributeError:
                # Module does not provide new AuthenticationResultsHeader class.
                pass

            try:
                for result_class in module.RESULT_CLASSES:
                    self.result_class_by_auth_method[result_class.METHOD] = result_class
            except AttributeError:
                # Module does not provide AuthenticationResult subclasses.
                pass

    def parse(self, string):
        return self.header_class.parse(self, string)

    def parse_value(self, string):
        return self.header_class.parse_value(self, string)

    def header(self,
        authserv_id = None,  authserv_id_comment = None,
        version     = None,  version_comment     = None,
        results     = None
    ):
        return self.header_class(
            self, authserv_id, authserv_id_comment, version, version_comment, results)

    def result(self, method, version = None,
        result = None, result_comment = None,
        reason = None, reason_comment = None,
        properties = None
    ):
        try:
            return self.result_class_by_auth_method[method](version,
                result, result_comment, reason, reason_comment, properties)
        except KeyError:
            return authres.core.AuthenticationResult(method, version,
                result, result_comment, reason, reason_comment, properties)

_core_features = None
def core_features():
    "Returns default feature context providing only RFC 5451 core features."
    global _core_features
    if not _core_features:
        _core_features = FeatureContext()
    return _core_features

_all_features = None
def all_features():
    """
    Returns default feature context providing all features shipped with the
    ``authres`` package.
    """
    global _all_features
    if not _all_features:
        import authres.dkim_b, authres.dkim_adsp, authres.vbr
        _all_features = FeatureContext(authres.dkim_b, authres.dkim_adsp, authres.vbr)
    return _all_features

# Simple API with implicit core-features-only context
###############################################################################

class AuthenticationResultsHeader(authres.core.AuthenticationResultsHeader):
    @classmethod
    def parse(self, string):
        return authres.core.AuthenticationResultsHeader.parse(core_features(), string)

    @classmethod
    def parse_value(self, string):
        return authres.core.AuthenticationResultsHeader.parse_value(core_features(), string)

    def __init__(self,
        authserv_id = None,  authserv_id_comment = None,
        version     = None,  version_comment     = None,
        results     = None
    ):
        authres.core.AuthenticationResultsHeader.__init__(self,
            core_features(), authserv_id, authserv_id_comment, version, version_comment, results)

def result(method, version = None,
    result = None, result_comment = None,
    reason = None, reason_comment = None,
    properties = None
):
    return core_features().result(method, version,
        result, result_comment, reason, reason_comment, properties)

def header(
    authserv_id = None,  authserv_id_comment = None,
    version     = None,  version_comment     = None,
    results     = None
):
    return core_features().header(
        authserv_id, authserv_id_comment, version, version_comment, results)

def parse(string):
    return core_features().parse(string)

def parse_value(string):
    return core_features().parse_value(string)

# vim:sw=4 sts=4
