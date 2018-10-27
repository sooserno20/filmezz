from django.db import models

# strategy: which item is giving error skip storing


# title.basics and title.ratings
class Movie(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    # !!! don't store which doesn't fit the title
    # load title.episode and store only tvEpisode which is parent
    title_type = models.CharField(max_length=10, null=True, blank=False)
    title = models.CharField(max_length=50)
    is_adult = models.NullBooleanField(default=False, null=True, blank=False)
    year = models.PositiveSmallIntegerField(null=True, blank=False)
    duration = models.PositiveSmallIntegerField(null=True, blank=False)
    genres = models.CharField(max_length=30, null=True, blank=False)
    rating = models.FloatField(null=True, blank=True)


class TitleAlias(models.Model):
    title_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    region = models.CharField(max_length=3)
    original_title = models.NullBooleanField(default=False, null=True, blank=False)


class Name(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=30)
    movies = models.ManyToManyField(Movie, related_name='names', through='TitlePrincipals')


class TitlePrincipals(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    category = models.CharField(max_length=15)
