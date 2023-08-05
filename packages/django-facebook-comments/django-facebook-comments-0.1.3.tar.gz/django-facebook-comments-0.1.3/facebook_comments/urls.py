from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('',
	url(r'^recache/', 'facebook_comments.views.recache', name="facebook_comments_recache"),
	url(r'^channel/', 'facebook_comments.views.channel', name="facebook_comments_channel"),
)
