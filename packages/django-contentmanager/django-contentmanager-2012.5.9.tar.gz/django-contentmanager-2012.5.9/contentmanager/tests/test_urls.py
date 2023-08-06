from django.conf.urls.defaults import *


urlpatterns = patterns('contentmanager.views',
    url(r'^(?P<area_id>\d+)/(?P<path_id>\d+)/(?P<position>\d+)/add/$',
        'add_block',
        name='add_block'),
    url(r'^(?P<block_id>\d+)/edit/$',
        'edit_block',
        name='edit_block'),
    url(r'^(?P<block_id>\d+)/move/$',
        'move_block',
        name='move_block'),
    url(r'^(?P<block_id>\d+)/delete/$',
        'delete_block',
        name='delete_block'),
)
