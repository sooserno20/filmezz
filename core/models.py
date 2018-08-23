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
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='links')
    episode_nr = models.PositiveIntegerField(null=True, blank=True)
    link = models.URLField()

    class Meta:
        ordering = ['episode_nr']

    def __str__(self):
        return self.link


class Category(models.Model):
    movies = models.ManyToManyField(Movie, related_name='categories')
    name = models.CharField(max_length=15)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Actor(models.Model):
    movies = models.ManyToManyField(Movie, related_name='actors')
    name = models.CharField(max_length=70)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Director(models.Model):
    movies = models.ManyToManyField(Movie, related_name='directors')
    name = models.CharField(max_length=70)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
