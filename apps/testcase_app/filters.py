import django_filters
from django_filters import FilterSet, Filter
from apps.testcase_app.models import NatcoStatus


class NatcoStatusFilter(django_filters.FilterSet):

    natco = django_filters.CharFilter(field_name='natco__natco')
    language = django_filters.CharFilter(field_name='language__language_name', lookup_expr='iexact')
    device = django_filters.CharFilter(field_name='device__name', lookup_expr='iexact')

    class Meta:
        model = NatcoStatus
        fields = ['natco', 'language', 'device']