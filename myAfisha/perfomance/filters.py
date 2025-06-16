import django_filters
from django.db.models import Min, Max
from .models import Performance, PerformanceCategory, PerformanceSchedule

class PerformanceFilter(django_filters.FilterSet):
    """
    Фильтр для спектаклей с различными опциями фильтрации
    """
    # Фильтр по названию (поиск по частичному совпадению, без учета регистра)
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Фильтр по категории (точное совпадение по ID)
    category = django_filters.ModelChoiceFilter(
        queryset=PerformanceCategory.objects.all()
    )
    
    # Фильтр по названию категории (частичное совпадение)
    category_name = django_filters.CharFilter(
        field_name='category__name', 
        lookup_expr='icontains'
    )
    
    # Фильтр по минимальной и максимальной цене билета
    min_price = django_filters.NumberFilter(
        field_name='schedule__price', 
        lookup_expr='gte',
        method='filter_by_price'
    )
    max_price = django_filters.NumberFilter(
        field_name='schedule__price', 
        lookup_expr='lte',
        method='filter_by_price'
    )
    
    # Фильтр по дате (спектакли, которые проходят после указанной даты)
    date_after = django_filters.DateFilter(
        field_name='schedule__date_time', 
        lookup_expr='gte'
    )
    
    # Фильтр по дате (спектакли, которые проходят до указанной даты)
    date_before = django_filters.DateFilter(
        field_name='schedule__date_time', 
        lookup_expr='lte'
    )
    
    # Фильтр по наличию мест (спектакли с количеством мест больше указанного)
    min_seats = django_filters.NumberFilter(
        field_name='schedule__available_seats', 
        lookup_expr='gte'
    )
    
    # Фильтр по продолжительности (в минутах)
    min_duration = django_filters.NumberFilter(method='filter_by_duration_min')
    max_duration = django_filters.NumberFilter(method='filter_by_duration_max')
    
    # Фильтр по театру
    theater = django_filters.CharFilter(
        field_name='schedule__theater__name', 
        lookup_expr='icontains'
    )
    
    def filter_by_price(self, queryset, name, value):
        """
        Метод для фильтрации по цене с учетом связанных расписаний
        """
        # Получаем ID спектаклей, у которых есть расписания с подходящей ценой
        if name == 'schedule__price__gte':
            performance_ids = PerformanceSchedule.objects.filter(
                price__gte=value
            ).values_list('performance_id', flat=True).distinct()
        else:
            performance_ids = PerformanceSchedule.objects.filter(
                price__lte=value
            ).values_list('performance_id', flat=True).distinct()
            
        return queryset.filter(id__in=performance_ids)
    
    def filter_by_duration_min(self, queryset, name, value):
        """
        Фильтр по минимальной продолжительности в минутах
        """
        # Преобразуем минуты в секунды (Django хранит duration в секундах)
        seconds = value * 60
        return queryset.filter(duration_time__gte=seconds)
    
    def filter_by_duration_max(self, queryset, name, value):
        """
        Фильтр по максимальной продолжительности в минутах
        """
        # Преобразуем минуты в секунды (Django хранит duration в секундах)
        seconds = value * 60
        return queryset.filter(duration_time__lte=seconds)
    
    class Meta:
        model = Performance
        fields = [
            'name', 'category', 'category_name', 
            'min_price', 'max_price', 
            'date_after', 'date_before',
            'min_seats', 'min_duration', 'max_duration',
            'theater'
        ] 