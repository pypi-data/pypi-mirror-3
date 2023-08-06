from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<url>.+)$',
        'vintage.views.render_archivedpage',
        name='vintage_detail'),
)
