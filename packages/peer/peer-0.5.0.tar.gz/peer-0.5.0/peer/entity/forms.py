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

from django import forms
from django.utils.translation import ugettext as _

from peer.customfields import TermsOfUseField, readtou
from peer.entity.models import Entity


class EditEntityForm(forms.ModelForm):

    class Meta:
        model = Entity
        fields = ('name', )

    def clean(self):
        name = self.cleaned_data.get('name')
        if name:
            for ch in r'!:&\|':
                if ch in name:
                    raise forms.ValidationError(
                            _('Illegal characters in the name: '
                              'You cannot use &, |, !, : or \\'))

        return self.cleaned_data


class EntityForm(forms.ModelForm):

    class Meta:
        model = Entity
        fields = ('name', 'domain')

    def __init__(self, user, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['domain'].queryset = self.fields['domain'].queryset.filter(
            owner=self.user, validated=True)

    def clean_domain(self):
        domain = self.cleaned_data.get('domain')
        if domain and (domain.owner != self.user):
            raise forms.ValidationError(_('You are not the domain owner'))

        return domain

    def clean(self):
        name = self.cleaned_data.get('name')
        domain = self.cleaned_data.get('domain')

        if name and domain:
            for ch in r'!:&\|':
                if ch in name:
                    raise forms.ValidationError(_('Illegal characters in the name: '
                                                  'You cannot use &, |, !, : or \\'))
            try:
                Entity.objects.get(name=name, domain=domain)
                raise forms.ValidationError(_('There is already an entity with that name for that domain'))
            except Entity.DoesNotExist:
                pass

        return self.cleaned_data


class MetadataTextEditForm(forms.Form):

    metadata_text = forms.CharField('metadata_text',
                label=_('Metadata'),
            help_text=_('Edit the metadata for this entity'),
        widget=forms.Textarea())
    commit_msg_text = forms.CharField('commit_msg_text',
                    required=True,
                label=_('Commit message'),
            help_text=_('Short description of the commited changes'))


class MetadataFileEditForm(forms.Form):

    metadata_file = forms.FileField('metadata_file',
                label=_('Metadata'),
            help_text=_('Upload a file with the metadata for this entity'))
    commit_msg_file = forms.CharField('commit_msg_file',
                    required=True,
                label=_('Commit message'),
            help_text=_('Short description of the commited changes'))
    tou = TermsOfUseField(readtou('USER_REGISTER_TERMS_OF_USE'))


class MetadataRemoteEditForm(forms.Form):

    metadata_url = forms.URLField('metadata_url',
                    required=True,
                label=_('Metadata'),
            help_text=_('Enter the URL of an XML document'
                        ' with the metadata for this entity'))
    commit_msg_remote = forms.CharField('commit_msg_remote',
                    required=True,
                label=_('Commit message'),
            help_text=_('Short description of the commited changes'))
    tou = TermsOfUseField(readtou('METADATA_IMPORT_TERMS_OF_USE'))
