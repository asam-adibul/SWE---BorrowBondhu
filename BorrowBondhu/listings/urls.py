from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create/', views.listing_create, name='listing_create'),
    path('<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('my/', views.my_listings, name='my_listings'),
]