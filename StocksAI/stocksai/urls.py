from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('clear_all_stock_prices/', views.clear_all_stock_prices, name='clear_all_stock_prices')
]