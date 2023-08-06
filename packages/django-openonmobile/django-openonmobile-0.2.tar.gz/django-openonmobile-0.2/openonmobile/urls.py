
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',

    url(r'^qr/$', 'openonmobile.views.qr', name='openonmobile_qr'),

)
