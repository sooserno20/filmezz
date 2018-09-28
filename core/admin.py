from django.contrib import admin
from .models import Movie, MovieLink, Actor, Category, Director


class MovieLinkInline(admin.StackedInline):
    model = MovieLink


class ActorInline(admin.StackedInline):
    model = Actor


class DirectorInline(admin.StackedInline):
    model = Director


class CategoryInline(admin.StackedInline):
    model = Category


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image_url', 'is_series', 'imdb_score',
                    'get_categories', 'get_actors', 'get_directors')
    search_fields = ('title', 'description', 'image_url', 'is_series', 'imdb_score')

    def get_actors(self, obj=None):
        obj = obj or self
        return [a for a in obj.actors.all()]

    def get_categories(self, obj):
        return [a for a in obj.categories.all()]

    def get_directors(self, obj):
        return [a for a in obj.directors.all()]

    get_actors.short_description = 'Actors'
    get_categories.short_description = 'Categories'
    get_directors.short_description = 'Directors'

    inlines = (MovieLinkInline,)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Category)
