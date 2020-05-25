from django.urls import path
from django.conf.urls import include, url
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
  # "name" is used for reverse url match.
  path('', views.index, name='index'),  # home page.
  path('edit_company/', views.edit_company, name='edit_company'),  # admin only.
  path('add_company/', views.edit_company, name='add_company'),  # admin only.
  path('delete_company/', views.edit_company, name='delete_company'),  # admin only.
  path('register/', views.register, name='register'),
  path('login/', LoginView.as_view(template_name='stocksai/login.html'), name='login'),
  path('logout/', LogoutView.as_view(template_name='stocksai/logout.html'), name='logout'),
  #path('clear_all_stock_prices/', views.clear_all_stock_prices, name='clear_all_stock_prices'),  # dev only
  #url(r'^.*', views.handler, name='handler'),
]
