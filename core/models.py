from cloudinary.models import CloudinaryField
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    # image = CloudinaryField('image', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    is_series = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class MovieLink(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    episode_nr = models.PositiveIntegerField(null=True, blank=True)
    link = models.URLField()

    class Meta:
        ordering = ['episode_nr']

    def __str__(self):
        return self.link
