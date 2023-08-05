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
from tempfile import NamedTemporaryFile
import urllib2

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
from django.core.files.base import File
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import HttpResponse
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
from peer.entity.models import Entity, PermissionDelegation
from peer.entity.security import can_edit_entity, can_change_entity_team
from peer.entity.utils import add_previous_revisions
from peer.entity.validation import validate


CONNECTION_TIMEOUT = 10


def _paginated_list_of_entities(request, entities):
    paginator = Paginator(entities, get_entities_per_page())

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


# METADATA EDIT

def _get_edit_metadata_form(request, entity, edit_mode, form=None):
    if form is None:
        if edit_mode == 'text':
            text = entity.metadata.get_revision()
            form = MetadataTextEditForm(initial={'metadata_text': text})
        elif edit_mode == 'file':
            # XXX siempre vacia, imborrable, required
            form = MetadataFileEditForm()
        elif edit_mode == 'remote':
            form = MetadataRemoteEditForm()
    form_action = reverse('%s_edit_metadata' % edit_mode, args=(entity.id, ))

    context_instance = RequestContext(request)
    return render_to_string('entity/simple_edit_metadata.html', {
        'edit': edit_mode,
        'entity': entity,
        'form': form,
        'form_action': form_action,
        'form_id': edit_mode + '_edit_form',
    }, context_instance=context_instance)


@login_required
def text_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = MetadataTextEditForm(request.POST)
        text = form['metadata_text'].data.strip()
        if not text:
            form.errors['metadata_text'] = [_('Empty metadata not allowed')]
        else:
            errors = validate(entity, text)
            if errors:
                form.errors['metadata_text'] = errors
        if form.is_valid():
            tmp = NamedTemporaryFile(delete=True)
            tmp.write(text.encode('utf8'))
            tmp.seek(0)
            content = File(tmp)
            name = entity.metadata.name
            username = authorname(request.user)
            commit_msg = form['commit_msg_text'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
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
        form = MetadataFileEditForm(request.POST, request.FILES)
        content = form['metadata_file'].data
        if content is not None:
            text = content.read()
            content.seek(0)
            if not text:
                form.errors['metadata_file'] = [_('Empty metadata not allowed')]
            else:
                errors = validate(entity, text)
                if errors:
                    form.errors['metadata_file'] = errors
        if form.is_valid():
            name = entity.metadata.name
            username = authorname(request.user)
            commit_msg = form['commit_msg_file'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
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
        form = MetadataRemoteEditForm(request.POST)
        if form.is_valid():
            content_url = form['metadata_url'].data
            try:
                resp = urllib2.urlopen(content_url, None, CONNECTION_TIMEOUT)
            except urllib2.URLError, e:
                form.errors['metadata_url'] = ['URL Error: ' + str(e)]
            except urllib2.HTTPError, e:
                form.errors['metadata_url'] = ['HTTP Error: ' + str(e)]
            except ValueError, e:
                try:
                    resp = urllib2.urlopen('http://' + content_url,
                                                 None, CONNECTION_TIMEOUT)
                except Exception:
                    form.errors['metadata_url'] = ['Value Error: ' + str(e)]
            except Exception, e:
                form.errors['metadata_url'] = ['Error: ' + str(e)]
            if form.is_valid():
                if resp.getcode() != 200:
                    form.errors['metadata_url'] = [_(
                                          'Error getting the data: %s'
                                                    ) % resp.msg]
                text = resp.read()
                if not text:
                    form.errors['metadata_url'] = [_('Empty metadata not allowed')]
                else:
                    errors = validate(entity, text)
                    if errors:
                        form.errors['metadata_url'] = errors
                try:
                    encoding = resp.headers['content-type'].split('charset=')[1]
                except (KeyError, IndexError):
                    encoding = ''
                resp.close()
        if form.is_valid():
            tmp = NamedTemporaryFile(delete=True)
            if encoding:
                text = text.decode(encoding).encode('utf8')
            tmp.write(text)
            tmp.seek(0)
            content = File(tmp)
            name = entity.metadata.name
            username = authorname(request.user)
            commit_msg = form['commit_msg_remote'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
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


def get_diff(request, entity_id, r1, r2):
    entity = get_object_or_404(Entity, id=entity_id)
    diff = entity.metadata.get_diff(r1, r2)
    formatter = HtmlFormatter(linenos=True,
                      outencoding=settings.DEFAULT_CHARSET)
    html = highlight(diff, DiffLexer(), formatter)
    return HttpResponse(html)


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
    formatter = HtmlFormatter(linenos=True,
                      outencoding=settings.DEFAULT_CHARSET)
    html = highlight(md, XmlLexer(), formatter)
    return HttpResponse(html)


@cache_page
def get_pygments_css(request):
    formatter = HtmlFormatter(linenos=True, outencoding='utf-8')
    return HttpResponse(content=formatter.get_style_defs(arg=''),
                    mimetype='text/css',
                content_type='text/css; charset=' + settings.DEFAULT_CHARSET)
