from django.contrib import admin
from .models import Artist

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'current_subs', 'growth_percentage', 'viral_status', 'is_blocked')
    list_filter = ('genre', 'location', 'is_blocked')
    search_fields = ('name',)
    list_editable = ('is_blocked',)
    actions = ['mark_as_blocked', 'mark_as_active']

    @admin.action(description="Block selected channels")
    def mark_as_blocked(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description="Unblock selected channels")
    def mark_as_active(self, request, queryset):
        queryset.update(is_blocked=False)
