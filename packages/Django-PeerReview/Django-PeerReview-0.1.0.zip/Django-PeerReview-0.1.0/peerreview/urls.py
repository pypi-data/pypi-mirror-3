from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
    url(r'peer-review-email-remainder/(?P<review_id>\d)/$', email_remainder, name = 'peer-review-email-remainder'),
    url(r'peer-review-email-message/(?P<review_id>\d)/$', email_message, name = 'peer-review-email-message'),
    url(r'index$', index, name = 'peer-review-index'),
    url(r'items_list/(?P<review_id>\d)/$', items_list, name = 'peer-review-items-list'),
    url(r'login/$', login_view, name = 'peer-review-login'),
    url(r'(?P<review_id>\d)/(?P<content_type>\w+)/(?P<content_id>\d)/(?P<review_option_id>\d)/$', add_entry, name = 'peer-review-add-entry'),
    url(r'(?P<review_id>\d)/$', details, name = 'peer-review-review-details'),
    url(r'add_items$', add_items_to_review, name = 'peer-review-add-items-to-review'),
    url(r'review_item$', review_item, name = 'peer-review-review-item'),
    url(r'post_comment$', post_comment, name = 'peer-review-post-comment'),
)