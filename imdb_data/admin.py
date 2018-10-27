from django.contrib import admin

# Register your models here.
from imdb_data.models import Movie, TitlePrincipals, TitleAlias, Name


admin.site.register(Movie)
admin.site.register(TitlePrincipals)
admin.site.register(TitleAlias)
admin.site.register(Name)
