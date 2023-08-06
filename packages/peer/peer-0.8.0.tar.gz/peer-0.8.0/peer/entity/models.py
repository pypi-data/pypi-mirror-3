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

from datetime import datetime
from lxml import etree
from urlparse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from vff.field import VersionedFileField

from peer.customfields import SafeCharField
from peer.domain.models import Domain
from peer.entity.managers import EntityManager
from peer.entity.utils import NAMESPACES, addns, delns, getlang
from peer.entity.utils import expand_settings_permissions
from peer.entity.utils import FetchError, fetch_resource
from peer.entity.utils import write_temp_file


XML_NAMESPACE = NAMESPACES['xml']
XMLDSIG_NAMESPACE = NAMESPACES['ds']
MDUI_NAMESPACE = NAMESPACES['mdui']

CONNECTION_TIMEOUT = 10


class Metadata(object):

    def __init__(self, etree):
        self.etree = etree

    @property
    def entityid(self):
        if 'entityID' in self.etree.attrib:
            return self.etree.attrib['entityID']

    @property
    def valid_until(self):
        if 'validUntil' in self.etree.attrib:
            value = self.etree.attrib['validUntil']
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:  # Bad datetime format
                pass

    @property
    def organization(self):
        languages = {}
        for org_node in self.etree.findall(addns('Organization')):
            for attr in ('name', 'displayName', 'URL'):
                node_name = 'Organization' + attr[0].upper() + attr[1:]
                for node in org_node.findall(addns(node_name)):
                    lang = getlang(node)
                    if lang is None:
                        continue  # the lang attribute is required

                    lang_dict = languages.setdefault(lang, {})
                    lang_dict[attr] = node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)
        return result

    @property
    def contacts(self):
        result = []
        for contact_node in self.etree.findall(addns('ContactPerson')):
            contact = {}

            if 'contactType' in contact_node.attrib:
                contact['type'] = contact_node.attrib['contactType']

            for child in contact_node:
                contact[delns(child.tag)] = child.text

            result.append(contact)
        return result

    @property
    def certificates(self):
        result = []
        key_descr_path = [addns('SPSSODescriptor'),
                          addns('KeyDescriptor')]

        for key_descriptor in self.etree.findall('/'.join(key_descr_path)):
            cert_path = [addns('KeyInfo', XMLDSIG_NAMESPACE),
                         addns('X509Data', XMLDSIG_NAMESPACE),
                         addns('X509Certificate', XMLDSIG_NAMESPACE)]
            for cert in key_descriptor.findall('/'.join(cert_path)):
                if 'use' in key_descriptor.attrib:
                    result.append({'use': key_descriptor.attrib['use'],
                                   'text': cert.text})
                else:
                    result.append({'use': 'signing and encryption',
                                   'text': cert.text})

        return result

    @property
    def endpoints(self):
        result = []

        def populate_endpoint(node, endpoint):
            for attr in ('Binding', 'Location'):
                if attr in node.attrib:
                    endpoint[attr] = node.attrib[attr]

        path = [addns('SPSSODescriptor'), addns('AssertionConsumerService')]
        for acs_node in self.etree.findall('/'.join(path)):
            acs_endpoint = {'Type': 'Assertion Consumer Service'}
            populate_endpoint(acs_node, acs_endpoint)
            result.append(acs_endpoint)

        path = [addns('SPSSODescriptor'), addns('SingleLogoutService')]
        for lss_node in self.etree.findall('/'.join(path)):
            lss_endpoint = {'Type': 'Single Logout Service'}
            populate_endpoint(lss_node, lss_endpoint)
            result.append(lss_endpoint)

        return result

    @property
    def geolocationhint(self):
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('GeolocationHint', MDUI_NAMESPACE)]
        result = self.etree.find('/'.join(path))
        if result is not None:
            latitude, longitude = result.text.replace('geo:', '').split(',')
            return {'latitude': latitude, 'longitude': longitude}
        else:
            return None

    @property
    def logos(self):
        languages = {}
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('Logo', MDUI_NAMESPACE)]
        for logo_node in self.etree.findall('/'.join(path)):
            lang = getlang(logo_node)
            if lang is None:
                continue  # the lang attribute is required

            lang_dict = languages.setdefault(lang, {})
            lang_dict['width'] = logo_node.attrib.get('width', '')
            lang_dict['height'] = logo_node.attrib.get('height', '')
            lang_dict['location'] = logo_node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)

        return result


