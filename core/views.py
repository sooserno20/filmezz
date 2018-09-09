from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models import Q
from .models import Movie, Category, MovieLink
import unicodedata
import requests


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def sort_accented_list(a_list):
    a_dict = {strip_accents(s): s for s in a_list}
    sorted_dict = sorted(a_dict.items(), key=lambda e: e[0])
    return [e[1] for e in sorted_dict]


class MovieList(ListView):
    model = Movie
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        category_options = list(Category.objects.all().values_list('name', flat=True))
        data['category_options'] = sort_accented_list(category_options)
        data['end_minus_five'] = data['paginator'].page_range.stop - 5
        data['last_page'] = data['paginator'].page_range.stop - 1
        # data['before_last_page'] = data['paginator'].page_range.stop - 2
        page_no = data['page_obj'].number
        begin = page_no - 2 if page_no > 3 else 2
        end = page_no + 3 if page_no < data['last_page'] - 2 else min(page_no + 2, data['last_page'])
        data['custom_page_range'] = range(begin, end)
        return data

    def get_queryset(self):
        search_by = self.request.GET.get('search_by', None)
        search = self.request.GET.get('search', None)
        category = self.request.GET.get('category', None)
        type = self.request.GET.get('type', None)

        query_filter = []
        if search:
            if search_by == 'title':
                query_filter.append(Q(title__icontains=search))
            elif search_by == 'actors':
                query_filter.append(Q(actors__name__icontains=search))
            elif search_by == 'directors':
                query_filter.append(Q(directors__name__icontains=search))

        if category and category != 'All':
            query_filter.append(Q(categories__name__icontains=category))

        if type and type != 'All':
            if type == 'Movie':
                query_filter.append(Q(is_series=False))
            elif type == 'Series':
                query_filter.append(Q(is_series=True))

        return self.model.objects.filter(*query_filter)
        

class MovieDetail(DetailView):
    model = Movie

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        category_options = list(Category.objects.all().values_list('name', flat=True))
        data['category_options'] = sort_accented_list(category_options)
        return data


def movie_link(request, movie_id, link_id):
    m_link = MovieLink.objects.filter(id=link_id).first()

    if m_link:
        # response = requests.get('http://sh.st/st/1b892a9f5fc5d5fb733633246ec2573d/{}'.format(m_link.link))
        # DECOMMENT FOR AD LINK
        # return HttpResponseRedirect(response.url)
        return HttpResponseRedirect(m_link.link)
    else:
        return HttpResponse()
