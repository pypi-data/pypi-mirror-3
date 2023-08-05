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


from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from peer.account.forms import RegistrationFormCaptchaTOU
from registration import urls as registration_urls

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^', include('peer.portal.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/profile/$', 'peer.account.views.profile',
        name='account_profile'),
    url(r'^accounts/profile/edit/$', 'peer.account.views.profile_edit',
        name='account_profile_edit'),
    url(r'^accounts/register/$', 'registration.views.register', {
            'form_class': RegistrationFormCaptchaTOU
            }, name='registration_register'),
    url(r'^accounts/password_change/$',
        'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^accounts/invite_friend/$',
        'peer.account.views.invite_friend', name='invite_friend'),
    url(r'^accounts/search_users_auto/$',
        'peer.account.views.search_users_auto', name='search_users_auto'),
    (r'^accounts/', include(registration_urls)),

    (r'^domain/', include('peer.domain.urls')),
    (r'^entity/', include('peer.entity.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
                }),
        )

    urlpatterns += staticfiles_urlpatterns()
