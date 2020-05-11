from django.contrib import admin

from .models import StockCode
from .models import StockPrice


admin.site.register(StockCode)
admin.site.register(StockPrice)
