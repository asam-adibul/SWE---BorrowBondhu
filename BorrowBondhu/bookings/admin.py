from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['renter', 'listing', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['renter__username', 'listing__title']
    list_editable = ['status']