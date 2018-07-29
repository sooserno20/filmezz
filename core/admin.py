from django.contrib import admin
from .models import Movie, MovieLink


class MovieLinkInline(admin.StackedInline):
    model = MovieLink


class MovieAdmin(admin.ModelAdmin):
    inlines = (MovieLinkInline,)

admin.site.register(Movie, MovieAdmin)
