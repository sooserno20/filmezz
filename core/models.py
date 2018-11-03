from cloudinary.models import CloudinaryField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Movie(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    # image = CloudinaryField('image', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    is_series = models.BooleanField(default=False)
    imdb_score = models.FloatField(default=0)
    year = models.CharField(null=True, blank=True, max_length=7)
    watch_nr = models.PositiveIntegerField(default=0, db_index=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=False)
    slug = models.SlugField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('movie-detail', kwargs={'pk': self.pk, 'slug': self.slug})


class MovieTranslation(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='translations')
    title = models.CharField(max_length=100, db_index=True)
    language = models.CharField(null=True, blank=True, max_length=20)

    def __str__(self):
        return '{}'.format(self.title)


class MovieLink(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='links')
    host = models.CharField(null=True, blank=True, max_length=20)
    # TODO: choices from language package, translate from googletrans
    language = models.CharField(null=True, blank=True, max_length=20)
    episode_nr = models.CharField(null=True, blank=True, max_length=15)
    link = models.URLField()
    verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['episode_nr']

    def __str__(self):
        return self.link


class Category(models.Model):
    movies = models.ManyToManyField(Movie, related_name='categories')
    name = models.CharField(max_length=15, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Actor(models.Model):
    movies = models.ManyToManyField(Movie, related_name='actors')
    name = models.CharField(max_length=70, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Director(models.Model):
    movies = models.ManyToManyField(Movie, related_name='directors')
    name = models.CharField(max_length=70, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
