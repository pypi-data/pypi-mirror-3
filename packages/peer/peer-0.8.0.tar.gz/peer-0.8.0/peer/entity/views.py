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

from pygments import highlight
from pygments.lexers import XmlLexer, DiffLexer
from pygments.formatters import HtmlFormatter

from django import db
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.utils import DatabaseError
from django.db import transaction
from django.utils.translation import ugettext as _

from peer.account.templatetags.account import authorname
from peer.domain.models import Domain
from peer.entity.filters import get_filters, filter_entities
from peer.entity.forms import EditEntityForm, EntityForm, MetadataTextEditForm
from peer.entity.forms import MetadataFileEditForm, MetadataRemoteEditForm
from peer.entity.forms import EditMetarefreshForm
from peer.entity.forms import EntityGroupForm
from peer.entity.models import Entity, PermissionDelegation, EntityGroup
from peer.entity.security import can_edit_entity
from peer.entity.security import can_change_entity_team
from peer.entity.security import can_edit_entity_group
from peer.entity.utils import add_previous_revisions, EntitiesPaginator
from peer.entity.feeds import EntitiesFeed


def _paginated_list_of_entities(request, entities):
    paginator = EntitiesPaginator(entities, get_entities_per_page())

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        entities = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entities = paginator.page(paginator.num_pages)
    return entities


def get_entities_per_page():
    if hasattr(settings, 'ENTITIES_PER_PAGE'):
        return settings.ENTITIES_PER_PAGE
    else:
        return 10


def entities_list(request):
    entities = Entity.objects.all()
    paginated_entities = _paginated_list_of_entities(request, entities)

    return render_to_response('entity/list.html', {
            'entities': paginated_entities,
            }, context_instance=RequestContext(request))


@login_required
def entity_add(request):
    return entity_add_with_domain(request, None, 'edit_metadata')


@login_required
def entity_add_with_domain(request, domain_name=None,
                           return_view_name='account_profile'):
    if domain_name is None:
        entity = None
    else:
        domain = get_object_or_404(Domain, name=domain_name)
        entity = Entity(domain=domain)

    if request.method == 'POST':
        form = EntityForm(request.user, request.POST, instance=entity)
        if form.is_valid():
            form.save()
            form.instance.owner = request.user
            form.instance.save()
            messages.success(request, _('Entity created succesfully'))
            if return_view_name == 'edit_metadata':
                url = reverse(return_view_name, args=[form.instance.id])
            else:
                url = reverse(return_view_name)
            return HttpResponseRedirect(url)
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityForm(request.user, instance=entity)

    return render_to_response('entity/add.html', {
            'form': form,
            }, context_instance=RequestContext(request))


def entity_view(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    revs = add_previous_revisions(entity.metadata.list_revisions())
    return render_to_response('entity/view.html', {
            'entity': entity,
            'revs': revs,
            }, context_instance=RequestContext(request))


@login_required
def entity_remove(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        username = authorname(request.user)
        commit_msg = u'entity removed'
        entity.metadata.delete(username, commit_msg)
        entity.delete()
        messages.success(request, _('Entity removed succesfully'))
        return HttpResponseRedirect(reverse('entities_list'))

    return render_to_response('entity/remove.html', {
            'entity': entity,
            }, context_instance=RequestContext(request))


@login_required
def entity_edit(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = EditEntityForm(request.POST, instance=entity)
        if form.is_valid():
            form.save()
            messages.success(request, _('Entity edited succesfully'))
            return HttpResponseRedirect(reverse('entity_view',
                                                args=(entity_id,)))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = EditEntityForm(instance=entity)

    return render_to_response('entity/edit.html', {
            'entity': entity,
            'form': form,
            }, context_instance=RequestContext(request))


# ENTITY GROUP

@login_required
def entity_group_add(request, return_view_name='entity_group_view'):
    if request.method == 'POST':
        form = EntityGroupForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            messages.success(request, _(u'Entity group created'))
            return HttpResponseRedirect(
                reverse(return_view_name, args=[instance.id])
                )
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityGroupForm()

    return render_to_response('entity/edit_entity_group.html', {
            'form': form,
            }, context_instance=RequestContext(request))


@login_required
def entity_group_view(request, entity_group_id):
    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)
    queries = entity_group.query.split('&')
    entities_in_group = Entity.objects.xpath_filters(queries)

    # Can't do it at the model because of circular dependency
    entity_group.feed_url = EntitiesFeed().link() + '?xpath=' + entity_group.query

    entities = _paginated_list_of_entities(request, entities_in_group)

    return render_to_response('entity/view_entity_group.html', {
            'entity_group': entity_group,
            'entities': entities,
            }, context_instance=RequestContext(request))


@login_required
def entity_group_edit(request, entity_group_id,
                      return_view_name='entity_group_view'):

    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)

    if not can_edit_entity_group(request.user, entity_group):
        raise PermissionDenied

    if request.method == 'POST':
        form = EntityGroupForm(request.POST, instance=entity_group)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Entity group edited succesfully'))
            return HttpResponseRedirect(
                reverse(return_view_name, args=[form.instance.id])
                )
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityGroupForm(instance=entity_group)

    return render_to_response('entity/edit_entity_group.html', {
            'entity_group': entity_group,
            'form': form,
            }, context_instance=RequestContext(request))


@login_required
def entity_group_remove(request, entity_group_id,
                        return_view_name='account_profile'):

    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)

    if not can_edit_entity_group(request.user, entity_group):
        raise PermissionDenied

    if request.method == 'POST':
        entity_group.delete()
        messages.success(request, _('Entity group removed succesfully'))
        return HttpResponseRedirect(reverse(return_view_name))

    return render_to_response('entity/remove_entity_group.html', {
            'entity_group': entity_group,
            }, context_instance=RequestContext(request))


