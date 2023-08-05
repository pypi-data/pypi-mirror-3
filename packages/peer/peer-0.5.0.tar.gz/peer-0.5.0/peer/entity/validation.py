# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

import urlparse

from lxml import etree
from django.utils.importlib import import_module
from django.conf import settings

from peer.entity.models import Metadata


def validate(entity, doc):
    """
    Call all validators defined in in settings.METADATA_VALIDATORS
    on the xml given as a sttring (doc). Information about the
    entity this metadata is validating for is passed in the first
    argument (entity).

    Each entry in METADATA_VALIDATORS is a string with the import path
    to a callable that accepts a string as input and returns a list
    of strings describing errors, or an empty list on no errors.
    """
    try:
        validators = settings.METADATA_VALIDATORS
    except AttributeError:
        validators = []
    errors = set()
    for v in validators:
        val_list = v.split('.')
        mname = '.'.join(val_list[:-1])
        cname = val_list[-1]
        module = import_module(mname)
        validator = getattr(module, cname)
        errors.update(validator(entity, doc))
    return list(errors)


def _parse_metadata(doc):
    """Aux function that returns a list of errors and a metadata object"""
    try:
        metadata = Metadata(etree.XML(doc))
    except etree.XMLSyntaxError, e:
        # XXX sin traducir (como traducimos e.msg?)
        error = e.msg or 'Unknown error, perhaps an empty doc?'
        return [u'XML syntax error: ' + error], None
    else:
        return [], metadata


def validate_xml_syntax(entity, doc):
    """
    Check that the provided string contains synctactically valid xml,
    simply by trying to parse it with lxml.
    """
    return _parse_metadata(doc)[0]


def validate_domain_in_endpoints(entity, doc):
    """
    Makes sure the endpoints urls belongs to the domain of the entity
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    domain = entity.domain.name

    for endpoint in metadata.endpoints:
        url = urlparse.urlparse(endpoint['Location'])
        if url.netloc.lower() != domain.lower():
            errors.append(
                u'The endpoint at %s does not belong to the domain %s' %
                (endpoint['Location'], domain))

    return errors


def validate_domain_in_entityid(entity, doc):
    """
    Makes sure the entityid url belongs to the domain of the entity
    """
    errors, metadata = _parse_metadata(doc)
    if errors:
        return errors

    domain = entity.domain.name

    url = urlparse.urlparse(metadata.entityid)
    if url.netloc.lower() != domain.lower():
        errors.append(
            u'The entityid does not belong to the domain %s' % domain)

    return errors
