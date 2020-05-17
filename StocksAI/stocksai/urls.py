from django.urls import path
from django.conf.urls import include, url

from . import views

urlpatterns = [
  path('', views.index, name='index'),  # home page.
  path('edit_company/', views.edit_company, name='edit_company'),  # admin only.
  path('add_company/', views.edit_company, name='add_company'),  # admin only.
  path('delete_company/', views.edit_company, name='delete_company'),  # admin only.
  path('clear_all_stock_prices/', views.clear_all_stock_prices, name='clear_all_stock_prices')  # dev only
]
