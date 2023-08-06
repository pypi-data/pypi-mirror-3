from django.utils import unittest
from django.template import Context, Template
from django.http import HttpRequest
from models import FacebookCommentCache
from views import recache
import os

class FBCommentBasicTest(unittest.TestCase):
	def setUp(self):
		self.path = os.environ.get('SITE')
		self.c = Context({"path":self.path})
	
	def test_nothing(self):
		t_str = """{% load fb_comments %}"""
		t = Template(t_str)
		output = t.render(self.c)
	
	def test_render(self):
		t_str = """{% load fb_comments %}{% fb_comments href=path %}"""
		t = Template(t_str)
		output = t.render(self.c)

		#assert widget actually gets rendered 
		self.assertTrue("<div class=\"fb-comments\"" in output)

		#assert js is output in this case
		self.assertTrue("<script>" in output)
	
	def test_no_scripts(self):
		t_str = """{% load fb_comments %}{% fb_comments href=path no_scripts %}"""
		t = Template(t_str)
		output = t.render(self.c)

		#assert widget actually gets rendered 
		self.assertTrue("<div class=\"fb-comments\"" in output)

		#assert js is not output in this case
		self.assertFalse("<script>" in output)

class FBCommentCacheTest(unittest.TestCase):
	def setUp(self):
		self.path = os.environ.get('SITE')
		self.c = Context({"path":self.path})

	def test_cache_get(self):
		r = HttpRequest()
		r.method = 'POST'
		r.POST = {
			'href': self.path,
		}
		res = recache(r)
		self.assertTrue("success" in res.content)

		t_str = """{% load fb_comments %}{% fb_comments href=path include_cached_comments no_scripts %}"""
		t = Template(t_str)
		output = t.render(self.c)
		self.assertTrue("<div class=\"cached_comments\"" in output)

		self.assertTrue(len(FacebookCommentCache.get(self.path)) > 0)
