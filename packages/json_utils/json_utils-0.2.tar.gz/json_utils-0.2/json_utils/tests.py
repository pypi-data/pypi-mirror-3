#coding=utf-8
from json_utils.utils import to_json
from django.test import TestCase
from django.db import models

class DummyModel(models.Model):
	title = models.CharField(max_length=128)
	number = models.PositiveIntegerField()
	description = models.TextField()

	def __unicode__(self):
		return self.title

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location='/tmp')

class DummyImageModel(models.Model):
	title = models.CharField(max_length=128)
	image = models.ImageField(max_length=255, upload_to = '/tmp', storage=fs,  height_field = 'image_height', width_field = 'image_width')
	image_height = models.PositiveSmallIntegerField(null=True)
	image_width = models.PositiveSmallIntegerField(null=True)

	def __unicode__(self):
		return self.title


class JSONEncodingTest(TestCase):
	def test_basic_model_encoding(self):
		dummy = DummyModel.objects.create(
			title="dummy title",
			number = 42,
			description="Some Dummy Description"
		)
		expected_json = '\{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 42, "title": "dummy title"\}\}'
		self.assertRegexpMatches(
			to_json(dummy),
			expected_json
		)
	
	def test_basic_model_encoding_unicode(self):
		dummy = DummyModel.objects.create(
			title=u"Déjà Vu",
			number = 42,
			description=u"Æ û â Ð Ý ï þ ł ś ć ·"
		)
		expected_json = u'\{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Æ û â Ð Ý ï þ ł ś ć ·", "number": 42, "title": "Déjà Vu"\}\}'
		self.assertRegexpMatches(
			to_json(dummy),
			expected_json
		)

	def test_model_with_image(self):
		import Image
		size = (200,200)
		color = (255,0,0,0)
		img = Image.new("RGBA",size,color)
		
		import StringIO
		f =  StringIO.StringIO()
		img.save(f, 'png')
		f.name = "test.png"
		f.seek(0)

		dummy = DummyImageModel.objects.create(
			title = "dummy2"
		)

		from django.core.files.base import ContentFile
		dummy.image.save('dummy_file_name.png', ContentFile(f.read()))

		expected_json = '\{"pk": \d+, "model": "json_utils.dummyimagemodel", "fields": \{"image": "/tmp/dummy_file_name_?\d*\.png", "image_height": 200, "image_width": 200, "title": "dummy2"\}\}'
		self.assertRegexpMatches(
			to_json(dummy),
			expected_json
		)

		dummy.image.delete();
		
	def test_queryset(self):
		for i in range(3):
			DummyModel.objects.create(
				title="dummy%i" % i,
				number = i,
				description="Some Dummy Description"
			)
		
		expected_json = '\[\{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 0, "title": "dummy0"\}\}, {"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 1, "title": "dummy1"\}\}, \{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 2, "title": "dummy2"\}\}\]'
		self.assertRegexpMatches(
			to_json(DummyModel.objects.all()),
			expected_json
		)
	
	def test_mixed(self):
		for i in range(3):
			DummyModel.objects.create(
				title="dummy%i" % i,
				number = i,
				description="Some Dummy Description"
			)
		result = DummyModel.objects.all()
		data = {'result':1, 'count':DummyModel.objects.count(), 'payload':result}
		expected_json = '\{"count": \d+, "result": 1, "payload": \[\{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 0, "title": "dummy0"\}''}, \{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 1, "title": "dummy1"\}\}, \{"pk": \d+, "model": "json_utils.dummymodel", "fields": \{"description": "Some Dummy Description", "number": 2, "title": "dummy2"\}\}\]\}'
		self.assertRegexpMatches(
			to_json(data),
			expected_json
		)