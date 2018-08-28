from django.views.generic import DetailView, ListView
from .models import Movie


class MovieList(ListView):
    model = Movie
    paginate_by = 12

    def get_queryset(self):
        search_by = self.request.GET.get('search_by', 'title')
        search = self.request.GET.get('search', None)
        if not search:
            return self.model.objects.all()

        if search_by == 'title':
            return self.model.objects.filter(title__icontains=search)
        elif search_by == 'actors':
            return self.model.objects.filter(actors__name__icontains=search)
        elif search_by == 'directors':
            return self.model.objects.filter(directors__name__icontains=search)
        else:
            return self.model.objects.all()


class MovieDetail(DetailView):
    model = Movie