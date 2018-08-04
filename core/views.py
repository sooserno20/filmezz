from django.db.models import Q
from django.views.generic import ListView
from .models import Movie


class MovieList(ListView):
    model = Movie
    paginate_by = 12
    template_name = 'core/list.html'

    def get_queryset(self):
        try:
            search = self.request.GET['search']
        except KeyError:
            object_list = self.model.objects.all()
        else:
            object_list = self.model.objects.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return object_list
