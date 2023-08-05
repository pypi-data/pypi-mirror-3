========
Overview
========

django-facebook-comments is a reusable Django app to place facebook
comment boxes in your templates.

This app basically provides two templatetags to use in your templates,
one which just places in a facebook comment box, and one which
caches the facebook comment box (using their api) so that content
will be in the rendered html (some people like this for SEO purposes).

Dependencies
============

django-facebook-comments was created in Django 1.3.  Please let me
know if you have success with it in lower versions.

Enabling django.core.context_processors.request is also helpful,
since that is the only way to get the current url of the page
the comments is embedded on.


Usage
=====

Add 'facebook_comments' to your INSTALLED_APPS.

Load the 'fb_comments' template tag and use it in your template:

::

    {% extends "whatever.html" %}
    {% load fb_comments %}
    {% block content %}
      <div class="section">
        <h2>{{ post.title }}</h2>
        <div>{{ post.body|safe }}</div>
        <p>Published {{ post.created_at|date:"Y/m/d" }}</p>
      </div>
      {% fb_comments width="600" include_cached_comments no_scripts %}
    {% endblock %}

Configuration
=============

The templatetag has the following configuration options. None of these
are required.  The flags are included as is, the variables are included
using variable_name="value" for static values.  Drop the quotes and
the value will be taken out of that variable name in the context.


Flags:

include_cached_comments
  Output cached comments in the templatetag output.  This will be a div
  with class="cached_comments"

no_scripts
  This flag will cause required inline javascript to not be rendered
  in the templatetag.  This is if you have multiple comment boxes
  on the page, or if you already have it in page for some other
  purpose.

Variables:

num_posts
  Number of posts to show

width
  Width (in pixels) of comment box

colorscheme
  Colorscheme option to pass (please refer to facebook api for
  available colorschemes)

href
  Fully qualified uri to pass to facebook.  If you have
  django.core.context_processors.request enabled you can
  leave this blank (and it'll inspect the RequestContext to
  decide the current href).  Otherwise you're on your own.
  Please note: this means you CANNOT stick things like
  '.' or '/' in here to mean the current page/site.


Contributors
============

  * `Shu Zong Chen`_
  * Locale patch `Panosl`_

.. CONTRIBUTORS

.. _`Shu Zong Chen`: http://freelancedreams.com/
.. _`Panosl`: http://bitbucket.org/panosl/
