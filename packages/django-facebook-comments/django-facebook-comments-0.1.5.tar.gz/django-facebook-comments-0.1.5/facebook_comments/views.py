from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.template import loader, Template, RequestContext
import urllib
from facebook_comments.models import FacebookCommentCache
from facebook_comments.conf import settings

def recache(request):
	if request.method == 'POST':
		if request.POST['href']:
			href = request.POST['href']
			rfh = urllib.urlopen('https://graph.facebook.com/comments/?ids=' + urllib.quote_plus(href))
			response = rfh.read()
			try:
				FacebookCommentCache.upsert(href, response)
			except ValueError:
				pass
		return HttpResponse("success")
	return HttpResponse("Invalid Request", status=500)

@csrf_protect
def channel(request):
	t = loader.get_template('facebook_comments/channel.html')
	ctx = RequestContext(request, {'locale': settings.LOCALE})
	fake_csrf = Template("{{ csrf_token }}")
	fake_csrf.render(ctx)
	return HttpResponse(t.render(ctx))

