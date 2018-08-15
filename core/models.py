from cloudinary.models import CloudinaryField
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.title


class MovieLink(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
    link = models.URLField(unique=True)

    def __str__(self):
        return self.link