@login_required
def metarefresh_edit(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = EditMetarefreshForm(request.POST)
        if form.is_valid():
            entity.metarefresh_frequency = \
                    form.cleaned_data['metarefresh_frequency']
            entity.save()
            messages.success(request, _('Metarefresh edited succesfully'))
            return HttpResponseRedirect(reverse('metarefresh_edit',
                                                args=(entity_id,)))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = EditMetarefreshForm(instance=entity)

    return render_to_response('entity/edit_metarefresh.html', {
            'entity': entity,
            'form': form,
            }, context_instance=RequestContext(request))


# METADATA EDIT

def _get_edit_metadata_form(request, entity, edit_mode, form=None):
    if form is None:
        if edit_mode == 'text':
            text = entity.metadata.get_revision()
            form = MetadataTextEditForm(entity, request.user,
                                        initial={'metadata_text': text})
        elif edit_mode == 'file':
            # XXX siempre vacia, imborrable, required
            form = MetadataFileEditForm(entity, request.user)
        elif edit_mode == 'remote':
            form = MetadataRemoteEditForm(entity, request.user)
    form_action = reverse('%s_edit_metadata' % edit_mode, args=(entity.id, ))

    context_instance = RequestContext(request)
    return render_to_string('entity/simple_edit_metadata.html', {
        'edit': edit_mode,
        'entity': entity,
        'form': form,
        'form_action': form_action,
        'form_id': edit_mode + '_edit_form',
    }, context_instance=context_instance)


def _handle_metadata_post(request, form, return_view):
    if form.is_valid():
        if request.is_ajax():
            diff = form.get_diff()
            html = highlight(diff, DiffLexer(), HtmlFormatter(linenos=True))
            return HttpResponse(html.encode(settings.DEFAULT_CHARSET))
        else:
            form.save()
            messages.success(request, _('Entity metadata has been modified'))
            return_url = reverse(return_view, args=(form.entity.id, ))
            return HttpResponseRedirect(return_url)
    else:
        messages.error(request, _('Please correct the errors indicated below'))
        if request.is_ajax():
            content = render_to_string('entity/validation_errors.html', {
                    'errors': form.errors,
                    }, context_instance=RequestContext(request))
            return HttpResponseBadRequest(content)


@login_required
def text_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = MetadataTextEditForm(entity, request.user, request.POST)
        result = _handle_metadata_post(request, form, 'text_edit_metadata')
        if result is not None:
            return result
    else:
        form = None

    return edit_metadata(request, entity.id, text_form=form,
                         edit_mode='text')


@login_required
def file_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = MetadataFileEditForm(entity, request.user,
                                    request.POST, request.FILES)
        result = _handle_metadata_post(request, form, 'file_edit_metadata')
        if result is not None:
            return result
    else:
        form = None
    return edit_metadata(request, entity.id, edit_mode='upload',
                         file_form=form)


@login_required
def remote_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = MetadataRemoteEditForm(entity, request.user, request.POST)
        result = _handle_metadata_post(request, form, 'remote_edit_metadata')
        if result is not None:
            return result
    else:
        form = None

    return edit_metadata(request, entity.id, edit_mode='remote',
                         remote_form=form)


DEFAULT_SAML_META_JS_PLUGINS = ('attributes', 'certs', 'contact', 'info',
                                'location', 'saml2sp')


@login_required
def edit_metadata(request, entity_id, edit_mode='text',
                  text_form=None, file_form=None, remote_form=None):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    samlmetajs_plugins = getattr(settings, 'SAML_META_JS_PLUGINS',
                                 DEFAULT_SAML_META_JS_PLUGINS)

    return render_to_response('entity/edit_metadata.html', {
            'entity': entity,
            'text_html': _get_edit_metadata_form(request, entity, 'text',
                                                 form=text_form),
            'file_html': _get_edit_metadata_form(request, entity, 'file',
                                                 form=file_form),
            'remote_html': _get_edit_metadata_form(request, entity, 'remote',
                                                   form=remote_form),
            'edit_mode': edit_mode,
            'samlmetajs_plugins': samlmetajs_plugins,
            'needs_google_maps': 'location' in samlmetajs_plugins,
            }, context_instance=RequestContext(request))


# ENTITY SEARCH

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

    paginated_entities = _paginated_list_of_entities(request, entities)
    return render_to_response('entity/search_results.html', {
            'entities': paginated_entities,
            'search_terms': search_terms_raw,
            'filters': filters,
            'query_string': u'&'.join(query_string),
            }, context_instance=RequestContext(request))


# SHARING ENTITY EDITION

@login_required
def sharing(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    return render_to_response('entity/sharing.html', {
            'entity': entity,
            }, context_instance=RequestContext(request))


@login_required
def list_delegates(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    return render_to_response('entity/delegate_list.html', {
            'delegates': entity.delegates.all(),
            'entity_id': entity.pk,
            }, context_instance=RequestContext(request))


@login_required
def remove_delegate(request, entity_id, user_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    delegate = User.objects.get(pk=user_id)
    if entity and delegate:
        delegations = PermissionDelegation.objects.filter(entity=entity,
                                                  delegate=delegate)
        for delegation in delegations:
            delegation.delete()
    return list_delegates(request, entity_id)


@login_required
def add_delegate(request, entity_id, username):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    new_delegate = User.objects.get(username=username)
    if entity and new_delegate:
        pd = PermissionDelegation.objects.filter(entity=entity,
                                                delegate=new_delegate)
        if not pd and new_delegate != entity.owner:
            pd = PermissionDelegation(entity=entity, delegate=new_delegate)
            pd.save()
        elif pd:
            return HttpResponse('delegate')
        else:
            return HttpResponse('owner')
    return list_delegates(request, entity_id)


@login_required
def make_owner(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    old_owner = entity.owner
    new_owner_id = request.POST.get('new_owner_id')
    if new_owner_id:
        new_owner = User.objects.get(pk=int(new_owner_id))
        if new_owner:
            entity.owner = new_owner
            entity.save()
            msg = _('New owner successfully set')
            old_pd = PermissionDelegation.objects.get(entity=entity,
                                                  delegate=new_owner)
            if old_pd:
                old_pd.delete()
            if old_owner:
                new_pd = PermissionDelegation.objects.filter(entity=entity,
                                              delegate=old_owner)
                if not new_pd:
                    new_pd = PermissionDelegation(entity=entity,
                                                  delegate=old_owner)
                    new_pd.save()
        else:
            msg = _('User not found')
    else:
        msg = _('You must provide the user id of the new owner')
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('entity_view', args=(entity_id,)))

# ENTITY DETAILS

HTML_WRAPPER = u'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%s - %s</title>
</head>
<body>
%s
</body>
</html>
'''


def get_diff(request, entity_id, r1, r2):
    entity = get_object_or_404(Entity, id=entity_id)
    diff = entity.metadata.get_diff(r1, r2)
    formatter = HtmlFormatter(linenos=True)
    html = HTML_WRAPPER % (entity_id, u'%s:%s' % (r1, r2),
                           highlight(diff, DiffLexer(), formatter))
    return HttpResponse(html.encode(settings.DEFAULT_CHARSET))


#import difflib
#def get_diff2(request, entity_id, r1, r2):
#    entity = get_object_or_404(Entity, id=entity_id)
#    md1 = entity.metadata.get_revision(r1).split('\n')
#    md2 = entity.metadata.get_revision(r2).split('\n')
#    html = difflib.HtmlDiff().make_table(md1, md2)
#    return HttpResponse(html)


def get_revision(request, entity_id, rev):
    entity = get_object_or_404(Entity, id=entity_id)
    md = entity.metadata.get_revision(rev)
    formatter = HtmlFormatter(linenos=True)
    html = HTML_WRAPPER % (entity_id, rev,
                           highlight(md, XmlLexer(), formatter))
    return HttpResponse(html.encode(settings.DEFAULT_CHARSET))


def get_latest_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    metadata_text = entity.metadata.get_revision()
    return HttpResponse(metadata_text, mimetype="application/samlmetadata+xml")


@cache_page
def get_pygments_css(request):
    formatter = HtmlFormatter(linenos=True, outencoding='utf-8')
    return HttpResponse(content=formatter.get_style_defs(arg=''),
                    mimetype='text/css',
                content_type='text/css; charset=' + settings.DEFAULT_CHARSET)
