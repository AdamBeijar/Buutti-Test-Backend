from django.db import models

# Create your models here.

class Books(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=False, null=False)
    author = models.CharField(max_length=100, blank=False, null=False)
    year = models.IntegerField()
    publisher = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField()

    def __str__(self):
        return self.title
