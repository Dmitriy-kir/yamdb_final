import os
import sys

from django_filters import rest_framework as filters
from reviews.models import Title

sys.path.append(os.path.abspath('..'))


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = filters.NumberFilter(
        field_name='year'
    )
    category = filters.CharFilter(
        field_name='category__slug'
    )
    genre = filters.CharFilter(
        field_name='genre__slug'
    )

    class Meta:
        model = Title
        fields = '__all__'
