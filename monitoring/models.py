from django.db import models

class DocumentUpload(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class InternshipList(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='internship_list/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
	# @property
	# def documentURL(self):
	# 	try:
	# 		url = self.document.url
	# 	except:
	# 		url = ''
	# 	return url