class Entity(models.Model):

    name = SafeCharField(_(u'Entity name'), max_length=100)
    metadata = VersionedFileField('metadata', verbose_name=_(u'Entity metadata'),
                                blank=True, null=True,)
    owner = models.ForeignKey(User, verbose_name=_('Owner'),
                              blank=True, null=True)
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))
    delegates = models.ManyToManyField(User, verbose_name=_('Delegates'),
                                       related_name='permission_delegated',
                                       through='PermissionDelegation')
    creation_time = models.DateTimeField(verbose_name=_(u'Creation time'),
                                         auto_now_add=True)
    modification_time = models.DateTimeField(verbose_name=_(u'Modification time'),
                                             auto_now=True)

    FREQ_CHOICES = (
        ('N', 'Never'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )

    metarefresh_frequency = models.CharField(
        verbose_name=_(u'Metadata refreshing frequency'),
        max_length=1,
        choices=FREQ_CHOICES,
        default='N',  # Never
        db_index=True,
    )

    metarefresh_last_run = models.DateTimeField(
        verbose_name=_(u'Last time refreshed'),
        auto_now_add=True,
    )

    objects = EntityManager();

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('entity_view', (str(self.id), ))

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')
        ordering = ('-creation_time', )
        permissions = expand_settings_permissions(include_xpath=False)

    def _load_metadata(self):
        if not hasattr(self, '_parsed_metadata'):
            data = self.metadata.read()
            if not data:
                raise ValueError('no metadata content')
            try:
                self._parsed_metadata = etree.XML(data)
            except etree.XMLSyntaxError:
                raise ValueError('invalid metadata XML')

        return Metadata(self._parsed_metadata)

    def has_metadata(self):
        try:
            self._load_metadata()
        except (ValueError, IOError):
            return False
        else:
            return True

    @property
    def entityid(self):
        return self._load_metadata().entityid

    @property
    def valid_until(self):
        return self._load_metadata().valid_until

    @property
    def organization(self):
        return self._load_metadata().organization

    @property
    def contacts(self):
        return self._load_metadata().contacts

    @property
    def certificates(self):
        return self._load_metadata().certificates

    @property
    def endpoints(self):
        return self._load_metadata().endpoints

    @property
    def geolocationhint(self):
        return self._load_metadata().geolocationhint

    @property
    def logos(self):
        return self._load_metadata().logos

    @property
    def metadata_etree(self):
        if self.has_metadata():
            return self._load_metadata().etree
        else:
            return None

    def is_expired(self):
        return (self.has_metadata() and self.valid_until
                and datetime.now() > self.valid_until)

    @property
    def is_metarefreshable(self):
        result = False
        try:
            entityid = self.entityid
        except IOError:
            return result
        if isinstance(entityid, basestring):
            url = urlparse(entityid)
            result = bool(url.scheme.startswith('http'))
            result = result and bool(url.netloc.split('.')[0])
        return result

    def metarefresh(self):

        noid_msg = "Error: Entity %s doesn't have entityid" % (self.id)

        if not hasattr(self, 'entityid'):
            return noid_msg

        url = self.entityid
        if not url:
            return noid_msg

        try:
            text = fetch_resource(url)
            if text is None:
                text = fetch_resource('http://' + url)

                if text is None:
                    return 'Unknown error while fetching the url'
        except FetchError, e:
            return str(e)

        if not text:
            return 'Empty metadata not allowed'


        content = write_temp_file(text)
        name = self.metadata.name
        commit_msg = 'Updated automatically from %s' % (url)
        self.metadata.save(name, content, self.owner.username, commit_msg)

        self.metarefresh_last_run = datetime.now()
        self.save()

        return 'Success: Data was updated successfully'


def handler_entity_pre_save(sender, instance, **kwargs):
    if not instance.is_metarefreshable:
        instance.metarefresh_frequency = 'N'  # Never
models.signals.pre_save.connect(handler_entity_pre_save, sender=Entity)


class EntityGroup(models.Model):

    name = SafeCharField(_(u'Name of the group'), max_length=200)
    query = SafeCharField(_(u'Query that defines the group'), max_length=100)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Entity group')
        verbose_name_plural = _('Entity groups')


class PermissionDelegation(models.Model):

    entity = models.ForeignKey(Entity, verbose_name=_(u'Entity'))
    delegate = models.ForeignKey(User, verbose_name=_('Delegate'),
                                       related_name='permission_delegate')
    date = models.DateTimeField(_(u'Delegation date'), default=datetime.now)

    def __unicode__(self):
        return ugettext(
            u'%(user)s delegates permissions for %(entity)s entity') % {
            'user': self.entity.owner.username, 'entity': self.entity.name}

    class Meta:
        verbose_name = _(u'Permission delegation')
        verbose_name_plural = _(u'Permission delegations')
