from django.conf.urls.defaults import patterns, include, url

from main.views import send_simple_email

# django-sendgrid
# from constants import POST_EVENT_URL as _POST_EVENT_URL
from views import listener


# POST_EVENT_URL = getattr(settings, "POST_EVENT_URL", _POST_EVENT_URL)
# POST_EVENT_URL_PATTERN = r"^{url}$".format(url=POST_EVENT_URL)

urlpatterns = patterns('',
	# url(POST_EVENT_URL_PATTERN, post_event, name="sendgrid_post_event"),
	url(r"^listener/$", "sendgrid.views.listener", name="sendgrid_post_event"),
)

# from django.conf.urls.defaults import *
# from tastypie.api import Api
# from myapp.api import EntryResource
# 
# v1_api = Api(api_name='v1')
# v1_api.register(EntryResource())
# 
# urlpatterns = patterns('',
# 	# The normal jazz here then...
# 	(r'^api/', include(v1_api.urls)),
# )
