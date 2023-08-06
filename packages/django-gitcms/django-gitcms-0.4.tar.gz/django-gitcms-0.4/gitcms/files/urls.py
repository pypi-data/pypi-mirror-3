from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
    url(r'^files/(?P<path>.+)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT + '/files'},
        name='files'),
)

