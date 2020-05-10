from django.contrib import admin

from .models import StockCode
from .models import StockPrice
from .models import UpdateDate


admin.site.register(StockCode)
admin.site.register(StockPrice)
admin.site.register(UpdateDate)
