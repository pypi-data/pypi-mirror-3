from django.conf.urls.defaults import *

urlpatterns = patterns('aloha.views',
    url('^save/$', 'save', name='aloha_save_content'),
)
