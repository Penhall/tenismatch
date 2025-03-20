# /tenismatch/apps/profiles/admin.py
from django.contrib import admin
from .models import UserProfile, ProfileHistory

class ProfileHistoryInline(admin.TabularInline):
    model = ProfileHistory
    extra = 0
    readonly_fields = ('timestamp', 'data')
    max_num = 10  # Limitar o número de históricos exibidos
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'profile_version', 'last_updated')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('profile_version', 'last_updated')
    inlines = [ProfileHistoryInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'user_type', 'bio', 'location')
        }),
        ('Preferências de Calçados', {
            'fields': ('shoe_size', 'preferred_brands', 'style_preferences')
        }),
        ('Informações Adicionais', {
            'fields': ('fashion_specialization', 'experience_years', 'compatibility_scores')
        }),
        ('Metadados', {
            'fields': ('profile_version', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProfileHistory)
class ProfileHistoryAdmin(admin.ModelAdmin):
    list_display = ('profile', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('profile__user__username',)
    readonly_fields = ('profile', 'data', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False