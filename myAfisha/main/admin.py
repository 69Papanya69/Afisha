from django.contrib import admin
from .models import Theater, Hall

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')
    ordering = ('name',)

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('number_hall', 'theater')
    list_filter = ('theater',)
    search_fields = ('theater__name', 'number_hall')
