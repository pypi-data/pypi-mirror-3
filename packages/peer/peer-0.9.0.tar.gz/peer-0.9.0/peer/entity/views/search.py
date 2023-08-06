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

import re

from django import db
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.utils import DatabaseError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from peer.entity.filters import get_filters, filter_entities
from peer.entity.models import Entity
from peer.entity.paginator import paginated_list_of_entities


def _search_entities(search_terms):
    lang = getattr(settings, 'PG_FT_INDEX_LANGUAGE', u'english')
    sql = u"select * from entity_entity where to_tsvector(%s, name) @@ to_tsquery(%s, %s)"
    return Entity.objects.raw(sql, [lang, lang, search_terms])


def search_entities(request):
    search_terms_raw = request.GET.get('query', '').strip()
    op = getattr(settings, 'PG_FTS_OPERATOR', '&')
    sid = transaction.savepoint()
    if db.database['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        search_terms = re.sub(ur'\s+', op, search_terms_raw)
        entities = _search_entities(search_terms)
    else:
        search_terms_list = search_terms_raw.split(' ')
        where = (u' %s ' % op).join([u"name ilike '%s'"] * len(search_terms_list))
        sql = u"select * from entity_entity where " + where
        entities = Entity.objects.raw(sql, search_terms_list)
        search_terms = op.join(search_terms_raw)

    try:
        entities = list(entities)
    except DatabaseError:
        transaction.savepoint_rollback(sid)
        entities = []
        msg = _(u'There seem to be illegal characters in your search.\n'
                u'You should not use !, :, &, | or \\')
        messages.error(request, msg)
    else:
        if search_terms_raw == '':
            entities = Entity.objects.all()
        else:
            n = len(entities)
            plural = n == 1 and 'entity' or 'entities'
            msg = _(u'Found %d %s matching "%s"') % (n, plural,
                                                     search_terms_raw)
            messages.success(request, msg)

    filters = get_filters(request.GET)
    entities = filter_entities(filters, entities)

    query_string = [u'%s=%s' % (f.name, f.current_value)
                    for f in filters if not f.is_empty()]
    if search_terms_raw:
        query_string.append(u'query=%s' % search_terms_raw)

    paginated_entities = paginated_list_of_entities(request, entities)
    return render_to_response('entity/search_results.html', {
            'entities': paginated_entities,
            'search_terms': search_terms_raw,
            'filters': filters,
            'query_string': u'&'.join(query_string),
            }, context_instance=RequestContext(request))
