"""filmezz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
import core.views

urlpatterns = [
    url(r'^$', core.views.MovieList.as_view(), name='movie-list'),
    url(r'^movie/(?P<movie_id>\d+)/(?P<link_id>\d+)$', core.views.movie_link, name='movie-link'),
    url(r'^movie/(?P<pk>\d+)/(?P<slug>[-\w\d]+)$', core.views.MovieDetail.as_view(), name='movie-detail'),
    # url(r'^movie/(?P<pk>\d+)$', core.views.MovieDetail.as_view(), name='movie-detail'),
    url(r'^random_movie/', core.views.suggest_random_movie, name='random-movie'),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
