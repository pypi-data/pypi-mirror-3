from django import template
from facebook_comments.conf import settings

register = template.Library()

"""ON THE DEFAULT OPTS
These strings are in '"Value"' format because the kwarg parser for the template
tag expects strings to be in key="value" format. If they weren't wrapped in
double quotes the node would try to resolve the value as a variable name in the
template context
"""
default_opts = {
	#'href': '"example.com"', ## See note below
	'num_posts': '"10"',
	'width': '"500"',
	#'colorscheme': '"light"',
}

"""ON THE MAGIC OF href
So it sorta sucks that the facebook comment plugin doesn't let you put in "/"
or "." or "" to tell it to use the current page. You *have* to stick on a fully
qualified url there.

This makes it rough to do in a template tag, since you'd always have to call
it and pass in a variable that resolves to the current url.  Who wants to do
that? I'm lazy, so don't look at me.

Fortunately, there is a django.core.context_processors.request that you can
use that will stick in the request object.  We can then inspect the
RequestContext and decide the href out of that.

Of course, if you specify an 'href' in the template tag call that will be
used.
"""

avail_flags = ['include_cached_comments', 'no_scripts']

class fb_comments_node(template.Node):
	def __init__(self, *args, **kwargs):
		self.kwargs = dict((k, template.Variable(str(v))) for k, v in kwargs.iteritems())
		self.args = args

	def render(self, context):
		kwargs = dict((k, v.resolve(context)) for k, v in self.kwargs.iteritems())
		if 'href' not in kwargs:
			try:
				req = context['request']
				href = req.build_absolute_uri(req.path)
				kwargs['href'] = href
			except AttributeError:
				raise template.TemplateSyntaxError("You didn't specify href and django.core.context_processors.request isn't around to give me the current url")
		t = template.loader.get_template('facebook_comments/comment_box.html')
		c = {'opts':kwargs}
		for i in self.args:
			c[i] = True
		c['locale'] = settings.LOCALE
		return t.render(template.Context(c))

@register.tag
def fb_comments(parser, token):
	args, kwargs = interpret_args(
		token.split_contents(),
		default = default_opts,
	)
	return fb_comments_node(*args, **kwargs)

def interpret_args(token_args, default):
	args = []
	kwargs = dict(default)
	for token in token_args[1:]:
		if '=' in token:
			key, value = token.split('=', 1)
			kwargs[key] = value
		elif token in avail_flags:
			args.append(token)
		else:
			raise template.TemplateSyntaxError("Invalid flag: {0}".format(token))
	return args, kwargs
