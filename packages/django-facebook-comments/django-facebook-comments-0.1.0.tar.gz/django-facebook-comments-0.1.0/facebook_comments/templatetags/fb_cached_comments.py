from django import template
from facebook_comments.models import FacebookCommentCache

register = template.Library()

@register.inclusion_tag('facebook_comments/cached_comments.html')
def fb_cached_comments(href):
	comments = FacebookCommentCache.get(href)
	return {'comments': comments}
