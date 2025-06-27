from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'phone_number',
        'preferred_alert_type',
        'vehicle_type',
        'suscription',
    )
    list_filter = ('preferred_alert_type', 'vehicle_type', 'suscription')
    search_fields = ('user__username', 'full_name', 'phone_number')
