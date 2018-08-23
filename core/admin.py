from django.contrib import admin
from .models import Movie, MovieLink, Actor, Category, Director


class MovieLinkInline(admin.StackedInline):
    model = MovieLink


class MovieAdmin(admin.ModelAdmin):
    inlines = (MovieLinkInline,)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Category)
