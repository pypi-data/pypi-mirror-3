# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('coop_cms.views',
    url(r'^cms/tree/$', 'process_nav_edition', name='navigation_tree'),
    url(r'^cms/media-images/$', 'show_media', {'media_type': 'image'}, name='coop_cms_media_images'),
    url(r'^cms/media-documents/$', 'show_media', {'media_type': 'document'}, name='coop_cms_media_documents'),
    url(r'^cms/upload-image/$', 'upload_image', name="coop_cms_upload_image"),
    url(r'^cms/upload-doc/$', 'upload_doc', name="coop_cms_upload_doc"),
    url(r'^cms/change-template/(?P<article_id>\d*)/$', 'change_template', name="coop_cms_change_template"),
    url(r'^cms/update-logo/(?P<article_id>\d*)/$', 'update_logo', name="coop_cms_update_logo"),
    url(r'^cms/private-download/(?P<doc_id>\d*)/$', 'download_doc', name='coop_cms_download_doc'),
    url(r'^newsletter/(?P<newsletter_id>\d+)/$', 'view_newsletter', name='coop_cms_view_newsletter'),
    url(r'^newsletter/(?P<newsletter_id>\d+)/cms_edit/$', 'edit_newsletter', name='coop_cms_edit_newsletter'),
    url(r'^newsletter/change-template/(?P<newsletter_id>\d+)/$', 'change_newsletter_template', name="coop_cms_change_newsletter_template"),
    url(r'^newsletter/test/(?P<newsletter_id>\d+)/$', 'test_newsletter', name="coop_cms_test_newsletter"),
    url(r'^newsletter/schedule/(?P<newsletter_id>\d+)/$', 'schedule_newsletter_sending', name="coop_cms_schedule_newsletter_sending"),
    
    #keep these at the end
    url(r'^(?P<url>.*)/cms_publish/$', 'publish_article', name='coop_cms_publish_article'),
    url(r'^(?P<url>.*)/cms_edit/$', 'edit_article', name='coop_cms_edit_article'),
    url(r'^(?P<url>.*)/cms_cancel/$', 'cancel_edit_article', name='coop_cms_cancel_edit_article'),
    url(r'^(?P<url>.*)/$', 'view_article', name='coop_cms_view_article'),
)
