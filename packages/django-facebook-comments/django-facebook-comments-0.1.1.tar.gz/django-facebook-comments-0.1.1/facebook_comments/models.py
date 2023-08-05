from django.db import models
import json

class FacebookCommentCache(models.Model):
	url = models.CharField(max_length=255, unique=True)
	content = models.TextField()

	@classmethod
	def upsert(cls, href, data):
		obj, _ = cls.objects.get_or_create(url=href)
		obj.content = data
		obj.save()

	@classmethod
	def get(cls, href):
		try:
			obj = cls.objects.get(url=href)
		except cls.DoesNotExist:
			return []
		try:
			comments = json.loads(obj.content)
			data = comments[href]['data']
		except ValueError, AttributeError, KeyError:
			return []
		return data
