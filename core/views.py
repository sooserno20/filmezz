from django.views.generic import DetailView, ListView
from .models import Movie, Category
import unicodedata


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


class MovieList(ListView):
    model = Movie
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        category_options = list(Category.objects.all().values_list('name', flat=True))
        data['category_options'] = sorted([strip_accents(s) for s in category_options])
        return data

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
