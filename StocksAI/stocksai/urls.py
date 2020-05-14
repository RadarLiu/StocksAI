from django.urls import path

from . import views

urlpatterns = [
  path('', views.index, name='index'),  # home page.
  path('edit_company/', views.edit_company, name='edit_company'),  # admin only.
  path('clear_all_stock_prices/', views.clear_all_stock_prices, name='clear_all_stock_prices')  # dev only
]